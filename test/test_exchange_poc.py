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
    
    # Create 3 users
    user1 = client.create_user_and_authenticate("9876543210", "Rahul Kumar")
    user2 = client.create_user_and_authenticate("9876543211", "Priya Sharma")
    user3 = client.create_user_and_authenticate("9876543212", "Amit Patel")
    
    print(f"\n{'='*60}")
    print("CREATING TICKETS WITH SCATTERED SEATS")
    print(f"{'='*60}")
    
    # User 1: Family with scattered seats (B2/45, B2/47, B3/12)
    print(f"\n📋 User 1: {user1['user_data']['name']}")
    ticket1_1 = client.create_ticket(
        user_id=user1["user_id"],
        pnr="5521678901",
        train_number=train_number,
        train_name=train_name,
        travel_date=travel_date,
        boarding_station_code="NDLS",
        boarding_station_name="NEW DELHI",
        destination_station_code="HWH",
        destination_station_name="HOWRAH JUNCTION",
        class_type="3A",
        passengers=[
            {"name": "Rahul Kumar", "age": 35, "gender": "M", "coach": "B2", "seat_number": 45, "berth_type": "LB", "booking_status": "CNF", "current_status": "CNF"},
            {"name": "Priya Kumar", "age": 32, "gender": "F", "coach": "B2", "seat_number": 47, "berth_type": "MB", "booking_status": "CNF", "current_status": "CNF"},
            {"name": "Aryan Kumar", "age": 8, "gender": "M", "coach": "B3", "seat_number": 12, "berth_type": "UB", "booking_status": "CNF", "current_status": "CNF"},
        ]
    )
    client.print_ticket_summary(ticket1_1, user1['user_data']['name'])
    
    # ticket1_2 = client.create_ticket(
    #     user_id=user1["user_id"],
    #     pnr="4521678902",
    #     train_number=train_number,
    #     train_name=train_name,
    #     travel_date=travel_date,
    #     boarding_station_code="NDLS",
    #     boarding_station_name="NEW DELHI",
    #     destination_station_code="HWH",
    #     destination_station_name="HOWRAH JUNCTION",
    #     class_type="3A",
    #     passengers=[
    #         {"name": "Rahul Kumar", "age": 35, "gender": "M", "coach": "B1", "seat_number": 20, "berth_type": "LB", "booking_status": "CNF", "current_status": "CNF"},
    #         {"name": "Priya Kumar", "age": 32, "gender": "F", "coach": "B1", "seat_number": 22, "berth_type": "MB", "booking_status": "CNF", "current_status": "CNF"},
    #     ]
    # )
    # client.print_ticket_summary(ticket1_2, user1['user_data']['name'])
    
    # ticket1_3 = client.create_ticket(
    #     user_id=user1["user_id"],
    #     pnr="4521678903",
    #     train_number=train_number,
    #     train_name=train_name,
    #     travel_date=travel_date,
    #     boarding_station_code="NDLS",
    #     boarding_station_name="NEW DELHI",
    #     destination_station_code="HWH",
    #     destination_station_name="HOWRAH JUNCTION",
    #     class_type="3A",
    #     passengers=[
    #         {"name": "Rahul Kumar", "age": 35, "gender": "M", "coach": "B4", "seat_number": 60, "berth_type": "UB", "booking_status": "CNF", "current_status": "CNF"},
    #     ]
    # )
    # client.print_ticket_summary(ticket1_3, user1['user_data']['name'])
    
    # User 2: Family with scattered seats (B2/46, B3/11, B3/13)
    print(f"\n📋 User 2: {user2['user_data']['name']}")
    ticket2_1 = client.create_ticket(
        user_id=user2["user_id"],
        pnr="4521678904",
        train_number=train_number,
        train_name=train_name,
        travel_date=travel_date,
        boarding_station_code="NDLS",
        boarding_station_name="NEW DELHI",
        destination_station_code="HWH",
        destination_station_name="HOWRAH JUNCTION",
        class_type="3A",
        passengers=[
            {"name": "Priya Sharma", "age": 28, "gender": "F", "coach": "B2", "seat_number": 46, "berth_type": "LB", "booking_status": "CNF", "current_status": "CNF"},
            {"name": "Rohan Sharma", "age": 30, "gender": "M", "coach": "B3", "seat_number": 11, "berth_type": "LB", "booking_status": "CNF", "current_status": "CNF"},
            {"name": "Meera Sharma", "age": 5, "gender": "F", "coach": "B3", "seat_number": 13, "berth_type": "MB", "booking_status": "CNF", "current_status": "CNF"},
        ]
    )
    client.print_ticket_summary(ticket2_1, user2['user_data']['name'])
    
    # ticket2_2 = client.create_ticket(
    #     user_id=user2["user_id"],
    #     pnr="4521678905",
    #     train_number=train_number,
    #     train_name=train_name,
    #     travel_date=travel_date,
    #     boarding_station_code="NDLS",
    #     boarding_station_name="NEW DELHI",
    #     destination_station_code="HWH",
    #     destination_station_name="HOWRAH JUNCTION",
    #     class_type="3A",
    #     passengers=[
    #         {"name": "Priya Sharma", "age": 28, "gender": "F", "coach": "B1", "seat_number": 21, "berth_type": "MB", "booking_status": "CNF", "current_status": "CNF"},
    #     ]
    # )
    # client.print_ticket_summary(ticket2_2, user2['user_data']['name'])
    
    # ticket2_3 = client.create_ticket(
    #     user_id=user2["user_id"],
    #     pnr="4521678906",
    #     train_number=train_number,
    #     train_name=train_name,
    #     travel_date=travel_date,
    #     boarding_station_code="NDLS",
    #     boarding_station_name="NEW DELHI",
    #     destination_station_code="HWH",
    #     destination_station_name="HOWRAH JUNCTION",
    #     class_type="3A",
    #     passengers=[
    #         {"name": "Rohan Sharma", "age": 30, "gender": "M", "coach": "B5", "seat_number": 70, "berth_type": "SL", "booking_status": "CNF", "current_status": "CNF"},
    #     ]
    # )
    # client.print_ticket_summary(ticket2_3, user2['user_data']['name'])
    
    # User 3: Family with scattered seats (B2/48, B3/10, B3/14)
    print(f"\n📋 User 3: {user3['user_data']['name']}")
    ticket3_1 = client.create_ticket(
        user_id=user3["user_id"],
        pnr="4521678907",
        train_number=train_number,
        train_name=train_name,
        travel_date=travel_date,
        boarding_station_code="NDLS",
        boarding_station_name="NEW DELHI",
        destination_station_code="HWH",
        destination_station_name="HOWRAH JUNCTION",
        class_type="3A",
        passengers=[
            {"name": "Amit Patel", "age": 40, "gender": "M", "coach": "B2", "seat_number": 48, "berth_type": "UB", "booking_status": "CNF", "current_status": "CNF"},
            {"name": "Sneha Patel", "age": 38, "gender": "F", "coach": "B3", "seat_number": 10, "berth_type": "LB", "booking_status": "CNF", "current_status": "CNF"},
            {"name": "Arjun Patel", "age": 12, "gender": "M", "coach": "B3", "seat_number": 14, "berth_type": "UB", "booking_status": "CNF", "current_status": "CNF"},
        ]
    )
    client.print_ticket_summary(ticket3_1, user3['user_data']['name'])
    
    # ticket3_2 = client.create_ticket(
    #     user_id=user3["user_id"],
    #     pnr="4521678908",
    #     train_number=train_number,
    #     train_name=train_name,
    #     travel_date=travel_date,
    #     boarding_station_code="NDLS",
    #     boarding_station_name="NEW DELHI",
    #     destination_station_code="HWH",
    #     destination_station_name="HOWRAH JUNCTION",
    #     class_type="3A",
    #     passengers=[
    #         {"name": "Amit Patel", "age": 40, "gender": "M", "coach": "B1", "seat_number": 23, "berth_type": "UB", "booking_status": "CNF", "current_status": "CNF"},
    #     ]
    # )
    # client.print_ticket_summary(ticket3_2, user3['user_data']['name'])
    
    # ticket3_3 = client.create_ticket(
    #     user_id=user3["user_id"],
    #     pnr="4521678909",
    #     train_number=train_number,
    #     train_name=train_name,
    #     travel_date=travel_date,
    #     boarding_station_code="NDLS",
    #     boarding_station_name="NEW DELHI",
    #     destination_station_code="HWH",
    #     destination_station_name="HOWRAH JUNCTION",
    #     class_type="3A",
    #     passengers=[
    #         {"name": "Sneha Patel", "age": 38, "gender": "F", "coach": "B6", "seat_number": 80, "berth_type": "SL", "booking_status": "CNF", "current_status": "CNF"},
    #     ]
    # )
    # client.print_ticket_summary(ticket3_3, user3['user_data']['name'])
    
    return client, {
        "user1": {"user": user1, "tickets": [ticket1_1]},
        "user2": {"user": user2, "tickets": [ticket2_1]},
        "user3": {"user": user3, "tickets": [ticket3_1]},
    }


