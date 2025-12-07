# 🚂 Train Seat Exchange (SeatSwap)

> Helping Indian Railways passengers sit together with their families through intelligent seat exchange matching.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Frontend](https://img.shields.io/badge/frontend-React%20+%20TypeScript-blue)
![Backend](https://img.shields.io/badge/backend-Python%20FastAPI-green)

## 📋 Overview

SeatSwap is a platform that helps train passengers exchange seats so families can travel together. When booking Indian Railways tickets during peak seasons, families often end up with scattered seats across different coaches. This app solves that problem by connecting passengers willing to exchange seats.

## ✨ Features

- **🔢 PNR Lookup** - Enter your PNR number to instantly fetch ticket details (Recommended - faster and more accurate)
- **📷 Ticket Upload & OCR** - Upload e-ticket images/PDFs as a fallback option
- **🔍 Smart Matching** - AI-powered algorithm to find the best exchange opportunities
- **💬 In-App Chat** - Communicate with other passengers to coordinate exchanges
- **🚃 Coach Visualization** - Visual representation of coach layouts and seat positions
- **🔔 Real-time Notifications** - Get notified of exchange requests and updates

## 🏗️ Tech Stack

### Frontend
- **React.js** + TypeScript
- **Tailwind CSS** for styling
- **Zustand** for state management
- **React Router** for navigation
- **Socket.io** for real-time features

### Backend
- **Python FastAPI** for REST APIs
- **MongoDB** with Beanie ODM
- **Firebase Auth** for phone OTP authentication
- **Hugging Face** models for OCR

## 📁 Project Structure

```
train-seat-exchange/
├── frontend/                    # React frontend application
│   ├── src/
│   │   ├── components/          # Reusable UI components
│   │   │   ├── ui/              # Base UI components (Button, Card, Input)
│   │   │   ├── layout/          # Layout components (Navbar, Footer)
│   │   │   ├── coach/           # Coach visualization components
│   │   │   └── ticket/          # Ticket display components
│   │   ├── features/            # Feature-based modules
│   │   │   ├── auth/            # Authentication (Login, OTP)
│   │   │   ├── dashboard/       # User dashboard
│   │   │   ├── tickets/         # Ticket management
│   │   │   ├── exchange/        # Seat exchange features
│   │   │   ├── chat/            # Messaging feature
│   │   │   └── profile/         # User profile
│   │   ├── services/            # API services
│   │   ├── store/               # Zustand stores
│   │   ├── types/               # TypeScript type definitions
│   │   └── hooks/               # Custom React hooks
│   └── package.json
│
├── backend/                     # Python FastAPI backend
│   ├── app/
│   │   ├── api/v1/              # API route handlers
│   │   │   ├── auth.py          # Authentication endpoints
│   │   │   ├── tickets.py       # Ticket CRUD operations
│   │   │   ├── exchange.py      # Exchange matching & requests
│   │   │   └── chat.py          # Messaging endpoints
│   │   ├── core/                # Core configurations
│   │   │   ├── config.py        # App settings
│   │   │   ├── database.py      # MongoDB connection
│   │   │   └── security.py      # JWT & auth utilities
│   │   ├── models/              # Database models (Beanie documents)
│   │   │   ├── user.py
│   │   │   ├── ticket.py
│   │   │   ├── exchange.py
│   │   │   └── message.py
│   │   └── services/            # Business logic services
│   │       ├── ocr_service.py   # Ticket OCR extraction
│   │       ├── matching_service.py  # Exchange matching algorithm
│   │       └── coach_layout.py  # Coach layout utilities
│   └── requirements.txt
│
└── BRAINSTORM_SEAT_EXCHANGE_APP.md  # Detailed brainstorming document
```

## 🚀 Getting Started

### Prerequisites

- Node.js 18+
- Python 3.10+
- MongoDB
- (Optional) Indian Railways API key for PNR lookup - Get free API key from [Indian Rail API](https://indianrailapi.com)
- (Optional) Hugging Face OCR models (automatically downloaded on first use) or Tesseract OCR for image processing fallback

#### OCR Configuration (for Image Upload Fallback)

The app supports multiple OCR methods in priority order:

1. **Hugging Face OCR Models** (Recommended - Better Accuracy)
   - Default model: `nanonets/Nanonets-OCR2-3B`
   - Alternative: `microsoft/trocr-base-printed`
   - Automatically uses GPU if available, falls back to CPU
   - No additional installation needed (uses transformers library)

2. **Tesseract OCR** (Fallback)
   - Traditional OCR engine
   - Requires system installation

**Hugging Face OCR (Recommended):**

The Hugging Face model is enabled by default and will be used automatically. The model will be downloaded on first use (may take a few minutes depending on your internet speed).

**Available Models:**
- `nanonets/Nanonets-OCR2-3B` (Default - Best accuracy, larger model ~6GB)
- `microsoft/trocr-base-printed` (Smaller, faster, good for printed text ~500MB)
- `microsoft/trocr-small-printed` (Smallest, fastest ~200MB)

To change the model, update your `.env`:

```env
HUGGINGFACE_MODEL=nanonets/Nanonets-OCR2-3B
USE_HUGGINGFACE_OCR=true
```

**Performance Notes:**
- First run will download the model (one-time, ~6GB for Nanonets-OCR2-3B)
- GPU acceleration is automatically used if available
- CPU inference works but is slower
- For production, consider using a smaller model like `microsoft/trocr-base-printed` for faster response times

**Tesseract OCR (Optional Fallback):**

If you prefer Tesseract or Hugging Face is unavailable:

**macOS:**
```bash
brew install tesseract
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

**Windows:**
1. Download the installer from [UB Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
2. Run the installer and add Tesseract to your PATH
3. Or if using Chocolatey: `choco install tesseract`

**Verify Installation:**
```bash
tesseract --version
```

**Note:** If Tesseract is installed in a non-standard location, you can configure the path in your `.env` file:
```env
TESSERACT_CMD=/path/to/tesseract
USE_HUGGINGFACE_OCR=false  # Disable Hugging Face to use Tesseract
```

#### Setting up PNR Lookup API (Recommended)

For the best experience, configure an Indian Railways PNR API:

1. Get a free API key from [Indian Rail API](https://indianrailapi.com) or similar services
2. Add to your `.env` file:
```
INDIAN_RAIL_API_KEY=your_api_key_here
```

**Note:** The app works without the API key, but PNR lookup will be unavailable. You can still use image upload as a fallback.

#### Ticket Text Parsing Methods

The app supports two methods for parsing ticket text after OCR:

1. **Regex Parsing** (Default - Fast, No API costs)
   - Uses pattern matching to extract ticket information
   - Fast and works offline
   - Handles common ticket formats

2. **OpenAI Parsing** (Optional - Better accuracy for complex formats)
   - Uses GPT-4o-mini or other OpenAI models
   - Better at handling OCR errors and unusual formats
   - Requires OpenAI API key

To enable OpenAI parsing, add to your `.env` file:
```env
USE_OPENAI_PARSING=true
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini  # or gpt-4o, gpt-3.5-turbo, etc.
```

**Note:** If OpenAI parsing fails or returns low confidence, the system automatically falls back to regex parsing.

### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your settings

# Run the server
python run.py
```

Backend will be available at `http://localhost:8000`

### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend will be available at `http://localhost:3000`

## 📚 API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/send-otp` | POST | Send OTP to phone |
| `/api/auth/verify-otp` | POST | Verify OTP & get token |
| `/api/tickets` | GET/POST | List/Create tickets |
| `/api/tickets/lookup-pnr` | POST | Fetch ticket details using PNR number (Recommended) |
| `/api/tickets/upload` | POST | Upload ticket image for OCR (Fallback) |
| `/api/exchange/find-matches/{ticket_id}` | POST | Find exchange matches |
| `/api/exchange/request` | POST | Send exchange request |
| `/api/chat/{exchange_id}` | GET/POST | Chat messages |

## 🎨 Design System

### Colors

- **Railway Blue**: `#1a237e` - Primary brand color
- **Primary Yellow**: `#f9a825` - Accent color (inspired by Indian Railways)
- **Berth Colors**:
  - Lower: `#4caf50` (Green)
  - Middle: `#ff9800` (Orange)
  - Upper: `#f44336` (Red)
  - Side: `#9c27b0` (Purple)

### Fonts

- **Display**: Outfit (headings)
- **Body**: Plus Jakarta Sans

## 🧮 Matching Algorithm

The exchange matching algorithm considers:

1. **Same Coach** (+30 points) - Passengers in the same coach
2. **Same Bay** (+20 points) - Seats within the same bay (group of 8)
3. **Adjacent Seats** (+15 points) - Directly next to each other
4. **Berth Improvement** (+10 points) - Better berth type available
5. **User Rating** - Prefer highly-rated users

## 🔒 Security

- Phone OTP verification via Firebase
- JWT tokens for API authentication
- Rate limiting on sensitive endpoints
- PNR numbers are never shared publicly

## 📱 Screenshots

*Coming soon*

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## ⚠️ Disclaimer

This application is not affiliated with Indian Railways or IRCTC. It is an independent platform to help passengers coordinate seat exchanges among themselves.

---

Built with ❤️ for Indian train travelers

