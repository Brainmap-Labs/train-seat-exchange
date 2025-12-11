# Test Clients for Tickets API

This directory contains test clients for testing the Tickets API endpoints.

## Files

- `test_tickets_client.py` - Synchronous test client using `requests` library
- `test_tickets_async.py` - Asynchronous test client using `httpx` library
- `test_exchange_poc.py` - **POC test for exchange matching logic** (3 users, 9 tickets with scattered seats)
- `testmongodb.py` - MongoDB connection test

## Prerequisites

Install required dependencies:

```bash
pip install requests httpx
```

## Usage

### Synchronous Client

```bash
# Run the synchronous test client
python test/test_tickets_client.py
```

### Asynchronous Client

```bash
# Run the asynchronous test client
python test/test_tickets_async.py
```

### Using as a Module

```python
from test.test_tickets_client import TicketsTestClient

# Create client
client = TicketsTestClient(base_url="http://localhost:8000")

# Authenticate
client.authenticate(phone="9876543210")

# Create a ticket
ticket_data = {
    "pnr": "6635006115",
    "train_number": "12069",
    "train_name": "JANSHATABDI EXP",
    "travel_date": datetime(2024, 4, 26),
    "boarding_station_code": "BSP",
    "boarding_station_name": "BILASPUR JN",
    "destination_station_code": "DURG",
    "destination_station_name": "DURG",
    "class_type": "2S",
    "quota": "GN",
    "passengers": [
        {
            "name": "Divya Singh Thak",
            "age": 25,
            "gender": "F",
            "coach": "D1",
            "seat_number": 12,
            "berth_type": "LB",
            "booking_status": "CNF",
            "current_status": "CNF"
        }
    ]
}

ticket = client.create_ticket(**ticket_data)
```

## Environment Variables

Set the API base URL if different from default:

```bash
export API_BASE_URL=http://localhost:8000
```

## Test Coverage

The test clients cover:

1. **Authentication**
   - Send OTP
   - Verify OTP
   - Get access token

2. **Ticket Upload**
   - Upload ticket image (JPEG/PNG/PDF)
   - OCR processing

3. **Ticket CRUD**
   - Create ticket
   - Get all tickets
   - Get ticket by ID
   - Delete ticket

4. **Sample Data**
   - 2S class ticket (JANSHATABDI)
   - 3A class ticket (RAJDHANI with multiple passengers)

## Exchange Matching POC

To test the exchange matching algorithm with realistic scattered seat scenarios:

```bash
# Run the POC test
python test/test_exchange_poc.py
```

This will:
1. Create 3 users (Rahul Kumar, Priya Sharma, Amit Patel)
2. Create 3 tickets for each user (9 tickets total) with scattered seats
3. All tickets are on the same train (12301 - HOWRAH RAJDHANI EXPRESS)
4. All tickets have the same travel date
5. Test the matching algorithm to find exchange opportunities

### Test Scenario

**User 1 (Rahul Kumar):**
- Ticket 1: B2/45 (LB), B2/47 (MB), B3/12 (UB) - Family scattered across coaches
- Ticket 2: B1/20 (LB), B1/22 (MB) - Family in same coach
- Ticket 3: B4/60 (UB) - Solo traveler

**User 2 (Priya Sharma):**
- Ticket 1: B2/46 (LB), B3/11 (LB), B3/13 (MB) - Family scattered
- Ticket 2: B1/21 (MB) - Solo traveler
- Ticket 3: B5/70 (SL) - Solo traveler

**User 3 (Amit Patel):**
- Ticket 1: B2/48 (UB), B3/10 (LB), B3/14 (UB) - Family scattered
- Ticket 2: B1/23 (UB) - Solo traveler
- Ticket 3: B6/80 (SL) - Solo traveler

### Expected Matches

The algorithm should find:
- User 1 ↔ User 2: Both have seats in B2 and B3, potential for exchange
- User 1 ↔ User 3: Both have seats in B2 and B3, potential for exchange
- User 2 ↔ User 3: Both have seats in B2 and B3, potential for exchange

## Notes

- The test clients use debug OTP "123456" for authentication (works when `DEBUG=True`)
- In DEBUG mode, any 6-digit OTP is accepted
- Make sure the backend server is running before executing tests
- The clients handle authentication tokens automatically
- All endpoints require authentication except `/api/auth/*`

