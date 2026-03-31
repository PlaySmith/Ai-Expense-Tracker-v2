# 🧠 SmartSpend AI - Implementation Plan

## Executive Summary

This document provides a comprehensive blueprint for building the SmartSpend AI MVP - a receipt scanning and expense tracking application. The plan follows industry best practices with a service-layer architecture that supports future AI/analytics upgrades.

---

## 🎯 Project Goals

### Primary Goal
Build a working MVP in 7 days that:
- ✅ Extracts expense data from receipt images using OCR
- ✅ Stores expenses in a database
- ✅ Displays expenses in a simple dashboard
- ✅ Handles errors gracefully
- ✅ Provides clear logging for debugging

### Secondary Goals
- ✅ Scalable architecture for future AI features
- ✅ Clean separation of concerns
- ✅ Professional code organization
- ✅ Easy to extend and maintain

---

## 🏗️ Architecture Overview

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                             │
│                     (React + Vite)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │ Upload Page  │  │  Dashboard   │  │ Error Bound  │        │
│  │  - Dropzone  │  │  - List View │  │  - Fallback  │        │
│  │  - Preview   │  │  - Sorting   │  │  - Logging   │        │
│  │  - Progress  │  │  - Delete    │  │              │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP/REST API
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                      BACKEND (FastAPI)                        │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  API Layer (Routes)                                     │ │
│  │  ├── POST /upload    → Receive image, return extracted  │ │
│  │  ├── GET /expenses   → List all expenses               │ │
│  │  ├── GET /expenses/{id} → Get specific expense          │ │
│  │  └── DELETE /expenses/{id} → Delete expense             │ │
│  └────────────────────┬────────────────────────────────────┘ │
│                       │                                      │
│  ┌────────────────────▼────────────────────────────────────┐ │
│  │  Service Layer (Business Logic)                         │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │ │
│  │  │ OCR Service │  │Parser Service│  │Expense Svc  │     │ │
│  │  │ - Preprocess│  │ - Extract   │  │ - CRUD      │     │ │
│  │  │ - Tesseract │  │   Amount    │  │ - Validate  │     │ │
│  │  │ - Confidence│  │ - Extract   │  │ - Workflow  │     │ │
│  │  │             │  │   Date      │  │             │     │ │
│  │  │             │  │ - Merchant  │  │             │     │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘     │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  Data Layer                                             │ │
│  │  ├── SQLAlchemy Models (User, Expense)                 │ │
│  │  ├── Pydantic Schemas (Validation)                      │ │
│  │  └── SQLite Database (PostgreSQL later)                 │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  Infrastructure                                         │ │
│  │  ├── Error Handlers (Global exception handling)         │ │
│  │  ├── Logging (Structured logs with rotation)            │ │
│  │  └── File Storage (Temp upload directory)               │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Detailed File Structure

### Backend Structure

```
Backend/
├── app/
│   ├── __init__.py                    # Package initialization
│   ├── main.py                        # FastAPI application entry
│   ├── config.py                      # Configuration settings
│   ├── database.py                    # Database connection & session
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── models.py                  # SQLAlchemy models
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── expense_schema.py          # Pydantic models
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── expenses.py                # Expense API endpoints
│   │   └── auth.py                    # Auth endpoints (optional)
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ocr_service.py             # OCR processing
│   │   ├── parser_service.py          # Text parsing logic
│   │   └── expense_service.py         # Business logic
│   │
│   └── utils/
│       ├── __init__.py
│       ├── error_handlers.py          # Exception handling
│       ├── logger.py                  # Logging configuration
│       └── validators.py              # Input validation
│
├── uploads/                           # Temporary file storage
├── logs/                              # Application logs
├── tests/                             # Test files
├── requirements.txt                   # Python dependencies
└── .env.example                       # Environment template
```

### Frontend Structure

```
Frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── common/
│   │   │   ├── ErrorBoundary.jsx      # React error boundary
│   │   │   ├── LoadingSpinner.jsx     # Loading indicator
│   │   │   ├── ErrorMessage.jsx       # Error display
│   │   │   └── Button.jsx             # Reusable button
│   │   ├── Upload/
│   │   │   ├── UploadComponent.jsx    # Main upload component
│   │   │   ├── UploadComponent.css    # Styles
│   │   │   └── FilePreview.jsx        # File preview sub-component
│   │   └── ExpenseList/
│   │       ├── ExpenseList.jsx        # Expense table
│   │       ├── ExpenseList.css        # Styles
│   │       ├── ExpenseItem.jsx        # Single expense row
│   │       └── EditModal.jsx          # Edit expense modal
│   │
│   ├── pages/
│   │   ├── HomePage.jsx               # Landing page
│   │   ├── UploadPage.jsx             # Upload page
│   │   └── DashboardPage.jsx          # Dashboard page
│   │
│   ├── api/
│   │   └── API.js                     # Axios configuration
│   │
│   ├── utils/
│   │   ├── errorHandler.js            # Frontend error handling
│   │   └── formatters.js              # Date/currency formatters
│   │
│   ├── App.jsx                        # Main app component
│   ├── main.jsx                       # Entry point
│   └── index.css                      # Global styles
├── package.json
├── vite.config.js
└── .env.example
```

