# 🚂 Train Seat Exchange (SeatSwap)

> Helping Indian Railways passengers sit together with their families through intelligent seat exchange matching.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Frontend](https://img.shields.io/badge/frontend-React%20+%20TypeScript-blue)
![Backend](https://img.shields.io/badge/backend-Python%20FastAPI-green)

## 📋 Overview

SeatSwap is a platform that helps train passengers exchange seats so families can travel together. When booking Indian Railways tickets during peak seasons, families often end up with scattered seats across different coaches. This app solves that problem by connecting passengers willing to exchange seats.

## ✨ Features

- **📷 Ticket Upload & OCR** - Upload e-ticket images/PDFs and automatically extract details
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
- (Optional) Tesseract OCR for local OCR processing

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
| `/api/tickets/upload` | POST | Upload ticket image for OCR |
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

