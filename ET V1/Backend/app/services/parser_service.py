import re
from datetime import datetime
from typing import Optional, Dict, Any, List
import logging

from app.utils.error_handlers import ParserError
from app.utils.logger import LoggerMixin


class ParserService(LoggerMixin):
    """Service for parsing OCR text and extracting structured data"""
    
    def __init__(self):
        super().__init__()

    
    def parse_receipt(self, text: str, ocr_confidence: float = 1.0) -> Dict[str, Any]:
        """
        Parse receipt text and extract structured data
        
        Args:
            text: Raw OCR text from receipt
            ocr_confidence: OCR confidence (0-1.0) to weight parsing confidence
            
        Returns:
            Dictionary with extracted: amount, date, merchant, category
            
        Raises:
            ParserError: If parsing fails critically
        """
        try:
            self.logger.info("Parsing receipt text")
            self.logger.debug(f"Text to parse: {text[:500]}...")
            
            result = {
                "amount": None,
                "date": None,
                "merchant": None,
                "category": None,
                "confidence_scores": {},
                "warnings": []
            }
            
            # Extract amount
            amount, amount_confidence = self._extract_amount(text)
            amount_confidence *= ocr_confidence / 100.0
            result["amount"] = amount
            result["confidence_scores"]["amount"] = amount_confidence
            
            if amount is None:
                result["warnings"].append("Could not extract amount from receipt")
            
            # Extract date
            date, date_confidence = self._extract_date(text)
            date_confidence *= ocr_confidence / 100.0
            result["date"] = date
            result["confidence_scores"]["date"] = date_confidence
            
            if date is None:
                result["warnings"].append("Could not extract date from receipt")
            
            # Extract merchant
            merchant, merchant_confidence = self._extract_merchant(text)
            merchant_confidence *= ocr_confidence / 100.0
            result["merchant"] = merchant
            result["confidence_scores"]["merchant"] = merchant_confidence
            
            if merchant is None:
                result["warnings"].append("Could not extract merchant from receipt")
            
            # Determine category
            category = self._categorize_expense(merchant, text)
            result["category"] = category
            
            self.logger.info(
                f"Parsing complete: amount={amount}, date={date}, "
                f"merchant={merchant}, category={category}"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Parsing failed: {str(e)}", exc_info=True)
            raise ParserError(
                message=f"Failed to parse receipt: {str(e)}",
                details={"text_preview": text[:200]}
            )
    
    def _extract_amount(self, text: str) -> tuple[Optional[float], float]:
        """
        Extract total amount from receipt text
        
        Strategy:
        1. Prioritize 'total' keywords
        2. Then numeric patterns
        3. Pick largest reasonable amount
        """
        try:
            # Enhanced patterns - prioritize TOTAL/Amount keywords
            patterns = [
                r'(?i)(total|amount|grand|balance).*?(\\d+[,.]?\\d{2})',  # New prioritized total regex
                r'(?i)(total|amount|grand|balance|due|payable|owed)[^0-9]*?([$,₹€£]?\s*)?(\\d{1,3}(?:,\\d{2,3})*(?:\\.\\d{2}))?',  # Keyword + amount
                r'([$,₹€£]?\s*(\\d{1,3}(?:,\\d{2,3})*(?:\\.\\d{2})))',  # Currency + amount
                r'(\\d{2,6}(?:[.,]\\d{2}))',  # Numeric only
            ]
            
            all_amounts = []
            keyword_hits = 0
            
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    try:
                        # Extract numeric part
                        amount_str = ''.join(str(m) for m in match if isinstance(m, str) and m.replace('.','').replace(',','').isdigit() or m == '.')
                        amount_str = re.sub(r'[^\d.]', '', amount_str)
                        if amount_str and len(amount_str.split('.')) <= 2:
                            amount = float(amount_str)
                            if 0.01 <= amount <= 100000:
                                all_amounts.append(amount)
                                if len(match) > 1 and match[0]:  # Keyword match
                                    keyword_hits += 1
                    except (ValueError, IndexError):
                        continue
            
            if not all_amounts:
                self.logger.warning("No amounts found in text")
                return None, 0.0
            
            amount = max(all_amounts)
            confidence = min(100.0, 80.0 + (keyword_hits * 10) + (len(all_amounts) * 2))
            
            self.logger.debug(f"Extracted amount: {amount} ({keyword_hits} keyword hits, {len(all_amounts)} candidates, conf: {confidence:.1f}%)")
            return amount, confidence
            
        except Exception as e:
            self.logger.error(f"Amount extraction failed: {str(e)}")
            return None, 0.0
    
    def _extract_date(self, text: str) -> tuple[Optional[datetime], float]:
        """
        Extract date from receipt text
        
        Supports formats:
        - DD/MM/YYYY, DD-MM-YYYY
        - MM/DD/YYYY, MM-DD-YYYY
        - YYYY/MM/DD, YYYY-MM-DD
        - DD Mon YYYY (e.g., 12 Jan 2024)
        - DD Month YYYY (e.g., 12 January 2024)
        
        Returns:
            Tuple of (datetime, confidence_score)
        """
        try:
            date_patterns = [
                # DD/MM/YYYY or DD-MM-YYYY
                (r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})', 'dmy'),
                # YYYY/MM/DD or YYYY-MM-DD
                (r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})', 'ymd'),
                # DD Mon YYYY (e.g., 12 Jan 2024)
                (r'(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{4})', 'dmy_text'),
                # Month DD, YYYY
                (r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{1,2}),?\s+(\d{4})', 'mdy_text'),
            ]
            
            months_map = {
                'jan': 1, 'january': 1, 'feb': 2, 'february': 2, 'mar': 3, 'march': 3, 
                'apr': 4, 'april': 4, 'may': 5, 'jun': 6, 'june': 6, 'jul': 7, 'july': 7,
                'aug': 8, 'august': 8, 'sep': 9, 'september': 9, 'oct': 10, 'october': 10, 
                'nov': 11, 'november': 11, 'dec': 12, 'december': 12
            }
            
            found_dates = []
            
            for pattern, fmt in date_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                
                for match in matches:
                    try:
                        if fmt == 'dmy':
                            day, month, year = int(match[0]), int(match[1]), int(match[2])
                        elif fmt == 'ymd':
                            year, month, day = int(match[0]), int(match[1]), int(match[2])
                        elif fmt == 'dmy_text':
                            day = int(match[0])
                            month = months_map.get(match[1].lower()[:3], 0)
                            year = int(match[2])
                        elif fmt == 'mdy_text':
                            month = months_map.get(match[0].lower()[:3], 0)
                            day = int(match[1])
                            year = int(match[2])
                        else:
                            continue
                        
                        # Validate date
                        if 1 <= day <= 31 and 1 <= month <= 12 and 2000 <= year <= 2030:
                            date_obj = datetime(year, month, day)
                            found_dates.append(date_obj)
                            
                    except (ValueError, IndexError):
                        continue
            
            if not found_dates:
                self.logger.warning("No dates found in text")
                return None, 0.0
            
            # Return the most recent date (likely the receipt date)
            latest_date = max(found_dates)
            confidence = min(100.0, 80.0)  # Base confidence for date extraction
            
            self.logger.debug(f"Extracted date: {latest_date} (confidence: {confidence}%)")
            return latest_date, confidence
            
        except Exception as e:
            self.logger.error(f"Date extraction failed: {str(e)}")
            return None, 0.0
    
    def _extract_merchant(self, text: str) -> tuple[Optional[str], float]:
        """
        Extract merchant name from receipt text
        
        Strategy:
        1. Look for common receipt headers
        2. Get first substantial line
        3. Filter out common non-merchant text
        """
        try:
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            
            # Common words to filter out
            filter_words = [
                'receipt', 'invoice', 'tax', 'bill', 'order', 'ticket',
                'cash', 'credit', 'debit', 'payment', 'change', 'total',
                'subtotal', 'tax', 'gst', 'vat', 'thank you', 'welcome',
                'date', 'time', 'server', 'cashier', 'register', 'terminal'
            ]
            
            for line in lines[:3]:  # First 3 lines only
                # Skip short lines
                if len(line) < 3:
                    continue
                
                # Skip lines that are mostly numbers
                # Clean: keep alphanum + spaces, remove symbols
                clean = re.sub(r'[^a-zA-Z0-9\s]', ' ', line)
                clean = re.sub(r'\s+', ' ', clean).strip()
                # Remove pure numbers
                if not re.match(r'^\d+$', clean) and len(clean) >= 3:
                    merchant = clean[:50]  # Limit 50 chars
                    confidence = min(85.0, 50.0 + len(merchant) * 1.5)
                    self.logger.debug(f"Extracted merchant: {merchant} (conf: {confidence:.1f}%)")
                    return merchant, confidence
            
            self.logger.warning("Could not identify merchant")
            return None, 0.0
            
        except Exception as e:
            self.logger.error(f"Merchant extraction failed: {str(e)}")
            return None, 0.0
    
    def _categorize_expense(self, merchant: Optional[str], text: str) -> Optional[str]:
        """
        Categorize expense based on merchant and text content
        
        Simple keyword-based categorization
        """
        try:
            text_lower = (merchant or '').lower() + ' ' + text.lower()
            
            categories = {
                'Food & Dining': ['restaurant', 'cafe', 'coffee', 'food', 'pizza', 'burger', 
                                'sushi', 'dining', 'eat', 'kitchen', 'bakery', 'starbucks',
                                'mcdonald', 'kfc', 'dominos', 'swiggy', 'zomato', 'uber eats'],
                'Groceries': ['grocery', 'supermarket', 'mart', 'store', 'fresh', 'vegetable',
                            'fruit', 'dairy', 'meat', 'walmart', 'target', 'costco',
                            'bigbasket', 'grofers', 'dmart', 'reliance fresh'],
                'Transportation': ['gas', 'fuel', 'petrol', 'diesel', 'uber', 'lyft', 'taxi',
                                 'cab', 'auto', 'ola', 'rapido', 'metro', 'bus', 'train',
                                 'parking', 'toll'],
                'Shopping': ['mall', 'shop', 'retail', 'clothing', 'fashion', 'apparel',
                           'electronics', 'amazon', 'flipkart', 'myntra', 'ajio',
                           'snapdeal', 'ebay'],
                'Entertainment': ['movie', 'cinema', 'theater', 'game', 'entertainment',
                                'netflix', 'spotify', 'amazon prime', 'hotstar', 'bookmyshow'],
                'Health & Medical': ['pharmacy', 'medical', 'hospital', 'clinic', 'doctor',
                                   'medicine', 'health', 'apollo', 'medplus', '1mg'],
                'Utilities': ['electric', 'water', 'gas', 'internet', 'phone', 'mobile',
                            'bill', 'recharge', 'jio', 'airtel', 'vodafone', 'bsnl'],
                'Travel': ['hotel', 'flight', 'airline', 'booking', 'travel', 'trip',
                         'vacation', 'airbnb', 'makemytrip', 'goibibo', 'yatra'],
            }
            
            for category, keywords in categories.items():
                if any(keyword in text_lower for keyword in keywords):
                    self.logger.debug(f"Categorized as: {category}")
                    return category
            
            # Default category
            self.logger.debug("No category matched, using 'Uncategorized'")
            return "Uncategorized"
            
        except Exception as e:
            self.logger.error(f"Categorization failed: {str(e)}")
            return "Uncategorized"
