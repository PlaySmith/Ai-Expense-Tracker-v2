import re
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from ..utils.logger import LoggerMixin
# from ..utils.error_handlers import ParserError

class ParserService(LoggerMixin):
    def __init__(self):
        super().__init__()

    def parse_receipt(self, ocr_data: Dict[str, Any]) -> Dict[str, Any]:
        
        # V2.1 Parser - Strict amounts + merchant filter
        
        self.logger.info("Parsing OCR data")
        try:
            merchant_text = ocr_data.get('merchant_text', '') or ''
            bottom_text = ocr_data.get('amount_text', '') or ''
            items_text = ocr_data.get('items_text', '') or ''
            full_text = ocr_data.get('full_text', '') or ''
            
            if len(full_text.strip()) < 10:
                self.logger.warning("Insufficient text")
                return {
                    'amount': None,
                    'merchant': None,
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

            self.requires_review = amount is None or amount_conf < 0.75 or not merchant
            overall_conf = min(1.0, amount_conf * 0.5 + (1.0 if merchant else 0.0) * 0.35 + 0.15)

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

            self.logger.info(f"Parsed: amount={amount} merchant='{merchant}' conf={overall_conf:.1%} review={self.requires_review}")
            return result

        except Exception as e:
            self.logger.error(f"Parse failed: {e}")
            raise Exception(f"Parsing failed: {str(e)}")

    def _extract_merchant(self, text: str) -> Optional[str]:
        # \"\"\"
        # Top lines, filter junk.
        # \"\"\"
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        junk_keywords = ['tax invoice', 'cash memo', 'date:', 'gstin', 'pan']
        
        for line in lines[:4]:
            clean = re.sub(r'[^a-zA-Z0-9\s]', ' ', line)[:60]
            clean = ' '.join(clean.split())
            if len(clean) > 4 and not any(j in clean.lower() for j in junk_keywords):
                return clean.title()
        return None

    def _extract_amount(self, bottom_text: str, full_fallback: str) -> Tuple[Optional[float], float]:
        # \"\"\"
        # STRICT Total keywords + ₹10 floor.
        # \"\"\"
        text = bottom_text + ' ' + full_fallback
        self.logger.debug(f"Amount search in {len(text)} chars")
        
        # PRIORITY 1: Total keywords
        patterns = [
            r'(grand total|net payable|total amount|payable amount|balance)\s*(?:rs\.?|inr|₹)?\s*([\d,]+\.\d{2})',
            r'(?:rs\.?|₹)\s*([\d,]+\.\d{2})\s*(?:grand total|total|payable|amt)',
        ]
        for pat in patterns:
            match = re.search(pat, text, re.IGNORECASE)
            if match:
                amt_str = re.sub(r'[^\d.]', '', match.group(1) or match.group(2))
                try:
                    amt = float(amt_str)
                    if amt >= 10.0:
                        self.logger.info(f"Total keyword match: ₹{amt}")
                        return amt, 0.95
                except:
                    pass

        # PRIORITY 2: Largest realistic amounts
        amounts = re.findall(r'[\d,]+\.[\d]{2}', text)
        for amt_str in sorted(amounts, key=lambda x: float(x.replace(',', '')) or 0, reverse=True)[:5]:
            try:
                amt = float(amt_str.replace(',', ''))
                if 15.0 <= amt <= 100000:
                    self.logger.info(f"Largest realistic: ₹{amt}")
                    return amt, 0.75
            except:
                pass

        self.logger.warning("No valid amount")
        return None, 0.0

    def _extract_date(self, text: str) -> Optional[datetime]:
        patterns = [r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})']
        for pat in patterns:
            match = re.search(pat, text)
            if match:
                try:
                    d, m, y = map(int, match.groups())
                    if y < 100: 
                        y += 2000 if y > 24 else 1900
                    return datetime(y, m, d)
                except:
                    pass
        return None

    def _categorize(self, merchant: str, text: str) -> str:
        lower_text = (merchant + ' ' + text).lower()
        cats = {
            'food': ['food', 'restaurant', 'cafe', 'swiggy', 'zomato', 'dominos'],
            'fuel': ['petrol', 'diesel', 'bpcl', 'hpcl'],
            'shop': ['mart', 'store', 'bigbazaar']
        }
        for cat, keywords in cats.items():
            if any(k in lower_text for k in keywords):
                return f'{cat.title()}'
        return 'Other'

