import easyocr
from PIL import Image, ImageEnhance, ImageOps
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import io
from ..utils.logger import LoggerMixin
# from ..utils.error_handlers import OCRError

class OCRService(LoggerMixin):
    def __init__(self):
        super().__init__()
        self._reader = None

    def _get_reader(self):
        """Strict singleton initialization for the OCR reader."""
        if self._reader is None:
            # CPU mode initialization
            self._reader = easyocr.Reader(['en'], gpu=False)
            self.logger.info("EasyOCR Reader initialized (strict singleton)")
        return self._reader

    def process_image(self, image_path: str) -> Dict[str, Any]:
        """
        V2.1 OCR - Binary preprocess + strict conf for accuracy
        """
        try:
            self.logger.info(f"Processing {image_path}")
            
            # Ensure reader is ready
            self._get_reader()
            
            # PREPROCESS: Grayscale → Autocontrast → Binarize → Enhance
            # This kills shadows and background noise from WhatsApp/Phone photos
            img_raw = Image.open(image_path).convert('L')  # Grayscale
            img_auto = ImageOps.autocontrast(img_raw)      # Histogram stretch
            
            # Strict binary threshold: 140 is the 'sweet spot' for thermal receipts
            img_bin = img_auto.point(lambda x: 0 if x < 140 else 255, '1') 
            
            # Convert to RGB for EasyOCR and Sharpen
            img = ImageEnhance.Sharpness(img_bin.convert('RGB')).enhance(2.0)
            
            width, height = img.size
            self.logger.debug(f"Preprocessed image size: {width}x{height}")
            
            # Tight crop zones (Slightly more aggressive to avoid fingers/edges)
            crop_left, crop_right = int(width * 0.05), int(width * 0.95)
            crop_top, crop_bottom = int(height * 0.08), int(height * 0.92)
            img_crop = img.crop((crop_left, crop_top, crop_right, crop_bottom))
            
            cw, ch = img_crop.size
            regions = {
                'merchant': img_crop.crop((0, 0, cw, int(ch * 0.3))),
                'items': img_crop.crop((0, int(ch * 0.25), cw, int(ch * 0.75))),
                'amount': img_crop.crop((0, int(ch * 0.65), cw, ch))
            }
            
            # OCR regions with high low_text threshold to ignore noise
            top_text = self._ocr_region(regions['merchant'], 'merchant')
            mid_text = self._ocr_region(regions['items'], 'items')
            bottom_text = self._ocr_region(regions['amount'], 'amount')
            
            # Strict confidence calculation
            def safe_mean(dets):
                confs = [float(d[2]) for d in dets if float(d[2]) > 0.5]
                return sum(confs)/len(confs) if confs else 0.0
            
            conf_merchant = safe_mean(top_text)
            conf_amount = safe_mean(bottom_text)
            conf_items = safe_mean(mid_text)
            
            # Weighted overall confidence (Amount is most important)
            overall_conf = min(1.0, (conf_merchant*0.25 + conf_amount*0.5 + conf_items*0.25))
            
            # Full fallback if regional results are questionable
            full_text_all = []
            if overall_conf < 0.45:
                self.logger.info("Low regional confidence - running full fallback scan")
                full_text_all = self._ocr_region(img_crop, 'full_fallback')
            
            result = {
                'merchant_text': ' '.join([t[1].strip() for t in top_text if self._is_valid_detection(t)]),
                'items_text': ' '.join([t[1].strip() for t in mid_text if self._is_valid_detection(t)]),
                'amount_text': ' '.join([t[1].strip() for t in bottom_text if self._is_valid_detection(t)]),
                'full_text': ' '.join([t[1].strip() for t in top_text + mid_text + bottom_text + full_text_all if self._is_valid_detection(t)]),
                'conf_merchant': conf_merchant,
                'conf_amount': conf_amount,
                'conf_items': conf_items,
                'conf_overall': overall_conf
            }
            
            self.logger.info(f"OCR result: conf={overall_conf:.1%} merchant='{result['merchant_text'][:20]}...' amount='{result['amount_text'][-15:]}'")
            return result
            
        except Exception as e:
            self.logger.error(f"OCR Pipeline failed: {e}")
            raise ValueError(f"OCR failed: {str(e)}")

    def _ocr_region(self, pil_img: Image.Image, region_type: str) -> List[Tuple]:
        """Runs EasyOCR on a specific region using PNG buffer."""
        if pil_img.size[0] == 0 or pil_img.size[1] == 0:
            return []
        
        img_bytes = io.BytesIO()
        pil_img.save(img_bytes, format='PNG')
        img_data = img_bytes.getvalue()
        
        try:
            # paragraph=False allows for more granular amount/date detection
            results = self._get_reader().readtext(img_data, detail=1, low_text=0.5, paragraph=False)
            
            # Unpack to prevent Pylance Literal index error
            filtered = []
            for r in results:
                try:
                    _, text, conf = r
                    if float(conf) > 0.5:
                        filtered.append(r)
                except (ValueError, IndexError, TypeError):
                    continue
            
            self.logger.debug(f"{region_type}: found {len(filtered)} valid detections")
            return filtered
        except Exception as e:
            self.logger.warning(f"{region_type} scan failed: {e}")
            return []

    def _is_valid_detection(self, t: Tuple) -> bool:
        """Helper for filtering valid tuples."""
        try:
            _, _, conf = t
            return float(conf) > 0.5
        except:
            return False

    def validate_image(self, image_path: str) -> bool:
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {image_path}")
        try:
            with Image.open(image_path) as img:
                img.verify()
            return True
        except Exception as e:
            self.logger.error(f"Invalid image format: {e}"); raise ValueError(f"Invalid image format: {e}")
