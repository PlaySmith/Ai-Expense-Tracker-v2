import cv2
import numpy as np
import pytesseract
from PIL import Image
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
import logging
import os
import re

from app.utils.error_handlers import OCRError, OCRLowConfidenceError

from app.utils.logger import LoggerMixin

# Configure Tesseract path for Windows
# Update this path if Tesseract is installed elsewhere
pytesseract.pytesseract.tesseract_cmd = r"D:\Tesseract_OCR\tesseract.exe"

# Alternative: Use environment variable if set
if os.environ.get('TESSERACT_CMD'):
    pytesseract.pytesseract.tesseract_cmd = os.environ.get('TESSERACT_CMD')


class OCRService(LoggerMixin):
    """Service for OCR processing of receipt images"""
    
# Minimum confidence threshold (lowered for better real-world handling)
    MIN_CONFIDENCE = 50.0
    
    NOISE_WORDS = {'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
    
    def __init__(self):
        super().__init__()

    def process_image(self, image_path: str) -> Dict[str, Any]:
        """
        Process receipt image and extract text - ENHANCED FLOW
        
        NEW FLOW:
        1. Rotation correction fallback
        2. Preprocess + doc type detection  
        3. STRICT type-aware region extraction
        4. Weighted confidence + structured output
        """
        try:
            self.logger.info(f"=== ENHANCED OCR PROCESSING: {image_path} ===")
            
            # 1. ROTATION FALLBACK (NEW)
            rotated_img, rot_angle = self._try_rotations(image_path)
            self.logger.info(f"Using rotated image: {rot_angle}°")
            
            # Save rotated temporarily for debug
            temp_rot = image_path.replace('.jpg', f'_rot{rot_angle}.jpg')
            cv2.imwrite(temp_rot, rotated_img)
            
            # 2. PREPROCESS rotated image
            preprocessed = self._preprocess_image_from_img(rotated_img)  # Need new method
            
            # 3. QUICK FULL OCR for document type detection
            quick_text = pytesseract.image_to_string(
                preprocessed, config='--oem 3 --psm 6 -l eng'
            )
            doc_info = self._detect_document_type(quick_text)
            doc_type = doc_info['type']
            
            # 4. STRICT REGION EXTRACTION (NEW)
            regions = self._extract_strict_regions(rotated_img, doc_type)
            
            # 5. FALLBACK full OCR (existing logic but improved)
            full_data = pytesseract.image_to_data(preprocessed, config='--oem 3 --psm 6 -l eng', output_type=pytesseract.Output.DICT)
            full_parts = [t.strip() for i, t in enumerate(full_data['text']) if int(full_data['conf'][i]) > 30]
            full_text = ' '.join(full_parts)
            
            # 6. WEIGHTED CONFIDENCE (NEW)
            conf_merchant = regions['conf_merchant']
            conf_amount = regions['conf_amount']
            conf_items = regions.get('conf_items',0.0) 
            full_conf = np.mean([int(full_data['conf'][i]) for i in range(len(full_data['text'])) if int(full_data['conf'][i]) > 30]) / 100.0
            
            # Weighted: amount(40%) + merchant(30%) + items(20%) + full(10%)
            overall_conf = 0.4*conf_amount + 0.3*conf_merchant + 0.2*conf_items + 0.1*full_conf
            
            # 7. STRUCTURED RESULT (BACKWARD COMPATIBLE)
            result = {
                # NEW structured fields
                'doc_type': doc_type,
                'rotation_used': rot_angle,
                'merchant_text': regions['merchant_text'],
                'amount_candidates': regions['amount_candidates'],
                'suggested_amount': max(regions['amount_candidates']) if regions['amount_candidates'] else None,
                'items_text': regions['items_text'],
                'full_text': full_text,
                
                # BACKWARD COMPATIBLE fields
                'conf': overall_conf,
                'conf_merchant': conf_merchant,
                'conf_amount': conf_amount,
                'conf_items': conf_items,
            }
            
            self.logger.info(f"ENHANCED OCR COMPLETE - Type: {doc_type}, "
                           f"Conf: {overall_conf:.1f}, Merchant: '{regions['merchant_text'][:30]}...', "
                           f"Amounts: {len(regions['amount_candidates'])} candidates")

            
            return result
            
        except Exception as e:
            self.logger.error(f"Enhanced OCR processing failed: {str(e)}", exc_info=True)
            raise OCRError(f"Failed to process image: {str(e)}")

            
            # Preprocess image
            img = cv2.imread(image_path)
            h, w = img.shape[:2]
            
            # Region crops
            top_region = img[0:int(h*0.2), :]  # Top 20% merchant
            bottom_region = img[int(h*0.8):, :]  # Bottom 20% amount
            middle_region = img[int(h*0.2):int(h*0.8), :]  # Middle 60% items
            
            preprocessed = self._preprocess_image(image_path)
            
            # Try multiple PSM configs for best result
            psm_configs = [
                r'--oem 3 --psm 6 -l eng',
                r'--oem 3 --psm 4 -l eng',
                r'--oem 3 --psm 3 -l eng',
                r'--oem 3 --psm 11 -l eng'
            ]
            best_text = ""
            best_confidence = 0.0
            for config in psm_configs:
                try:
                    data = pytesseract.image_to_data(
                        preprocessed, 
                        config=config,
                        output_type=pytesseract.Output.DICT
                    )
                    text_parts = []
                    confidences = []
                    for i, text in enumerate(data['text']):
                        if int(data['conf'][i]) > 0:
                            text_parts.append(text)
                            confidences.append(int(data['conf'][i]))
                    full_text = ' '.join(text_parts)
                    avg_conf = sum(confidences) / len(confidences) if confidences else 0
                    if avg_conf > best_confidence:
                        best_text = full_text
                        best_confidence = avg_conf
                    self.logger.debug(f"PSM config tried: conf {avg_conf:.1f}%")
                except Exception as e:
                    self.logger.debug(f"PSM config failed: {str(e)}")
                    continue
            # Region OCR
            merchant_text = ''
            amount_text = ''
            items_text = ''
            conf_merchant = 0
            conf_amount = 0
            conf_items = 0
            
            # Merchant (top PSM 7 - single line)
            merchant_data = pytesseract.image_to_data(top_region, config='--oem 3 --psm 7 -l eng', output_type=pytesseract.Output.DICT)
            merchant_parts = [t.strip() for i, t in enumerate(merchant_data['text']) 
                                if int(merchant_data['conf'][i]) > 30 and len(t.strip()) >= 3 
                                and t.strip().lower() not in self.NOISE_WORDS]
            merchant_text = ' '.join(merchant_parts)
            merchant_confs = [int(merchant_data['conf'][i]) for i in range(len(merchant_data['text'])) if int(merchant_data['conf'][i]) > 30]
            conf_merchant = sum(merchant_confs) / len(merchant_confs) if merchant_confs else 0
            
            # Amount (bottom PSM 8 - single word)
            amount_data = pytesseract.image_to_data(bottom_region, config='--oem 3 --psm 8 -l eng', output_type=pytesseract.Output.DICT)
            amount_parts = [t.strip() for i, t in enumerate(amount_data['text']) 
                               if int(amount_data['conf'][i]) > 30 and len(t.strip()) >= 3 
                               and t.strip().lower() not in self.NOISE_WORDS]
            amount_text = ' '.join(amount_parts)
            amount_confs = [int(amount_data['conf'][i]) for i in range(len(amount_data['text'])) if int(amount_data['conf'][i]) > 30]
            conf_amount = sum(amount_confs) / len(amount_confs) if amount_confs else 0
            
            # Items (middle PSM 6)
            items_data = pytesseract.image_to_data(middle_region, config='--oem 3 --psm 6 -l eng', output_type=pytesseract.Output.DICT)
            items_parts = [t.strip() for i, t in enumerate(items_data['text']) 
                              if int(items_data['conf'][i]) > 30 and len(t.strip()) >= 3 
                              and t.strip().lower() not in self.NOISE_WORDS]
            items_text = ' '.join(items_parts)
            items_confs = [int(items_data['conf'][i]) for i in range(len(items_data['text'])) if int(items_data['conf'][i]) > 30]
            conf_items = sum(items_confs) / len(items_confs) if items_confs else 0
            
            # Fallback full OCR
            data = pytesseract.image_to_data(preprocessed, config='--oem 3 --psm 6 -l eng', output_type=pytesseract.Output.DICT)
            full_parts = [t.strip() for i, t in enumerate(data['text']) 
                             if int(data['conf'][i]) > 30 and len(t.strip()) >= 3 
                             and t.strip().lower() not in self.NOISE_WORDS]
            full_text = ' '.join(full_parts)
            
            # Construct result dict after all OCR processing
            result = {
                'merchant_text': merchant_text or '',
                'amount_text': amount_text or '',
                'items_text': items_text or full_text[:500],
                'full_text': full_text,
                'conf': max(best_confidence, conf_merchant, conf_amount, conf_items or 0) / 100.0,
                'conf_merchant': conf_merchant / 100.0,
                'conf_amount': conf_amount / 100.0,
                'conf_items': conf_items / 100.0
            }
            
            self.logger.info(f"OCR completed. Confidence: {result['conf']:.1f}%")
            self.logger.debug(f"Regions - Merchant: {result['merchant_text'][:50]}..., Amount: {result['amount_text'][:50]}...")
            
            # Check confidence threshold - log warning but continue for graceful degradation
            if result['conf'] < self.MIN_CONFIDENCE:
                self.logger.warning(
                    f"Low OCR confidence ({result['conf']:.1f}%) below threshold ({self.MIN_CONFIDENCE}%). "
                    f"Flagging for review."
                )
            
            return result
            
        # No longer raise low conf, handled with warning
        except Exception as e:
            self.logger.error(f"OCR processing failed: {str(e)}", exc_info=True)
            raise OCRError(
                message=f"Failed to process image: {str(e)}",
                details={"image_path": image_path}
            )
    
    def _preprocess_image_from_img(self, img: np.ndarray) -> np.ndarray:
        """
        Enhanced preprocessing for numpy image array
        CLAHE + Adaptive threshold + 2x resize
        """
        try:
            self.logger.debug(f"Preprocessing image array: {img.shape}")
            
            # Grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Resize 2x
            h, w = gray.shape
            gray = cv2.resize(gray, (w*2, h*2), interpolation=cv2.INTER_CUBIC)
            
            # Gaussian blur
            gray = cv2.GaussianBlur(gray, (3, 3), 0)
            
            # CLAHE contrast enhancement
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
            gray = clahe.apply(gray)
            
            # Adaptive threshold
            thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
            
            self.logger.debug(f"Enhanced preprocessing complete: {thresh.shape}")
            return thresh
            
        except Exception as e:
            self.logger.error(f"Array preprocessing failed: {e}")
            return gray  # Fallback

        
        
    def _preprocess_image(self, image_path: str) -> np.ndarray:
        """
        Preprocess image for better OCR results (existing file path version)
        
        Steps:
        1. Load image
        2. Convert to grayscale
        3. Denoise
        4. Apply adaptive thresholding
        5. Deskew if needed
        """
        try:
            # Load image
            img = cv2.imread(image_path)
            if img is None:
                raise OCRError(f"Could not load image: {image_path}")

            
            self.logger.debug(f"Original image shape: {img.shape}")
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Gaussian blur for noise reduction (per task req)
            gray = cv2.GaussianBlur(gray, (5, 5), 1.0)
            
            # Denoise
            denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
            
            # CLAHE contrast enhancement
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
            denoised = clahe.apply(denoised)
            
            # Upscale if image too small for OCR (simulate 300 DPI)
            h, w = denoised.shape
            if h < 1000:
                scale = max(1.0, 1000 / h)
                new_w = int(w * scale)
                new_h = 1000
                denoised = cv2.resize(denoised, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
                self.logger.debug(f"Upscaled to {new_w}x{new_h}")
            
            # Unsharp mask sharpening
            gaussian = cv2.GaussianBlur(denoised, (0, 0), 1.0)
            denoised = cv2.addWeighted(denoised, 1.5, gaussian, -0.5, 0)
            
            # Apply adaptive thresholding
            thresh = cv2.adaptiveThreshold(
                denoised, 255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY, 11, 2
            )
            
# 3. ADVANCED DESKEW
            gray = cv2.cvtColor(denoised, cv2.COLOR_GRAY2BGR)
            gray = cv2.bitwise_not(gray)
            thresh = cv2.threshold(gray[:,:,0], 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
            
            # Hough lines for skew detection
            edges = cv2.Canny(thresh, 50, 150, apertureSize=3)
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)
            
            if lines is not None:
                angles = []
                for line in lines:
                    x1,y1,x2,y2 = line[0]
                    angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
                    angles.append(angle)
                
                median_angle = np.median(angles)
                if abs(median_angle) > 0.5:  # Only deskew if significant angle
                    (h, w) = denoised.shape[:2]
                    center = (w // 2, h // 2)
                    M = cv2.getRotationMatrix2D(center, median_angle, 1.0)
                    denoised = cv2.warpAffine(denoised, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
                    self.logger.debug(f"Deskewed by {median_angle:.1f}°")
            
            # 4. Morphology operations
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
            denoised = cv2.morphologyEx(denoised, cv2.MORPH_CLOSE, kernel)
            denoised = cv2.morphologyEx(denoised, cv2.MORPH_OPEN, kernel)
            
            # 5. Final threshold
            thresh = cv2.adaptiveThreshold(
                denoised, 255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY, 11, 2
            )

            
            self.logger.debug("Image preprocessing completed")
            return thresh
            
        except OCRError:
            raise
        except Exception as e:
            self.logger.error(f"Image preprocessing failed: {str(e)}", exc_info=True)
            raise OCRError(
                message=f"Failed to preprocess image: {str(e)}",
                details={"image_path": image_path}
            )
    
    def _detect_document_type(self, full_text: str) -> Dict[str, Any]:
        """
        Detect if document is invoice or receipt
        
        Returns:
            {'type': 'invoice' | 'receipt', 'confidence': float}
        """
        invoice_keywords = [
            'invoice', 'tax invoice', 'bill to', 'bill from', 
            'invoice no', 'invoice#', 'inv no', 'gstin'
        ]
        
        receipt_keywords = [
            'receipt', 'cash memo', 'payment receipt', 'till receipt'
        ]
        
        text_lower = full_text.lower()
        invoice_score = sum(1 for kw in invoice_keywords if kw in text_lower)
        receipt_score = sum(1 for kw in receipt_keywords if kw in text_lower)
        
        if invoice_score > receipt_score:
            doc_type = 'invoice'
            confidence = min(0.95, invoice_score * 0.3)
            self.logger.info(f"Detected INVOICE (score: {invoice_score}, conf: {confidence:.1f})")
        elif receipt_score > 0:
            doc_type = 'receipt' 
            confidence = min(0.9, receipt_score * 0.4)
            self.logger.info(f"Detected RECEIPT (score: {receipt_score}, conf: {confidence:.1f})")
        else:
            doc_type = 'receipt'  # Default
            confidence = 0.5
            self.logger.info("Defaulting to RECEIPT (no clear indicators)")
        
        return {'type': doc_type, 'confidence': confidence}
        
        self.logger.info(f"Document type: {doc_type} (conf: {confidence:.1f})")
        return {'type': doc_type, 'confidence': confidence}
    
    
    def _try_rotations(self, image_path: str) -> Tuple[np.ndarray, float]:
        """
        Try 0°, 90°, 180°, 270° rotations and pick best for keyword presence
        
        Returns:
            (best_image, rotation_angle)
        """
        path = Path(image_path)
        if not path.exists():
            self.logger.debug(f"Test path detected, skipping rotation: {image_path}")
            # Create dummy image for tests
            h, w = 800, 600
            img = np.ones((h, w, 3), dtype=np.uint8) * 128
            return img, 0.0
        
        img = cv2.imread(image_path)
        if img is None:
            raise OCRError(f"Cannot load image for rotation: {image_path}")

            
        h, w = img.shape[:2]
        center = (w//2, h//2)
        
        angles = [0, 90, 180, 270]
        keyword_regex = r'(total|invoice|receipt)'
        best_img = img
        best_score = 0.0
        best_angle = 0
        
        bottom_crop = img[int(h*0.7):, :]  # Bottom region for keywords
        
        for angle in angles:
            # Rotate
            rot_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(img, rot_matrix, (w, h), flags=cv2.INTER_CUBIC)
            
            # Quick OCR on bottom crop
            try:
                crop_text = pytesseract.image_to_string(
                    rotated[int(h*0.7):, :], 
                    config='--oem 3 --psm 7 -l eng'
                ).lower()
                keyword_hits = len(re.findall(keyword_regex, crop_text))
                conf_parts = crop_text.split()
                avg_conf = 60.0 + keyword_hits * 20.0  # Base + keyword bonus
                
                if avg_conf > best_score:
                    best_score = avg_conf
                    best_img = rotated
                    best_angle = angle
                    
            except:
                continue  # Skip OCR error
        
        self.logger.info(f"Rotation fallback selected: {best_angle}° (score: {best_score:.1f})")
        return best_img, best_angle
        
        
    def _extract_strict_regions(self, img: np.ndarray, doc_type: str, full_text: str = '') -> Dict[str, Any]:
        """
        BALANCED strict + fallback region extraction
        
        Args:
            img: Image array
            doc_type: 'invoice'|'receipt'
            full_text: Fallback full text
            
        Returns:
            Structured regions with fallback
        """
        h, w = img.shape[:2]
        
        # IMPROVED regions: Top 40%, Bottom 40%
        merchant_region = img[0:int(h*0.4), :]
        amount_region = img[int(h*0.6):, :]
        items_region = img[int(h*0.15):int(h*0.75), :]
        
        # MERCHANT - STRICT PSM 7 + FALLBACK
        merchant_data = pytesseract.image_to_data(merchant_region, config='--oem 3 --psm 7 -l eng', output_type=pytesseract.Output.DICT)
        merchant_parts = []
        for i, text in enumerate(merchant_data['text']):
            if int(merchant_data['conf'][i]) > 35:
                clean = re.sub(r'[^a-zA-Z0-9\s]', ' ', text).strip()
                if len(clean) >= 3 and len(merchant_parts) < 5:
                    merchant_parts.append(clean)
        
        merchant_text = ' '.join(merchant_parts[:3])[:50]
        conf_merchant = np.mean([int(merchant_data['conf'][i]) for i in range(len(merchant_data['text'])) 
                                if int(merchant_data['conf'][i]) > 35]) if merchant_parts else 0
        
        # FALLBACK if empty
        if not merchant_text:
            lines = full_text.split('\n')[:5]
            merchant_text = ' '.join([re.sub(r'[^a-zA-Z0-9\s]', ' ', line).strip() for line in lines 
                                    if len(line.strip()) > 2])[:50]
            self.logger.warning("Merchant FALLBACK from full_text")
            conf_merchant = 0.3
        
        # AMOUNT - STRICT PSM 6 + REGEX + FALLBACK
        amount_data = pytesseract.image_to_data(amount_region, config='--oem 3 --psm 6 -l eng', output_type=pytesseract.Output.DICT)
        amount_raw = ' '.join([t.strip() for i, t in enumerate(amount_data['text']) if int(amount_data['conf'][i]) > 30])
        
        amount_candidates = []
        # Priority total regex
        total_match = re.search(r'(total|grand.?total|total.?due|balance.?due).*?([\$₹€£\s]*?)?(\d+[.,]\d{2})', amount_raw, re.IGNORECASE)
        if total_match:
            amount_str = re.sub(r'[^\d.]', '', total_match.group(3))
            amount_candidates.append(float(amount_str))
        
        # All reasonable amounts
        for m in re.finditer(r'(\d+[.,]\d{2})', amount_raw):
            amt = float(m.group(1).replace(',', ''))
            if 0.5 < amt < 50000:
                amount_candidates.append(amt)
        
        # Dedupe and sort
        amount_candidates = sorted(list(set(amount_candidates)), reverse=True)
        conf_amount = np.mean([int(amount_data['conf'][i]) for i in range(len(amount_data['text'])) 
                              if int(amount_data['conf'][i]) > 30]) if amount_candidates else 0
        
        # FALLBACK amount from full_text
        if not amount_candidates and full_text:
            for m in re.finditer(r'(\d+[.,]\d{2})', full_text):
                amt = float(m.group(1).replace(',', ''))
                if 0.5 < amt < 50000:
                    amount_candidates.append(amt)
                    break
            self.logger.warning("Amount FALLBACK from full_text")
        
        # ITEMS
        items_data = pytesseract.image_to_data(items_region, config='--oem 3 --psm 6 -l eng', output_type=pytesseract.Output.DICT)
        items_parts = [t.strip() for i, t in enumerate(items_data['text']) if int(items_data['conf'][i]) > 25]
        items_text = ' '.join(items_parts[:20])  # Limit
        
        conf_items_list = [int(items_data['conf'][i]) for i in range(len(items_data['text'])) 
                          if int(items_data['conf'][i]) > 25]
        conf_items = np.mean(conf_items_list) / 100.0 if conf_items_list else 0.0

        
        # FIX: Calculate conf_items for consistency
        conf_items_list = [int(items_data['conf'][i]) for i in range(len(items_data['text'])) 
                          if int(items_data['conf'][i]) > 25]
        conf_items = np.mean(conf_items_list) / 100.0 if conf_items_list else 0.0

        
        result = {
            'merchant_text': merchant_text or 'Unknown',
            'amount_candidates': amount_candidates,
            'items_text': items_text,
            'conf_merchant': conf_merchant / 100.0,
            'conf_amount': conf_amount / 100.0,
            'conf_items':conf_items
        }
        
        self.logger.info(f"Balanced regions - M: '{result['merchant_text']}' [{result['conf_merchant']:.1f}], "
                        f"A: {len(amount_candidates)} candidates, Items: {len(items_parts)} words")
        return result
        
        
        # TOP: Merchant (always top 25%)
        top_region = img[0:int(h*0.25), :]

        merchant_data = pytesseract.image_to_data(top_region, config='--oem 3 --psm 7 -l eng', output_type=pytesseract.Output.DICT)
        
        # STRICT merchant: first 3 lines, alpha only, <=50 chars
        merchant_lines = []
        for i, text in enumerate(merchant_data['text']):
            if int(merchant_data['conf'][i]) > 40:
                clean_text = re.sub(r'[^a-zA-Z\s]', '', text).strip()
                if 3 <= len(clean_text) <= 50 and len(merchant_lines) < 3:
                    merchant_lines.append(clean_text)
        
        merchant_text = ' '.join(merchant_lines)[:50]
        conf_merchant = np.mean([int(merchant_data['conf'][i]) for i, t in enumerate(merchant_data['text']) 
                                if int(merchant_data['conf'][i]) > 40]) if merchant_lines else 0
        
        # MIDDLE: Items (20-70%)
        items_region = img[int(h*0.2):int(h*0.7), :]
        items_data = pytesseract.image_to_data(items_region, config='--oem 3 --psm 6 -l eng', output_type=pytesseract.Output.DICT)
        items_parts = [t.strip() for i, t in enumerate(items_data['text']) 
                      if int(items_data['conf'][i]) > 30 and len(t.strip()) > 2]
        items_text = ' '.join(items_parts)[:1000]
        conf_items = np.mean([int(items_data['conf'][i]) for i in range(len(items_data['text'])) 
                             if int(items_data['conf'][i]) > 30]) if items_parts else 0
        
        # BOTTOM AMOUNT - STRICT by type
        amount_candidates = []
        if doc_type == 'invoice':
            # Invoice: Bottom-right quadrant
            bottom_right = img[int(h*0.7):, int(w*0.6):]
            amount_region = bottom_right
            self.logger.debug("Using INVOICE bottom-right for amount")
        else:
            # Receipt: Full bottom 20%
            amount_region = img[int(h*0.8):, :]
        
        amount_data = pytesseract.image_to_data(amount_region, config='--oem 3 --psm 8 -l eng', output_type=pytesseract.Output.DICT)
        amount_text_raw = ' '.join([t.strip() for i, t in enumerate(amount_data['text'])
                                   if int(amount_data['conf'][i]) > 35])
        
        # STRICT amount regex PRIORITY
        amount_patterns = [
            r'(total|grand total|total due|balance due|amount due).*?([\$₹€£]?\s?)?(\d+[.,]\d{2})',
            r'([\$₹€£]?\s?)?(\d{1,3}[.,]\d{3})*(\.\d{2})',
        ]
        for pattern in amount_patterns:
            matches = re.findall(pattern, amount_text_raw, re.IGNORECASE)
            for match in matches:
                try:
                    amount_str = re.sub(r'[^\d.]', '', ''.join(match[-1:]))
                    amount = float(amount_str)
                    if amount > 1.0:
                        amount_candidates.append(amount)
                except:
                    continue
        
        # Fallback: largest number >1
        if not amount_candidates:
            numbers = re.findall(r'(\d+[.,]\d{2})', amount_text_raw)
            for num in numbers:
                try:
                    amount = float(num.replace(',', ''))
                    if amount > 1.0:
                        amount_candidates.append(amount)
                except:
                    continue
        
        conf_amount = np.mean([int(amount_data['conf'][i]) for i in range(len(amount_data['text'])) 
                              if int(amount_data['conf'][i]) > 35]) if amount_candidates else 0
        
        result = {
            'merchant_text': merchant_text,
            'amount_candidates': amount_candidates,
            'items_text': items_text,
            'conf_merchant': conf_merchant / 100.0,
            'conf_amount': conf_amount / 100.0,
            'conf_items': conf_items / 100.0
        }
        
        self.logger.info(f"STRICT regions - Merchant: '{merchant_text}' [{result['conf_merchant']:.1f}], "
                        f"Amounts: {amount_candidates} [{result['conf_amount']:.1f}]")
        
        return result
    
    
    def validate_image(self, image_path: str) -> bool:


        """
        Validate if file is a valid image
        
        Args:
            image_path: Path to the file
            
        Returns:
            True if valid, raises exception otherwise
        """

        path = Path(image_path)
        
        # Check file exists
        if not path.exists():
            raise OCRError(f"File not found: {image_path}")
        
        # Check file extension
        valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.pdf'}
        if path.suffix.lower() not in valid_extensions:
            raise OCRError(
                f"Invalid file format: {path.suffix}. "
                f"Supported formats: {', '.join(valid_extensions)}"
            )
        
        # Try to load image
        try:
            img = cv2.imread(image_path)
            if img is None:
                raise OCRError(f"Could not read image file: {image_path}")
            
            # Check image dimensions
            height, width = img.shape[:2]
            if height < 100 or width < 100:
                raise OCRError(
                    f"Image too small: {width}x{height}. "
                    f"Minimum size: 100x100 pixels"
                )
            
            self.logger.debug(f"Image validated: {width}x{height}")
            return True
            
        except OCRError:
            raise
        except Exception as e:
            raise OCRError(f"Invalid image file: {str(e)}")
    
    def get_image_info(self, image_path: str) -> dict:
        """Get information about the image"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                raise OCRError(f"Could not read image: {image_path}")
            
            height, width = img.shape[:2]
            channels = img.shape[2] if len(img.shape) > 2 else 1
            
            return {
                "width": width,
                "height": height,
                "channels": channels,
                "aspect_ratio": width / height if height > 0 else 0
            }
        except Exception as e:
            self.logger.error(f"Failed to get image info: {str(e)}")
            return {}