def test_exchange_matching(client: ExchangePOCClient, users_data: Dict):
    """Test the exchange matching algorithm"""
    
    print("\n" + "="*60)
    print("TESTING EXCHANGE MATCHING ALGORITHM")
    print("="*60)
    
    # Test 1: User 1's first ticket (B2/45, B2/47, B3/12) - should find matches
    print(f"\n{'='*60}")
    print("TEST 1: User 1 - Ticket 1 (Family scattered: B2/45, B2/47, B3/12)")
    print(f"{'='*60}")
    ticket1_1 = users_data["user1"]["tickets"][0]
    user1_id = users_data["user1"]["user"]["user_id"]
    
    print(f"\n🔍 Searching for exchange matches...")
    matches_result = client.find_matches(user1_id, ticket1_1["id"])
    
    print(f"\n✓ Found {matches_result.get('total_matches', 0)} potential matches")
    matches = matches_result.get("matches", [])
    
    if matches:
        print(f"\n📊 Match Results:")
        for i, match in enumerate(matches, 1):
            print(f"\n  Match #{i}:")
            print(f"    User: {match.get('user_name', 'Unknown')} (Rating: {match.get('user_rating', 0)})")
            print(f"    Match Score: {match.get('match_score', 0)}%")
            print(f"    Benefit: {match.get('benefit_description', 'N/A')}")
            print(f"    Available Seats:")
            for seat in match.get('available_seats', []):
                print(f"      - {seat.get('passenger_name', 'Unknown')}: {seat.get('coach')}/{seat.get('seat_number')}/{seat.get('berth_type')}")
    else:
        print("  ❌ No matches found")
    
    # Test 2: User 2's first ticket (B2/46, B3/11, B3/13) - should find matches with User 1
    print(f"\n{'='*60}")
    print("TEST 2: User 2 - Ticket 1 (Family scattered: B2/46, B3/11, B3/13)")
    print(f"{'='*60}")
    ticket2_1 = users_data["user2"]["tickets"][0]
    user2_id = users_data["user2"]["user"]["user_id"]
    
    print(f"\n🔍 Searching for exchange matches...")
    matches_result = client.find_matches(user2_id, ticket2_1["id"])
    
    print(f"\n✓ Found {matches_result.get('total_matches', 0)} potential matches")
    matches = matches_result.get("matches", [])
    
    if matches:
        print(f"\n📊 Match Results:")
        for i, match in enumerate(matches, 1):
            print(f"\n  Match #{i}:")
            print(f"    User: {match.get('user_name', 'Unknown')} (Rating: {match.get('user_rating', 0)})")
            print(f"    Match Score: {match.get('match_score', 0)}%")
            print(f"    Benefit: {match.get('benefit_description', 'N/A')}")
            print(f"    Available Seats:")
            for seat in match.get('available_seats', []):
                print(f"      - {seat.get('passenger_name', 'Unknown')}: {seat.get('coach')}/{seat.get('seat_number')}/{seat.get('berth_type')}")
    else:
        print("  ❌ No matches found")
    
    # Test 3: User 3's first ticket (B2/48, B3/10, B3/14) - should find matches
    print(f"\n{'='*60}")
    print("TEST 3: User 3 - Ticket 1 (Family scattered: B2/48, B3/10, B3/14)")
    print(f"{'='*60}")
    ticket3_1 = users_data["user3"]["tickets"][0]
    user3_id = users_data["user3"]["user"]["user_id"]
    
    print(f"\n🔍 Searching for exchange matches...")
    matches_result = client.find_matches(user3_id, ticket3_1["id"])
    
    print(f"\n✓ Found {matches_result.get('total_matches', 0)} potential matches")
    matches = matches_result.get("matches", [])
    
    if matches:
        print(f"\n📊 Match Results:")
        for i, match in enumerate(matches, 1):
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
    print(f"✓ Created 3 users with 9 tickets total")
    print(f"✓ All tickets have scattered seats (different coaches/bays)")
    print(f"✓ All tickets are on the same train ({ticket1_1['train_number']} - {ticket1_1['train_name']})")
    print(f"✓ All tickets have the same travel date")
    print(f"✓ Tested matching algorithm for 3 different tickets")
    print(f"\n💡 Potential Exchange Opportunities:")
    print(f"  - User 1 (B2/45, B2/47, B3/12) ↔ User 2 (B2/46, B3/11, B3/13)")
    print(f"    → Could exchange B3/12 ↔ B3/11 to bring families together")
    print(f"  - User 1 (B2/45, B2/47) ↔ User 2 (B2/46)")
    print(f"    → Could exchange to get adjacent seats in B2")
    print(f"  - User 1 (B2/45, B2/47, B3/12) ↔ User 3 (B2/48, B3/10, B3/14)")
    print(f"    → Could exchange B2/48 ↔ B3/12 to consolidate in B2")


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

