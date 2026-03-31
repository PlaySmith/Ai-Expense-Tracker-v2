# Ai-Expense-Tracker-v2-side TODO

## Fix Server Reload Crash (ET V2/backend)

**Status: [IN PROGRESS]**

### Step 1: [DONE] Clean logger.py ✓
- Clean dictConfig setup

### Step 2: [DONE] Optimize ocr_service.py ✓
- Lazy Reader + PIL-only + fixes

### Step 3: [DONE] app/__init__.py ✓
- Lifespan try/except

### Step 4: [DONE] Test
- Server started: `cd ET V2/backend && uvicorn app:app --reload --host 0.0.0.0 --port 8000`
- Edit ocr_service.py → should reload cleanly (no logging crash)
- Test POST /expenses/upload image

### Step 5: [DONE] Cleanup ✓
- ocr_service_fixed.py deleted (obsolete)
- No reqs changes (opencv optional)

**CRASH FIX + ACCURACY BOOST COMPLETE!** 🎉

**New: OCR v2.1**
- Binary preprocess (autocontrast + threshold) 
- Strict conf 0.5+, low_text=0.5
- Parser: Total keywords, ₹10 floor (no ₹0.01 ghosts)

Server: http://localhost:8000/docs 
Upload receipt → 70%+ conf target.


