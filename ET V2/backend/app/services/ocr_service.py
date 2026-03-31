import easyocr
import cv2
import numpy as np
from PIL import Image
from pathlib import Path
from typing import Dict, Any, Tuple
import io
from ..utils.logger import LoggerMixin
from ..utils.error_handlers import OCRError

# Global singleton reader (init once!)
_reader = None


class OCRService(LoggerMixin):
    def __init__(self):
        super().__init__()
        global _reader
        if _reader is None:
            _reader = easyocr.Reader(['en'], gpu=False)
            self.logger.info("EasyOCR initialized (singleton)")
        self.reader = _reader


    def process_image(self, image_path: str) -> Dict[str, Any]:
        """
        V2 OCR Pipeline - FAST optimized (resize + crop + singleton)
        """
        try:
            self.logger.info(f"Processing {image_path}")
            
            # FAST: cv2 resize + crop (80% area)
            img = cv2.imread(image_path)
            h, w = img.shape[:2]
            
            # Resize 0.5x + crop receipt zone
            scale = 0.5
            new_w, new_h = int(w * scale), int(h * scale)
            img = cv2.resize(img, (new_w, new_h))
            
            crop_top, crop_bottom = int(new_h*0.1), int(new_h*0.9)
            crop_left, crop_right = int(new_w*0.05), int(new_w*0.95)
            img_crop = img[crop_top:crop_bottom, crop_left:crop_right]
            
            # Regions on cropped/resized
            height_crop, width_crop = img_crop.shape[:2]
            top_region = img_crop[0:int(height_crop*0.35), :]
            mid_region = img_crop[int(height_crop*0.25):int(height_crop*0.75), :]
            bottom_region = img_crop[int(height_crop*0.7):, :]
            
            # FAST OCR w/ optimized params
            top_text = self._ocr_region_fast(top_region, 'merchant')
            mid_text = self._ocr_region_fast(mid_region, 'items') 
            bottom_text = self._ocr_region_fast(bottom_region, 'amount')
            
            # Conf >0.5 only, handle nan
            def safe_mean(dets):
                confs = [d[2] for d in dets if d[2] > 0.5]
                return np.mean(confs) if confs else 0.4
                
            conf_merchant = safe_mean(top_text)
            conf_amount = safe_mean(bottom_text)
            conf_items = safe_mean(mid_text)
            overall_conf = np.clip((conf_merchant*0.3 + conf_amount*0.4 + conf_items*0.3), 0.0, 1.0)
            
            result = {
                'merchant_text': ' '.join([t[1].strip() for t in top_text if t[2] > 0.5]),
                'items_text': ' '.join([t[1].strip() for t in mid_text if t[2] > 0.5]),
                'amount_text': ' '.join([t[1].strip() for t in bottom_text if t[2] > 0.5]),
                'full_text': ' '.join([t[1].strip() for t in top_text + mid_text + bottom_text if t[2] > 0.5]),
                'conf_merchant': conf_merchant,
                'conf_amount': conf_amount, 
                'conf_items': conf_items,
                'conf_overall': overall_conf
            }
            
            self.logger.info(f"OCR done: conf={overall_conf:.2f}, merchant='{result['merchant_text'][:30]}', amounts='{result['amount_text'][:50]}' (FAST)")
            return result
            
        except Exception as e:
            self.logger.error(f"OCR failed: {e}")
            raise OCRError(f"OCR processing failed: {str(e)}")

    def _ocr_region_fast(self, cv_img: np.ndarray, region_type: str) -> list:
        """
        FAST: Direct cv2 np.array → EasyOCR (no PIL/BytesIO)
        """
        if cv_img.size == 0:
            self.logger.warning(f"{region_type}: empty crop")
            return []
        # BGR→RGB 
        rgb_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        try:
            results = self.reader.readtext(rgb_img, detail=1, low_text=0.4, paragraph=True)
        except Exception as e:
            self.logger.warning(f"{region_type} OCR failed: {e}")
            return []
        filtered = [r for r in results if len(r) >= 3 and r[2] > 0.5]
        self.logger.debug(f"{region_type}: {len(filtered)}/{len(results)} detections (conf>0.5)")
        return filtered

    def validate_image(self, image_path: str) -> bool:
        path = Path(image_path)
        if not path.exists():
            raise OCRError("Image file not found")
        try:
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError("Cannot read image")
            return True
        except:
            raise OCRError("Invalid image")