---

## 🔧 Technology Stack

### Backend
| Component | Technology | Purpose |
|-----------|------------|---------|
| Framework | FastAPI | High-performance API framework |
| Database | SQLite (PostgreSQL later) | Data persistence |
| ORM | SQLAlchemy | Database abstraction |
| OCR | Tesseract (pytesseract) | Text extraction from images |
| Image Processing | OpenCV (cv2) | Image preprocessing |
| Validation | Pydantic | Data validation |
| Auth | python-jose + passlib | JWT authentication (optional) |
| Server | Uvicorn | ASGI server |

### Frontend
| Component | Technology | Purpose |
|-----------|------------|---------|
| Framework | React 18 | UI library |
| Build Tool | Vite | Fast development & building |
| HTTP Client | Axios | API communication |
| Routing | React Router DOM | Page navigation |
| Styling | CSS Modules | Component styling |
| Icons | Lucide React | Icon library |

---

## 📊 Data Flow Diagram

### Receipt Upload Flow

```
┌─────────┐     ┌─────────────┐     ┌──────────────┐
│  User   │────▶│ Select File │────▶│  Validate    │
│ Action  │     │  (Frontend) │     │  (Frontend)  │
└─────────┘     └─────────────┘     └──────┬───────┘
                                           │
                                           ▼
┌─────────┐     ┌─────────────┐     ┌──────────────┐
│ Display │◀────│    Parse    │◀────│    OCR       │
│ Result  │     │   Response  │     │  (Backend)   │
│         │     │  (Frontend) │     └──────┬───────┘
└─────────┘     └─────────────┘            │
                                           ▼
                                    ┌──────────────┐
                                    │  Preprocess  │
                                    │   Image      │
                                    │  (OpenCV)    │
                                    └──────────────┘
```

### Expense Retrieval Flow

```
┌─────────┐     ┌─────────────┐     ┌──────────────┐
│  User   │────▶│  Request    │────▶│   Validate   │
│ Action  │     │   Expenses  │     │   Request    │
│         │     │  (Frontend) │     │  (Backend)   │
└─────────┘     └─────────────┘     └──────┬───────┘
                                           │
                                           ▼
┌─────────┐     ┌─────────────┐     ┌──────────────┐
│ Display │◀────│   Format    │◀────│    Query     │
│  List   │     │   Response  │     │   Database   │
│         │     │  (Backend)  │     │  (SQLAlchemy)│
└─────────┘     └─────────────┘     └──────────────┘
```

---

## 🔍 OCR Processing Pipeline

### Step-by-Step OCR Flow

```
┌─────────────────┐
│  Input Image    │
│  (JPG/PNG/PDF)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Validation     │
│  - File type    │
│  - File size    │
│  - Corruption   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Preprocessing  │
│  - Grayscale    │
│  - Denoising    │
│  - Thresholding │
│  - Deskew (opt) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  OCR Extraction │
│  - Tesseract    │
│  - Config:      │
│    --psm 6      │
│    -l eng       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Confidence     │
│  Check          │
│  - Score > 60?  │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌───────┐  ┌────────┐
│ PASS  │  │  FAIL  │
│       │  │ Flag for│
│ Parse │  │ manual  │
│       │  │ review  │
└───┬───┘  └────────┘
    │
    ▼
┌─────────────────┐
│  Raw Text       │
│  Output         │
└─────────────────┘
```

---

## 🔎 Parser Logic Details

### Amount Extraction Algorithm

```python
def extract_amount(text: str) -> Optional[float]:
    """
    1. Find all currency patterns: \d+\.\d{2}
    2. Filter out suspicious values (too small/large)
    3. Return largest value (usually the total)
    4. Return None if no valid amount found
    """
```

### Date Extraction Algorithm

```python
def extract_date(text: str) -> Optional[str]:
    """
    Supported formats:
    - DD/MM/YYYY
    - DD-MM-YYYY
    - MM/DD/YYYY
    - YYYY-MM-DD
    - DD/MM/YY
    - DD Mon YYYY (e.g., 12 Jan 2024)
    
    Returns: ISO format YYYY-MM-DD
    """
```

### Merchant Extraction Algorithm

```python
def extract_merchant(text: str) -> Optional[str]:
    """
    1. Get first non-empty line
    2. Filter out common headers (RECEIPT, TAX INVOICE, etc.)
    3. Clean special characters
    4. Return cleaned name or None
    """
```

---

## ⚠️ Error Handling Strategy

### Error Categories

| Category | Examples | Handling Strategy |
|----------|----------|-------------------|
| **Upload Errors** | Invalid file type, File too large, Corrupt image | Validate before upload, clear user message |
| **OCR Errors** | No text detected, Low confidence, Unsupported language | Flag for manual review, suggest retaking photo |
| **Parser Errors** | No amount found, Multiple amounts, Invalid date | Pre-fill what we found, highlight missing fields |
| **Database Errors** | Connection lost, Constraint violation, Timeout | Retry logic, queue for later, notify user |
| **Network Errors** | Timeout, DNS failure, Server down | Auto-retry, offline queue, user notification |

