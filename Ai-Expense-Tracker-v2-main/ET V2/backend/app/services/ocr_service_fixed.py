import easyocr
from PIL import Image
from pathlib import Path
from typing import Dict, Any, Tuple
import io
import numpy as np
from ..utils.logger import LoggerMixin
from ..utils.error_handlers import OCRError


class OCRService(LoggerMixin):
    def __init__(self):
        super().__init__()
        self.reader = easyocr.Reader(['en'], gpu=False)  # Torch warning normal/ignored
        self.logger.info("EasyOCR initialized")


    def process_image(self, image_path: str) -> Dict[str, Any]:
        """
        V2 OCR Pipeline - minimal, region-based EasyOCR
        """
        try:
            self.logger.info(f"Processing {image_path}")
            img = Image.open(image_path)
            
            # Image dims
            width, height = img.size
            
            # STRICT regions for Indian receipts
            top_region = img.crop((0, 0, width, int(height * 0.3)))      # Merchant
            mid_region = img.crop((0, int(height * 0.25), width, int(height * 0.75)))  # Items/Date
            bottom_region = img.crop((0, int(height * 0.7), width, height))  # Grand Total
            
            # EasyOCR (no preprocess needed)
            top_text = self._ocr_region(top_region, 'merchant')
            mid_text = self._ocr_region(mid_region, 'items')
            bottom_text = self._ocr_region(bottom_region, 'amount')
            
            # Confidence: avg of detections > 60
            conf_merchant = np.mean([d[2] for d in top_text if d[2] > 0.6]) if top_text else 0.0
            conf_amount = np.mean([d[2] for d in bottom_text if d[2] > 0.6]) if bottom_text else 0.0
            conf_items = np.mean([d[2] for d in mid_text if d[2] > 0.6]) if mid_text else 0.0
            overall_conf = (conf_merchant * 0.3 + conf_amount * 0.4 + conf_items * 0.3)
            
            result = {
                'merchant_text': ' '.join([t[1].strip() for t in top_text if t[2] > 0.6]),
                'items_text': ' '.join([t[1].strip() for t in mid_text if t[2] > 0.6]),
                'amount_text': ' '.join([t[1].strip() for t in bottom_text if t[2] > 0.6]),
                'full_text': ' '.join([t[1].strip() for t in top_text + mid_text + bottom_text if t[2] > 0.6]),
                'conf_merchant': conf_merchant,
                'conf_amount': conf_amount,
                'conf_items': conf_items,
                'conf_overall': overall_conf
            }
            
            self.logger.info(f"OCR done: conf={overall_conf:.2f}, merchant='{result['merchant_text'][:30]}', amounts='{result['amount_text'][:50]}'")
            return result
            
        except Exception as e:
            self.logger.error(f"OCR failed: {e}")
            raise OCRError(f"OCR processing failed: {str(e)}")

    def _ocr_region(self, pil_img: Image.Image, region_type: str) -> list:
        \"\"\"
        Run EasyOCR on PIL crop.
        \"\"\"
        img_bytes = io.BytesIO()
        pil_img.convert('RGB').save(img_bytes, format='JPEG')
        img_bytes = img_bytes.getvalue()
        
        results = self.reader.readtext(img_bytes)
        self.logger.debug(f"{region_type}: {len(results)} detections")
        return results

    def validate_image(self, image_path: str) -> bool:
        path = Path(image_path)
        if not path.exists():
            raise OCRError("Image file not found")
        try:
            img = Image.open(image_path)
            img.verify()
            return True
        except:
            raise OCRError("Invalid image")
