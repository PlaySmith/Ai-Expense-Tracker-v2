# 🧠 SmartSpend AI - Intelligent Expense Tracker

> **AI-powered receipt scanning and expense management system**
> 
> Upload receipts → OCR extraction → Auto-categorization → Dashboard analytics

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![Tesseract](https://img.shields.io/badge/Tesseract-4285F4?style=for-the-badge&logo=google&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

---

## ✨ Features

### 🔍 Smart OCR Processing
- **Tesseract OCR** with OpenCV preprocessing
- Automatic image enhancement (grayscale, denoising, thresholding)
- Confidence scoring for extraction accuracy
- Support for multiple image formats (JPG, PNG, BMP, TIFF)

### 🧠 Intelligent Parsing
- **Amount extraction**: Automatically finds the total amount
- **Date detection**: Supports multiple date formats (DD/MM/YYYY, MM-DD-YY, etc.)
- **Merchant identification**: Extracts store/business name
- **Auto-categorization**: Smart categorization based on merchant type

### 📊 Dashboard & Analytics
- Real-time expense tracking
- Category-wise spending breakdown
- Statistics (total, average, count)
- Visual progress bars and confidence indicators

### 🛡️ Error Handling & Quality Assurance
- Comprehensive error handling with user-friendly messages
- Duplicate detection prevents double entries
- Low confidence warnings for manual verification
- Structured logging for debugging

---

## 🏗️ Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   React Frontend │────▶│  FastAPI Backend │────▶│  Tesseract OCR  │
│   (Vite + Axios) │     │  (Python 3.8+)   │     │  + OpenCV       │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌──────────────────┐
                        │   SQLite DB      │
                        │  (SQLAlchemy)    │
                        └──────────────────┘
```

### Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React 18, Vite, Axios, react-dropzone |
| **Backend** | FastAPI, Uvicorn, SQLAlchemy |
| **OCR** | Tesseract OCR, OpenCV, Pillow |
| **Database** | SQLite (PostgreSQL ready) |
| **Validation** | Pydantic |
| **Security** | python-jose, passlib (JWT ready) |

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **Node.js 16+**
- **Tesseract OCR** installed on your system

#### Install Tesseract

**Windows:**
```powershell
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Add to PATH or set in .env file
```

**macOS:**
```bash
brew install tesseract
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install tesseract-ocr
```

### Backend Setup

```bash
# Navigate to backend
cd Backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings (Tesseract path, etc.)

# Initialize database
python -c "from app.database import create_db; create_db()"

# Start server
python -m app.main
```

Backend will be available at: **http://localhost:8000**

API Documentation: **http://localhost:8000/docs**

### Frontend Setup

```bash
# Navigate to frontend
cd Frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at: **http://localhost:5173**

---

## 📁 Project Structure

```
smartspend-ai/
├── Backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI entry point
│   │   ├── database.py          # SQLAlchemy configuration
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── models.py        # User & Expense models
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── expense_schema.py # Pydantic schemas
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── expenses.py      # Expense API endpoints
│   │   │   └── auth.py          # Auth endpoints (future)
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── ocr_service.py   # Tesseract OCR
│   │   │   ├── parser_service.py  # Text parsing logic
│   │   │   └── expense_service.py # Business logic
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── error_handlers.py # Custom exceptions
│   │       └── logger.py        # Structured logging
│   ├── requirements.txt
│   ├── .env.example
│   └── Upload/                  # Temporary upload storage
│
├── Frontend/
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx
│   │   ├── index.css
│   │   ├── App.css
│   │   ├── api/
│   │   │   └── API.js           # Axios configuration
│   │   └── pages/
│   │       ├── UploadPage.jsx   # Receipt upload
│   │       ├── UploadPage.css
│   │       ├── DashboardPage.jsx # Expense dashboard
│   │       └── DashboardPage.css
│   ├── package.json
│   ├── vite.config.js
│   └── index.html
│
├── TODO.md                      # Progress tracking
├── IMPLEMENTATION_PLAN.md       # Architecture details
└── README.md                    # This file
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/health` | Health check |
| `POST` | `/api/v1/expenses/upload` | Upload receipt image |
| `GET` | `/api/v1/expenses/` | List all expenses |
| `GET` | `/api/v1/expenses/{id}` | Get specific expense |
| `PUT` | `/api/v1/expenses/{id}` | Update expense |
| `DELETE` | `/api/v1/expenses/{id}` | Delete expense |
| `GET` | `/api/v1/expenses/stats` | Get statistics |

### Example API Response

```json
{
  "success": true,
  "message": "Receipt processed successfully",
  "expense": {
    "id": 1,
    "amount": 52.99,
    "merchant": "Starbucks",
    "category": "Food & Dining",
    "date": "2024-02-13T10:30:00",
    "ocr_confidence": 85.5
  },
  "extracted_data": {
    "raw_text": "STARBUCKS\nDate: 02/13/2024\nTotal: $52.99",
    "ocr_confidence": 85.5
  },
  "warnings": []
}
```

---

## ⚙️ Configuration

Create a `.env` file in the Backend directory:

```env
# Database
DATABASE_URL=sqlite:///./smartspend.db

# Tesseract OCR
# Windows: TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
# macOS/Linux: leave empty (uses system PATH)
TESSERACT_CMD=

# Security (for future JWT implementation)
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/smartspend.log
```

---

## 🧪 Testing

### Test OCR Processing

```bash
# Using curl
curl -X POST "http://localhost:8000/api/v1/expenses/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@receipt.jpg"
```

### Test with Sample Data

```bash
# Get all expenses
curl "http://localhost:8000/api/v1/expenses/"

# Get statistics
curl "http://localhost:8000/api/v1/expenses/stats"
```

---

## 🐛 Troubleshooting

### Tesseract Not Found
```
Error: TesseractNotFoundError
```
**Solution:** Install Tesseract and set path in `.env` file

### Low OCR Confidence
- Ensure good lighting when taking photos
- Keep receipt flat and avoid shadows
- Use higher resolution images
- Check if text is clearly visible

### Database Errors
```bash
# Reset database
rm Backend/smartspend.db
python -c "from app.database import create_db; create_db()"
```

### CORS Errors
- Check `ALLOWED_ORIGINS` in `.env`
- Ensure frontend URL is included

---

## 🗺️ Roadmap

### Phase 1: MVP ✅ (Current)
- [x] OCR receipt processing
- [x] Basic expense tracking
- [x] Dashboard with statistics

### Phase 2: Enhancement
- [ ] User authentication (JWT)
- [ ] Expense editing
- [ ] Receipt image storage
- [ ] Advanced analytics charts

### Phase 3: AI Features
- [ ] ML-based categorization
- [ ] Spending predictions
- [ ] Anomaly detection
- [ ] Smart budget recommendations

### Phase 4: Scale
- [ ] Mobile app (React Native)
- [ ] Bank integration
- [ ] Multi-currency support
- [ ] Team/enterprise features

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

MIT License - feel free to use for personal or commercial projects.

---

## 🙏 Acknowledgments

- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) - Open source text recognition
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [React](https://reactjs.org/) - UI library
- [SQLAlchemy](https://www.sqlalchemy.org/) - Database toolkit

---

## 📞 Support

For issues and questions:
- Check [TODO.md](TODO.md) for known issues
- Review [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) for architecture details
- Open an issue on GitHub

---

**Built with ❤️ for smarter expense tracking**
