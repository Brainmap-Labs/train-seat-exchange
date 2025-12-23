"""
POC Test Client for Exchange Matching Logic
Creates 3 users with scattered tickets and tests the matching algorithm
Usage: python test/test_exchange_poc.py
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List
import os

# Configuration
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_PREFIX = "/api"


def berth_from_seat(seat_number: int) -> str:
    """Return berth type based on Indian Railways seat number modulo 8."""
    mod = seat_number % 8
    if mod == 1 or mod == 4:
        return "LB"
    if mod == 2 or mod == 5:
        return "MB"
    if mod == 3 or mod == 6:
        return "UB"
    if mod == 7:
        return "SL"
    return "SU"

class ExchangePOCClient:
    """Test client for Exchange POC"""
    
    def __init__(self, base_url: str = BASE_URL, api_prefix: str = API_PREFIX):
        self.base_url = base_url
        self.api_prefix = api_prefix
        self.users = []
        self.tokens = {}
        self.tickets = {}
        self.session = requests.Session()
    
    def _get_headers(self, user_id: str) -> Dict[str, str]:
        """Get headers with authentication token for a user"""
        headers = {"Content-Type": "application/json"}
        if user_id in self.tokens:
            headers["Authorization"] = f"Bearer {self.tokens[user_id]}"
        return headers
    
    def create_user_and_authenticate(self, phone: str, name: str) -> Dict[str, Any]:
        """Create a user and authenticate"""
        print(f"\n{'='*60}")
        print(f"Creating user: {name} ({phone})")
        print(f"{'='*60}")
        
        # Step 1: Send OTP
        send_otp_url = f"{self.base_url}{self.api_prefix}/auth/send-otp"
        response = self.session.post(send_otp_url, json={"phone": phone})
        response.raise_for_status()
        otp_data = response.json()
        print(f"✓ OTP sent (use any 6-digit OTP in DEBUG mode)")
        
        # Step 2: Verify OTP (use any 6-digit OTP in DEBUG mode)
        verify_otp_url = f"{self.base_url}{self.api_prefix}/auth/verify-otp"
        otp = "123456"  # Any OTP works in DEBUG mode
        
        response = self.session.post(
            verify_otp_url,
            json={"phone": phone, "otp": otp}
        )
        response.raise_for_status()
        token_data = response.json()
        
        user_id = token_data["user"]["id"]
        self.tokens[user_id] = token_data["access_token"]
        self.users.append({
            "id": user_id,
            "phone": phone,
            "name": name,
            "token": token_data["access_token"]
        })
        
        print(f"✓ User authenticated: {token_data['user']['name']} (ID: {user_id})")
        return {"user_id": user_id, "token": token_data["access_token"], "user_data": token_data["user"]}
    
    def create_ticket(
        self,
        user_id: str,
        pnr: str,
        train_number: str,
        train_name: str,
        travel_date: datetime,
        boarding_station_code: str,
        boarding_station_name: str,
        destination_station_code: str,
        destination_station_name: str,
        class_type: str,
        passengers: List[Dict],
        quota: str = "GN"
    ) -> Dict[str, Any]:
        """Create a ticket for a user"""
        url = f"{self.base_url}{self.api_prefix}/tickets"
        
        payload = {
            "pnr": pnr,
            "train_number": train_number,
            "train_name": train_name,
            "travel_date": travel_date.isoformat(),
            "boarding_station_code": boarding_station_code,
            "boarding_station_name": boarding_station_name,
            "destination_station_code": destination_station_code,
            "destination_station_name": destination_station_name,
            "class_type": class_type,
            "quota": quota,
            "passengers": passengers
        }
        
        response = self.session.post(
            url,
            json=payload,
            headers=self._get_headers(user_id)
        )
        response.raise_for_status()
        ticket_data = response.json()
        
        if user_id not in self.tickets:
            self.tickets[user_id] = []
        self.tickets[user_id].append(ticket_data)
        
        return ticket_data
    
    def find_matches(self, user_id: str, ticket_id: str) -> List[Dict[str, Any]]:
        """Find exchange matches for a ticket"""
        url = f"{self.base_url}{self.api_prefix}/exchange/find-matches/{ticket_id}"
        
        response = self.session.post(
            url,
            json={},  # No preferences for now
            headers=self._get_headers(user_id)
        )
        response.raise_for_status()
        return response.json()
    
    def print_ticket_summary(self, ticket: Dict, user_name: str):
        """Print a summary of a ticket"""
        print(f"\n  Ticket: {ticket['pnr']}")
        print(f"  Train: {ticket['train_number']} - {ticket['train_name']}")
        print(f"  Route: {ticket['boarding_station']['name']} → {ticket['destination_station']['name']}")
        print(f"  Date: {ticket['travel_date']}")
        print(f"  Class: {ticket['class_type']}")
        print(f"  Passengers ({len(ticket['passengers'])}):")
        for p in ticket['passengers']:
            print(f"    - {p['name']}: {p['coach']}/{p['seat_number']}/{p['berth_type']}")
        print(f"  Scattered: {ticket.get('is_scattered', False)}")


def create_scattered_tickets():
    """Create test scenario with scattered seats"""
    
    # Common travel date (30 days from now)
    travel_date = datetime.now() + timedelta(days=30)
    travel_date = travel_date.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # All tickets on the same train for matching
    train_number = "12301"
    train_name = "HOWRAH RAJDHANI EXPRESS"

    client = ExchangePOCClient()

    print("\n" + "="*60)
    print("EXCHANGE MATCHING POC - SETUP")
    print("="*60)

    print(f"\n{'='*60}")
    print("CREATING 10 USERS WITH SINGLE TICKETS (1-5 PASSENGERS)")
    print(f"{'='*60}")

    users_map = {}
    coaches = ["B1", "B2", "B3", "B4", "B5"]

    # Create 10 users, each with 1-5 passengers (tickets)
    for i in range(10):
        phone = f"98765432{10 + i}"
        name = f"User {i+1}"
        user = client.create_user_and_authenticate(phone, name)

        # Determine number of passengers for this user's ticket (1..5)
        passenger_count = (i % 5) + 1

        passengers = []
        for j in range(passenger_count):
            coach = coaches[j % len(coaches)]
            seat_number = 10 * (j + 1) + (i % 9)
            berth = berth_from_seat(seat_number)
            passengers.append({
                "name": f"Passenger {i+1}-{j+1}",
                "age": 20 + ((i + j) % 50),
                "gender": "M" if (j % 2 == 0) else "F",
                "coach": coach,
                "seat_number": seat_number,
                "berth_type": berth,
                "booking_status": "CNF",
                "current_status": "CNF",
            })

        pnr = f"PNR{1000 + i}"
        ticket = client.create_ticket(
            user_id=user["user_id"],
            pnr=pnr,
            train_number=train_number,
            train_name=train_name,
            travel_date=travel_date,
            boarding_station_code="NDLS",
            boarding_station_name="NEW DELHI",
            destination_station_code="HWH",
            destination_station_name="HOWRAH JUNCTION",
            class_type="3A",
            passengers=passengers,
        )

        client.print_ticket_summary(ticket, user['user_data']['name'])

        users_map[f"user{i+1}"] = {"user": user, "tickets": [ticket]}
    
    return client, users_map


def test_exchange_matching(client: ExchangePOCClient, users_data: Dict):
    """Test the exchange matching algorithm"""
    
    print("\n" + "="*60)
    print("TESTING EXCHANGE MATCHING ALGORITHM")
    print("="*60)
    
    print("\n" + "="*60)
    print("TESTING EXCHANGE MATCHING ALGORITHM FOR ALL USERS")
    print("="*60)

    for idx, user_key in enumerate(sorted(users_data.keys()), start=1):
        entry = users_data[user_key]
        ticket = entry["tickets"][0]
        user_id = entry["user"]["user_id"]

        print(f"\n{'='*60}")
        print(f"TEST {idx}: {entry['user']['user_data']['name']} - Ticket {ticket.get('pnr', ticket.get('id'))}")
        print(f"{'='*60}")

        print(f"\n🔍 Searching for exchange matches...")
        matches_result = client.find_matches(user_id, ticket["id"])

        total = matches_result.get('total_matches', 0)
        print(f"\n✓ Found {total} potential matches")
        matches = matches_result.get("matches", [])

        if matches:
            print(f"\n📊 Top Matches (up to 5):")
            for i, match in enumerate(matches[:5], 1):
                print(f"\n  Match #{i}:")
                print(f"    User: {match.get('user_name', 'Unknown')} (Rating: {match.get('user_rating', 0)})")
                print(f"    Match Score: {match.get('match_score', 0)}%")
                print(f"    Benefit: {match.get('benefit_description', 'N/A')}")
                print(f"    Available Seats:")
                for seat in match.get('available_seats', []):
                    print(f"      - {seat.get('passenger_name', 'Unknown')}: {seat.get('coach')}/{seat.get('seat_number')}/{seat.get('berth_type')}")
        else:
            print("  ❌ No matches found")

    # Summary
    print(f"\n{'='*60}")
    print("POC SUMMARY")
    print(f"{'='*60}")
    print(f"✓ Created {len(users_data)} users each with one ticket")
    print(f"✓ Tickets have 1-5 passengers each")
    sample_ticket = next(iter(users_data.values()))['tickets'][0]
    print(f"✓ All tickets are on the same train ({sample_ticket['train_number']} - {sample_ticket['train_name']})")
    print(f"\n💡 Tip: Review match details above to spot good exchange opportunities.")


def main():
    """Main function to run the POC"""
    try:
        # Step 1: Create users and tickets
        client, users_data = create_scattered_tickets()
        
        # Step 2: Test exchange matching
        test_exchange_matching(client, users_data)
        
        print(f"\n{'='*60}")
        print("✅ POC COMPLETED SUCCESSFULLY!")
        print(f"{'='*60}\n")
        
    except requests.exceptions.HTTPError as e:
        print(f"\n❌ HTTP Error: {e}")
        if e.response is not None:
            print(f"  Status: {e.response.status_code}")
            print(f"  Response: {e.response.text}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

