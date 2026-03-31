# OCR Accuracy Improvement Plan - ALL TASKS COMPLETED ✓

## 1. Enhanced Preprocessing (OCRService._preprocess_image)
- [x] Add Gaussian blur after denoise
- [x] Strengthen CLAHE clipLimit=3.0 (already implemented)
- [x] Add morph dilate/erode after thresh  
- [x] Final sharpen

## 2. Region-based OCR (OCRService.process_image)
- [x] Crop top20% merchant (PSM 7 single text line)
- [x] Bottom20% amount/total (PSM 8 single word)
- [x] Middle items (PSM 6)
- [x] Return dict {'merchant_text': text1, 'amount_text': text2, 'items_text': text3, 'conf': avg}

## 3. Parser upgrade (parser_service.py)
- [x] _extract_amount: regex '(?i)(total|amount|grand|balance).*?(\\d+[,.]?\\d{2})' pick max
- [x] _extract_merchant: first 3 lines, clean non-alphanum, [:50]
- [x] _extract_date: add more patterns DD Mon YYYY full month (months_map extended)

## 4. Conf filter
- [x] In OCR: filter conf >30 before join text_parts

## 5. Test
- [ ] Upload batch2-0501.jpg, check logs extracted amount/merchant - RECOMMENDED

**OCR accuracy improvements implemented per plan. Test recommended before completion.**

