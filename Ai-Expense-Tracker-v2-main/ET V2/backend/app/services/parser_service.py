import re
from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional, Tuple, List
from ..utils.logger import LoggerMixin
from ..utils.error_handlers import ParserError
from dateutil import parser as dateutil_parser  # ADDED: For flexible date parsing

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
            amount, amount_conf = self._extract_amount_bottomup(full_text)  # Improved: bottom-up search
            combined_for_date = f"{merchant_text}\n{bottom_text}\n{items_text}\n{full_text}"
            date = self._extract_date(combined_for_date)
            category = self._categorize(merchant or '', full_text)

            # IMPROVED: Less strict confidence weighting
            # Only mark for review if BOTH amount is highly uncertain AND merchant is missing
            # Single missing property shouldn't mark for review
            amount_missing = amount_conf < 0.5
            merchant_missing = not merchant or merchant == "Unreadable Receipt"
            date_missing = date is None
            
            # Mark for review only if critical info is missing
            self.requires_review = (
                (amount_missing and merchant_missing) or  # Both missing = review needed
                amount_conf < 0.3  # Amount very uncertain = review needed
            )
            
            # Improved: More generous confidence scoring
            merchant_score = 0.8 if merchant and merchant != "Unreadable Receipt" else 0.0
            amount_score = amount_conf * 0.6  # Scale amount contribution down
            date_score = 0.2 if date is not None else 0.1  # Still some credit for attempting date
            
            overall_conf = min(1.0, merchant_score + amount_score + date_score)

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

    def _extract_amount_bottomup(self, text: str) -> Tuple[float, float]:
        """
        IMPROVED: Bottom-up total search - Start from bottom of text.
        Search for keywords like 'Grand Total', 'Total', 'Food Total', 'S.Tax', etc.
        Ignore 'Round off' and 'Sub Total'.
        Support multiple currencies and formats: ₹1000, $100, €50, 1000.00, 1,000.00
        ALSO: Support integer amounts without decimals (e.g., ₹250, 300, 1000)
        """
        lines = text.split('\n')
        
        # Tax keywords to ignore (these are components, not totals)
        tax_keywords = ['CGST', 'SGST', 'VAT', 'Tax', 'S.Tax', 'Service Tax', 'Round off', 'Sub Total', 'Subtotal']
        
        # Search from BOTTOM up (last lines first - where totals usually are)
        for i in range(len(lines) - 1, -1, -1):
            line = lines[i]
            
            # Skip empty lines and tax lines
            if not line.strip() or any(tax in line for tax in tax_keywords):
                continue
            
            # Look for total keywords (case-insensitive)
            if any(keyword in line.lower() for keyword in ['grand total', 'total', 'food total', 'amount', 'payable', 'due']):
                # Extract amount from this line - support both decimal and integer formats
                # Regex matches: ₹1000.00, ₹250, $100.50, €50, 1000.00, 1,000.00, 250
                amount_match = re.search(r'[₹$€]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?|\d+\.\d{2}|\d+)', line)
                if amount_match:
                    amount_str = amount_match.group(1).replace(',', '')
                    try:
                        amount = float(amount_str)
                        # Sanity check: receipt amounts are typically between ₹1 and ₹100,000
                        if 0.5 < amount < 100000:
                            self.logger.debug(f"Bottom-up found total: {amount} from line: {line}")
                            return amount, 0.85  # Higher confidence for explicit total keyword
                    except ValueError:
                        continue
        
        # Fallback: Look for largest reasonable number if no explicit total found
        # Match both decimal and integer formats
        all_numbers = re.findall(r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?|\d+\.\d{2}|\d+)', text)
        if all_numbers:
            amounts = []
            for num in all_numbers:
                try:
                    val = float(num.replace(',', ''))
                    # Filter out unreasonably small numbers and GST codes
                    # Accept amounts between ₹1 and ₹100,000
                    if 0.5 < val < 100000:
                        amounts.append(val)
                except ValueError:
                    continue
            
            if amounts:
                amount = max(amounts)
                self.logger.debug(f"No explicit total found, using largest reasonable number: {amount}")
                return amount, 0.65  # Lower confidence for inferred amount
        
        self.logger.warning("No amount found in receipt")
        return 0.01, 0.3

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
        """
        IMPROVED: Extract date from receipt text.
        Handles multiple formats:
        - DD/MM/YY (05/01/23)
        - DD-MM-YY (20-05-18)
        - DD-MMM-YY (20-May-18)
        - YYYY-MM-DD (2023-05-01)
        - DD Mon YYYY (20 May 2023)
        
        Enhanced logic:
        - Search from top (headers have dates first)
        - Use dateutil for flexible parsing
        - Validate date is reasonable (not in future, not before 1990)
        """
        raw = text or ""
        if not raw.strip():
            return None

        # Get today's date for validation
        today = date.today()
        max_future = today + timedelta(days=2)
        min_past = date(1990, 1, 1)

        # Extract potential date strings (flexible regex)
        # Match patterns like: 05/01/23, 20-May-18, 05-01-2023, etc.
        date_patterns = [
            r'\b(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\b',  # Numeric dates
            r'\b(\d{1,2}[-/]\w+[-/]\d{2,4})\b',  # With month name like 20-May-18
            r'\b(\w+[-/]\d{1,2}[-/]\d{2,4})\b',  # Month first like May-20-2018
        ]

        candidates = []
        for pattern in date_patterns:
            for match in re.finditer(pattern, raw, re.IGNORECASE):
                date_str = match.group(1)
                try:
                    # Use dateutil for intelligent parsing (handles DD/MM/YY, DD-Mon-YY, etc.)
                    parsed_date = dateutil_parser.parse(date_str, dayfirst=True)  # Prefer DD/MM/YY
                    
                    # Validate date is reasonable
                    if min_past <= parsed_date.date() <= max_future:
                        bonus = self._date_keyword_bonus(raw, match.start())
                        candidates.append((bonus, parsed_date.date()))
                        self.logger.debug(f"Found date: {parsed_date.date()} from '{date_str}'")
                except (ValueError, TypeError):
                    continue  # Skip invalid dates

        # Return best date (with highest keyword bonus, then most recent)
        if candidates:
            candidates.sort(key=lambda x: (-x[0], -x[1].toordinal()))  # Sort by bonus desc, then recent
            best_date = candidates[0][1]
            self.logger.debug(f"Selected date: {best_date}")
            return datetime.combine(best_date, datetime.min.time())

        self.logger.warning("No valid date found in receipt")
        return None
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

