# Ai-Expense-Tracker-v2 ✅ COMPLETE

## 🚀 Quick Start (PowerShell - Copy/paste each line separately)

**Backend Terminal 1**:
```
cd "ET V2/backend"
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000 --host 0.0.0.0
```

**Frontend Terminal 2**:
```
cd "ET V2/frontend"
npm run dev
```

**CMD Alternative** (change VSCode terminal to cmd.exe):
```
cd /d "ET V2\backend"
uvicorn app.main:app --reload --port 8000
```
```
cd /d "ET V2\frontend"
npm run dev
```

## Features
- AI OCR → Charts/Dashboard
- Glassmorphism UI + Themes
- Responsive Mobile

localhost:3001 ready!

## Features
- **AI OCR** Receipt → Merchant/Amount/Category
- **Dashboard** Recharts pie/stats/recent list (glassmorphism UI)
- **Upload** Drag-drop + progress + extraction preview
- **Themes** Dark/light toggle
- **Responsive** Mobile-first

## Test Flow
1. Start both servers
2. localhost:3001 → Dashboard (empty initially)
3. Upload receipt image → OCR → Dashboard updates with charts!
4. Backend logs in `logs/`

All TODO items done. Linter clean. Enjoy! 🎉
