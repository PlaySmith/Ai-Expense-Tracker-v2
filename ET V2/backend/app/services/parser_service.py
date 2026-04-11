import re
from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional, Tuple, List
from ..utils.logger import LoggerMixin
from ..utils.error_handlers import ParserError

class ParserService(LoggerMixin):
    def __init__(self):
        super().__init__()

    def parse_receipt(self, ocr_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse OCR data - improved amount extraction.
        """
        self.logger.info("Parsing OCR data")
        self.requires_review = True  # Default
        try:
            merchant_text = ocr_data.get('merchant_text', '') or ''
            bottom_text = ocr_data.get('amount_text', '') or ''
            items_text = ocr_data.get('items_text', '') or ''
            full_text = ocr_data.get('full_text', '') or ''
            
            if not full_text.strip():
                self.logger.warning("No text extracted → fallback")
                return {
                    'amount': 0.01,
                    'merchant': 'Unreadable Receipt',
                    'date': None,
                    'category': 'Other',
                    'requires_review': True,
                    'confidence': 0.0,
                    'extracted_raw': ocr_data
                }

            merchant = self._extract_merchant(merchant_text)
            amount, amount_conf = self._extract_amount(bottom_text + ' ' + full_text)
            combined_for_date = f"{merchant_text}\n{bottom_text}\n{items_text}\n{full_text}"
            date = self._extract_date(combined_for_date)
            category = self._categorize(merchant or '', full_text)

            self.requires_review = (
                amount_conf < 0.7 or not merchant or date is None
            )
            date_boost = 0.15 if date is not None else 0.0
            overall_conf = min(
                1.0,
                amount_conf * 0.5
                + (1.0 if merchant else 0.0) * 0.35
                + date_boost,
            )

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
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        candidates = []
        for line in lines[:3]:
            clean = re.sub(r'[^a-zA-Z0-9\s]', ' ', line)
            clean = ' '.join(clean.split())[:50]
            if len(clean) >= 3:
                candidates.append(clean)
        return candidates[0] if candidates else None

    def _extract_amount(self, text: str) -> Tuple[float, float]:
        # Improved: findall \d+\.\d{2}, take last (total usually last)
        matches = re.findall(r'\d+\.\d{2}', text)
        if matches:
            amount = float(matches[-1])
            self.logger.debug(f"Found {len(matches)} amounts, using last: {amount}")
            return amount, 0.8
        self.logger.warning("No decimal amounts found")
        return 0.01, 0.4

    def _normalize_two_digit_year(self, y: int) -> int:
        if y >= 100:
            return y
        return 2000 + y if y < 70 else 1900 + y

    def _try_ymd(self, y: int, m: int, d: int) -> Optional[datetime]:
        try:
            if y < 1990 or y > 2100:
                return None
            return datetime(y, m, d)
        except (ValueError, TypeError):
            return None

    def _parse_slash_date(self, a: int, b: int, y: int) -> Optional[datetime]:
        y = self._normalize_two_digit_year(y)
        # If one part > 12, that side must be day → unambiguous DMY or MDY
        if a > 12:
            return self._try_ymd(y, b, a)
        if b > 12:
            return self._try_ymd(y, a, b)
        # Both ≤12: assume day-first (India / most receipts)
        dt_dmy = self._try_ymd(y, b, a)
        if dt_dmy:
            return dt_dmy
        return self._try_ymd(y, a, b)

    def _date_keyword_bonus(self, text: str, pos: int) -> float:
        line_start = text.rfind("\n", 0, pos) + 1
        line_end = text.find("\n", pos)
        if line_end < 0:
            line_end = len(text)
        line = text[line_start:line_end].lower()
        keys = (
            "date",
            "bill date",
            "dt.",
            "dt ",
            "issued",
            "receipt",
            "txn",
            "transaction",
            "invoice",
            "time:",
        )
        return 1.0 if any(k in line for k in keys) else 0.0

    def _pick_best_date(
        self, text: str, candidates: List[Tuple[int, datetime]]
    ) -> Optional[datetime]:
        if not candidates:
            return None
        today = date.today()
        max_future = today + timedelta(days=2)

        scored: List[Tuple[float, datetime]] = []
        for pos, dt in candidates:
            d = dt.date()
            if d > max_future or d.year < 1990:
                continue
            bonus = self._date_keyword_bonus(text, pos)
            # Prefer keyword lines, then most recent on/before today
            recency = (d - date(1990, 1, 1)).days / 36525.0
            score = bonus * 10 + recency + (0.5 if d <= today else 0)
            scored.append((score, dt))

        if not scored:
            return None
        scored.sort(key=lambda x: -x[0])
        return scored[0][1]

    def _extract_date(self, text: str) -> Optional[datetime]:
        raw = text or ""
        if not raw.strip():
            return None

        candidates: List[Tuple[int, datetime]] = []

        # ISO: YYYY-MM-DD (also allow /)
        for m in re.finditer(
            r"\b(20\d{2}|19\d{2})-(\d{1,2})-(\d{1,2})\b", raw
        ):
            y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
            dt = self._try_ymd(y, mo, d)
            if dt:
                candidates.append((m.start(), dt))

        for m in re.finditer(
            r"\b(20\d{2}|19\d{2})/(\d{1,2})/(\d{1,2})\b", raw
        ):
            y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
            dt = self._try_ymd(y, mo, d)
            if dt:
                candidates.append((m.start(), dt))

        # DD/MM/YY or DD-MM-YY (separators . / -)
        for m in re.finditer(
            r"\b(\d{1,2})[/.-](\d{1,2})[/.-](\d{2,4})\b", raw
        ):
            a, b, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
            dt = self._parse_slash_date(a, b, y)
            if dt:
                candidates.append((m.start(), dt))

        # DD Mon YYYY or DD-Mon-YY
        months = (
            "jan|feb|mar|apr|may|jun|jul|aug|sept|sep|oct|nov|dec"
        )
        mon_pat = re.compile(
            rf"\b(\d{{1,2}})[\s./-]+({months})[a-z]*[\s./-]+(\d{{2,4}})\b",
            re.I,
        )
        month_names = {
            "jan": 1,
            "feb": 2,
            "mar": 3,
            "apr": 4,
            "may": 5,
            "jun": 6,
            "jul": 7,
            "aug": 8,
            "sep": 9,
            "sept": 9,
            "oct": 10,
            "nov": 11,
            "dec": 12,
        }
        for m in mon_pat.finditer(raw):
            d = int(m.group(1))
            mo_abbr = m.group(2).lower()[:4]
            if mo_abbr.startswith("sept"):
                mo_abbr = "sept"
            else:
                mo_abbr = mo_abbr[:3]
            mo = month_names.get(mo_abbr)
            if not mo:
                continue
            y = int(m.group(3))
            y = self._normalize_two_digit_year(y)
            dt = self._try_ymd(y, mo, d)
            if dt:
                candidates.append((m.start(), dt))

        # Mon DD, YYYY
        mon_first = re.compile(
            rf"\b({months})[a-z]*[\s./]+(\d{{1,2}}),?\s+(\d{{4}})\b",
            re.I,
        )
        for m in mon_first.finditer(raw):
            mk = m.group(1).lower()
            mo = month_names.get(mk) or month_names.get(mk[:3])
            if not mo:
                continue
            d = int(m.group(2))
            y = int(m.group(3))
            dt = self._try_ymd(y, mo, d)
            if dt:
                candidates.append((m.start(), dt))

        # OCR often glues time: "11/04/2025 14:30" — slash block already matches date part

        best = self._pick_best_date(raw, candidates)
        if best:
            return best

        # Fallback: first valid slash date without scoring filter (any reasonable in text)
        for m in re.finditer(
            r"\b(\d{1,2})[/.-](\d{1,2})[/.-](\d{2,4})\b", raw
        ):
            dt = self._parse_slash_date(
                int(m.group(1)), int(m.group(2)), int(m.group(3))
            )
            if dt and date(1990, 1, 1) <= dt.date() <= date.today() + timedelta(
                days=2
            ):
                return dt
        return None

    def _categorize(self, merchant: str, text: str) -> str:
        """
        Keyword-based categorization for Indian receipts.
        This is heuristic by nature, but it should split common merchants into
        more than just "Other" so the dashboard pie chart becomes useful.
        """
        lower = (merchant + " " + text).lower()

        rules = [
            (
                "Food & Dining",
                [
                    "restaurant",
                    "restro",
                    "cafe",
                    "coffee",
                    "coffeehouse",
                    "swiggy",
                    "zomato",
                    "kfc",
                    "pizza",
                    "domino",
                    "burger",
                    "biryani",
                    "thali",
                    "chaat",
                    "dosa",
                    "idli",
                    "soda",
                    "milk",
                    "hotel",
                    "bar",
                    "pub",
                ],
            ),
            (
                "Groceries",
                [
                    "grocery",
                    "supermarket",
                    "mart",
                    "dmart",
                    "d-mart",
                    "bigbasket",
                    "reliance fresh",
                    "spencer",
                    "vegetable",
                    "fruit",
                    "dairy",
                    "bakery",
                    "chicken",
                    "fish",
                ],
            ),
            (
                "Fuel & Transport",
                [
                    "fuel",
                    "petrol",
                    "diesel",
                    "cng",
                    "bpcl",
                    "hpcl",
                    "io ",
                    "indian oil",
                    "ioil",
                ],
            ),
            (
                "Transportation",
                [
                    "uber",
                    "ola",
                    "metro",
                    "bus",
                    "rail",
                    "railway",
                    "irctc",
                    "taxi",
                    "cab",
                    "auto",
                    "flight",
                    "airways",
                    "ticket",
                    "travels",
                ],
            ),
            (
                "Shopping",
                [
                    "amazon",
                    "flipkart",
                    "myntra",
                    "ajio",
                    "nykaa",
                    "lenskart",
                    "decathlon",
                    "nike",
                    "adidas",
                    "zara",
                    "hm",
                    "store",
                    "mall",
                    "shopping",
                    "electronics",
                    "apparel",
                    "clothing",
                    "fashion",
                ],
            ),
            (
                "Utilities",
                [
                    "electricity",
                    "power",
                    "bescom",
                    "tneb",
                    "gas",
                    "cylinder",
                    "water",
                    "broadband",
                    "internet",
                    "fiber",
                    "airtel",
                    "jio",
                    "vodafone",
                    "dth",
                    "dish",
                    "tata",
                ],
            ),
            (
                "Health & Pharmacy",
                [
                    "pharmacy",
                    "pharm",
                    "medicine",
                    "med",
                    "hospital",
                    "clinic",
                    "diagnostic",
                    "lab",
                    "x-ray",
                    "pathology",
                    "doctor",
                    "apollo",
                    "fortis",
                    "care",
                ],
            ),
            (
                "Education",
                [
                    "school",
                    "college",
                    "tuition",
                    "class",
                    "coaching",
                    "academy",
                    "exam",
                    "stationery",
                    "books",
                    "book",
                    "course",
                ],
            ),
            (
                "Entertainment",
                [
                    "cinema",
                    "movie",
                    "netflix",
                    "prime",
                    "spotify",
                    "bookmyshow",
                    "hotstar",
                    "gaming",
                    "concert",
                ],
            ),
            (
                "Rent",
                [
                    "rent",
                    "landlord",
                    "lease",
                    "property",
                ],
            ),
            (
                "Services",
                [
                    "service",
                    "services",
                    "salon",
                    "spa",
                    "laundry",
                    "dryclean",
                    "repair",
                    "maintenance",
                    "charging",
                    "charge",
                    "taxi",
                    "fee",
                ],
            ),
            (
                "Household",
                [
                    "home",
                    "furniture",
                    "hardware",
                    "paint",
                    "appliance",
                    "kitchen",
                    "refrigerator",
                    "washing",
                    "cleaning",
                ],
            ),
        ]

        for category, keywords in rules:
            if any(k in lower for k in keywords):
                return category

        # Fallback if no keywords match
        return "Other"

