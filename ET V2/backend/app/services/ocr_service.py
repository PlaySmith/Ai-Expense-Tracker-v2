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
        Fixed OCR Pipeline - Accuracy First (no resize/crop, grayscale + blur)
        """
        try:
            self.logger.info(f"Processing {image_path}")
            
            img = cv2.imread(image_path)
            if img is None:
                raise OCRError("Cannot read image")
            
            # Preprocess for accuracy: grayscale + light blur (no threshold/resize/crop)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            img = cv2.GaussianBlur(gray, (3, 3), 0)
            
            # Full image OCR - detail=1, no paragraph for better detection
            results = self.reader.readtext(img, detail=1)
            
            # Extract texts (filter conf >0.4 optional, but keep all for now)
            texts = [r[1].strip() for r in results if len(r) > 1]
            confs = [r[2] for r in results if len(r) > 2]
            overall_conf = np.mean(confs) if confs else 0.4
            
            # Heuristic split for compatibility
            merchant_text = texts[0][:50] if texts else ''
            amount_text = ' '.join(texts[-5:]) if len(texts) >= 5 else ' '.join(texts)
            items_text = ' '.join(texts[1:-5]) if len(texts) > 6 else ' '.join(texts[1:])
            full_text = ' '.join(texts)
            
            # Compat confs (weighted average simplified)
            conf_merchant = overall_conf
            conf_amount = overall_conf
            conf_items = overall_conf
            
            result = {
                'merchant_text': merchant_text,
                'items_text': items_text,
                'amount_text': amount_text,
                'full_text': full_text,
                'conf_merchant': conf_merchant,
                'conf_amount': conf_amount,
                'conf_items': conf_items,
                'conf_overall': overall_conf
            }
            
            self.logger.info(f"OCR done: conf={overall_conf:.2f}, merchant='{merchant_text[:30]}', amounts='{amount_text[:50]}'")
            return result
            
        except Exception as e:
            self.logger.error(f"OCR failed: {e}")
            raise OCRError(f"OCR processing failed: {str(e)}")

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

