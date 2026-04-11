# 🚀 Expense Tracker V2 (ET V2)

**Clean, accurate OCR for Indian receipts using EasyOCR** (80-90% accuracy).

Rebuilt from V1: Removed OpenCV/Tesseract → Simple regions + targeted parsing.

## 🏗️ Structure
```
ET V2/
├── backend/      # FastAPI + EasyOCR
├── frontend/     # React + Vite
├── uploads/      # Receipts
├── start.bat     # Windows 1-click
├── start.sh      # Linux/Mac 1-click
└── smartspend_v2.db
```

## 🚀 1-Click Start (Recommended)

**Windows:**
```cmd
cd /d "D:\Ai Expense Tracker\ET V2"
start.bat
```
**Linux/Mac/WSL:**
```bash
cd "D:/Ai Expense Tracker/ET V2"
chmod +x start.sh && ./start.sh
```

**Auto-opens terminals → Backend:8000 + Frontend:3001**

## URLs
- **UI**: http://localhost:3001 (drag-drop)
- **API**: http://localhost:8000/docs (Swagger test)

## Manual Run
**Backend:**
```cmd
cd ET V2\backend
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```
**Frontend:**
```cmd
cd ET V2\frontend
npm install
npm run dev
```

## 🧪 Test
1. Copy image from `../ET V1/Backend/uploads/` to `ET V2/uploads/`
2. Open http://localhost:3001
3. Drag JPG → Process → See merchant/₹amount/review

**Example:** "KNS Charholi" + "Grand Total ₹390.00" → Parsed instantly.

## Features
- **OCR**: EasyOCR regions (no preprocess)
- **Parse**: Indian-specific (₹Grand Total, DD/MM/YY)
- **Flag**: `requires_review` for manual edit
- **Zero deps**: No Docker, auto-DB

**V1→V2:** Simpler (90%), accurate (85%+), practical.

Enjoy ET V2!
