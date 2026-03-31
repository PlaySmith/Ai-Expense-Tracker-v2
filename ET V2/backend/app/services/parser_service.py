import re
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from ..utils.logger import LoggerMixin
from ..utils.error_handlers import ParserError

class ParserService(LoggerMixin):
    def __init__(self):
        super().__init__()

    def parse_receipt(self, ocr_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse OCR regions for Indian receipts - SAFE empty handling.
        """
        self.logger.info("Parsing OCR data")
        self.requires_review = True  # Default to review
        try:
            merchant_text = ocr_data.get('merchant_text', '') or ''
            bottom_text = ocr_data.get('amount_text', '') or ''
            items_text = ocr_data.get('items_text', '') or ''
            full_text = ocr_data.get('full_text', '') or ''
            
            if not full_text.strip():
                self.logger.warning("No text extracted from OCR - fallback")
                return {
                    'amount': None,
                    'merchant': 'Unreadable Receipt',
                    'date': None,
                    'category': 'Other',
                    'requires_review': True,
                    'confidence': 0.0,
                    'extracted_raw': ocr_data
                }

            merchant = self._extract_merchant(merchant_text)
            amount, amount_conf = self._extract_amount(bottom_text, full_text)
            date = self._extract_date(items_text + ' ' + full_text)
            category = self._categorize(merchant or '', full_text)

            self.requires_review = amount is None or amount_conf < 0.7 or not merchant
            overall_conf = min(1.0, amount_conf * 0.5 + (1.0 if merchant else 0.0) * 0.3 + 0.2)

            result = {
                'amount': amount,
                'merchant': merchant,
                'date': date,
                'category': category,
                'requires_review': self.requires_review,
                'confidence': overall_conf,
                'extracted_raw': {
                    'merchant_raw': merchant_text,
                    'amount_raw': bottom_text,
                    'items_raw': items_text[:500]
                }
            }

            self.logger.info(f"Parsed: amount={amount}, merchant='{merchant}', review={self.requires_review}")
            return result

        except Exception as e:
            self.logger.error(f"Parse failed: {e}")
            raise ParserError(f"Parsing failed: {str(e)}")

    def _extract_merchant(self, text: str) -> Optional[str]:
        "First 2-3 lines from TOP region."
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        candidates = []
        for line in lines[:3]:
            clean = re.sub(r'[^a-zA-Z0-9\s]', ' ', line)
            clean = ' '.join(clean.split())[:50]
            if len(clean) >= 3:
                candidates.append(clean)
        return candidates[0] if candidates else None

    def _extract_amount(self, bottom_text: str, full_fallback: str) -> Tuple[Optional[float], float]:
        "STRICT bottom region Grand Total ₹."
        pattern = r'(grand total|total)[^0-9]*₹?\s*([0-9,]+\.[0-9]{2})'
        match = re.search(pattern, bottom_text, re.IGNORECASE)
        if match:
            amt_str = re.sub(r'[^\d.]', '', match.group(2))
            return float(amt_str), 0.9

        amounts = re.findall(r'(\d+[.,]\d{2})', bottom_text)
        for amt_str in amounts:
            amt = float(amt_str.replace(',', ''))
            if amt > 1.0:
                return amt, 0.7

        amounts = re.findall(r'(\d+[.,]\d{2})', full_fallback)
        for amt_str in amounts:
            amt = float(amt_str.replace(',', ''))
            if 1.0 < amt < 100000:
                return amt, 0.4

        return None, 0.0

    def _extract_date(self, text: str) -> Optional[datetime]:
        "Indian formats DD/MM/YY."
        patterns = [r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})']
        for pat in patterns:
            match = re.search(pat, text)
            if match:
                d, m, y = map(int, match.groups())
                if y < 100: y += 2000 if y >= 25 else 1900
                try:
                    return datetime(y, m, d)
                except:
                    pass
        return None

    def _categorize(self, merchant: str, text: str) -> str:
        lower = (merchant + ' ' + text).lower()
        if any(k in lower for k in ['food', 'restaurant', 'cafe', 'swiggy', 'zomato']):
            return 'Food & Dining'
        return 'Other'