### Error Response Format

```json
{
  "status": "error",
  "error_code": "OCR_LOW_CONFIDENCE",
  "message": "We couldn't clearly read this receipt. Try taking a clearer photo with better lighting.",
  "details": {
    "confidence_score": 45,
    "suggested_action": "retake_photo",
    "extracted_text_preview": "..."
  },
  "timestamp": "2024-02-13T10:30:00Z"
}
```

### Auto Problem Identification

1. **Low OCR Confidence** (< 60%)
   - Flag: `NEEDS_REVIEW`
   - Action: Show warning, allow manual edit

2. **No Amount Found**
   - Flag: `MANUAL_ENTRY_REQUIRED`
   - Action: Pre-fill other fields, highlight amount field

3. **Duplicate Detection**
   - Compare file hash or extracted data
   - Flag: `POSSIBLE_DUPLICATE`
   - Action: Show warning, ask for confirmation

4. **Corrupt Image**
   - Detect during validation
   - Flag: `INVALID_IMAGE`
   - Action: Reject immediately with clear message

---

## 📝 Logging Strategy

### Log Levels

| Level | Usage | Example |
|-------|-------|---------|
| **DEBUG** | Detailed debugging info | OCR preprocessing steps, raw text |
| **INFO** | Normal operations | Upload received, expense saved |
| **WARNING** | Recoverable issues | Low OCR confidence, retry attempt |
| **ERROR** | Failed operations | Database connection failed, OCR crash |
| **CRITICAL** | System failure | Database corruption, out of disk space |

### Log Files

```
logs/
├── app.log          # General application logs
├── api.log          # API request/response logs
├── ocr.log          # OCR processing logs
├── error.log        # Error-only logs
└── audit.log        # Security/audit events
```

### Log Format

```
[2024-02-13 10:30:45] [INFO] [ocr_service] Receipt processed successfully
  - File: receipt_001.jpg
  - Merchant: Starbucks
  - Amount: $12.50
  - Confidence: 85%
  - Processing time: 1.2s
```

---

## 🗓️ 7-Day Development Timeline

### Day 1: Foundation
- [ ] Fix Database.py typo
- [ ] Create requirements.txt
- [ ] Set up FastAPI main.py
- [ ] Create folder structure
- [ ] Test database connection

### Day 2: Database & Models
- [ ] Refactor models into separate file
- [ ] Create Pydantic schemas
- [ ] Set up database migrations
- [ ] Create test data
- [ ] Test CRUD operations

### Day 3: OCR Module
- [ ] Implement OCR service with OpenCV
- [ ] Add image preprocessing
- [ ] Test with sample receipts
- [ ] Add confidence scoring
- [ ] Handle error cases

### Day 4: Parser & Services
- [ ] Implement parser service
- [ ] Amount extraction logic
- [ ] Date extraction logic
- [ ] Merchant extraction logic
- [ ] Create expense service workflow

### Day 5: API Routes
- [ ] Implement /upload endpoint
- [ ] Implement /expenses endpoints
- [ ] Add input validation
- [ ] Add error handling
- [ ] Test with Postman

### Day 6: Frontend
- [ ] Set up React with Vite
- [ ] Create upload component
- [ ] Create expense list component
- [ ] Connect to backend API
- [ ] Add basic styling

### Day 7: Polish & Deploy
- [ ] Add error boundaries
- [ ] Implement logging
- [ ] Write README
- [ ] Test end-to-end
- [ ] Deploy demo version

---

## 🎯 MVP Success Metrics

### Functional Requirements
- [ ] Upload receipt image (JPG, PNG)
- [ ] Extract amount with >70% accuracy
- [ ] Extract date with >60% accuracy
- [ ] Extract merchant with >50% accuracy
- [ ] Display expense list
- [ ] Delete expenses
- [ ] Handle errors gracefully

### Non-Functional Requirements
- [ ] API response time < 3 seconds
- [ ] OCR processing time < 5 seconds
- [ ] Log all errors
- [ ] Clear error messages for users
- [ ] Mobile-responsive UI

---

## 🚀 Future Roadmap

### Phase 2: AI Enhancement (Week 2-3)
- [ ] ML-based categorization
- [ ] Spending pattern analysis
- [ ] Anomaly detection
- [ ] Smart budget recommendations

### Phase 3: Advanced Features (Week 4-6)
- [ ] User authentication
- [ ] Multi-user support
- [ ] Bank integration
- [ ] Recurring expense detection
- [ ] Export to CSV/PDF

### Phase 4: Scale & Optimize (Week 7-8)
- [ ] PostgreSQL migration
- [ ] Redis caching
- [ ] Async processing (Celery)
- [ ] Cloud deployment
- [ ] Mobile app

---

## 📚 References

- FastAPI Documentation: https://fastapi.tiangolo.com/
- Tesseract OCR: https://github.com/tesseract-ocr/tesseract
- SQLAlchemy: https://docs.sqlalchemy.org/
- React Documentation: https://react.dev/

---

**Plan Version**: 1.0  
**Created**: 2024-02-13  
**Status**: Ready for Implementation
