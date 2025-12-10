"""
Test client for Tickets API endpoints
Usage: python test/test_tickets_client.py
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import os
from pathlib import Path

# Configuration
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_PREFIX = "/api"

class TicketsTestClient:
    """Test client for Tickets API"""
    
    def __init__(self, base_url: str = BASE_URL, api_prefix: str = API_PREFIX):
        self.base_url = base_url
        self.api_prefix = api_prefix
        self.token: Optional[str] = None
        self.user_id: Optional[str] = None
        self.session = requests.Session()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with authentication token"""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def authenticate(self, phone: str = "9876543210", use_debug_otp: bool = True) -> Dict[str, Any]:
        """
        Authenticate and get access token
        
        Args:
            phone: Phone number (10 digits)
            use_debug_otp: If True, use "123456" as OTP (works in DEBUG mode)
        
        Returns:
            Authentication response with token
        """
        # Step 1: Send OTP
        send_otp_url = f"{self.base_url}{self.api_prefix}/auth/send-otp"
        response = requests.post(
            send_otp_url,
            json={"phone": phone}
        )
        response.raise_for_status()
        otp_data = response.json()
        
        # Step 2: Verify OTP
        verify_otp_url = f"{self.base_url}{self.api_prefix}/auth/verify-otp"
        otp = "123456" if use_debug_otp else otp_data.get("debug_otp", "123456")
        
        response = requests.post(
            verify_otp_url,
            json={"phone": phone, "otp": otp}
        )
        response.raise_for_status()
        token_data = response.json()
        
        self.token = token_data["access_token"]
        self.user_id = token_data["user"]["id"]
        
        print(f"✓ Authenticated as user: {token_data['user']['name']} (ID: {self.user_id})")
        return token_data
    
    def upload_ticket_image(
        self, 
        image_path: str,
        content_type: str = "image/jpeg"
    ) -> Dict[str, Any]:
        """
        Upload ticket image for OCR processing
        
        Args:
            image_path: Path to image file
            content_type: MIME type of the file
        
        Returns:
            OCR extraction results
        """
        url = f"{self.base_url}{self.api_prefix}/tickets/upload"
        
        with open(image_path, "rb") as f:
            files = {"file": (os.path.basename(image_path), f, content_type)}
            headers = {}
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"
            
            response = self.session.post(url, files=files, headers=headers)
            response.raise_for_status()
            return response.json()
    
    def create_ticket(
        self,
        pnr: str,
        train_number: str,
        train_name: str,
        travel_date: datetime,
        boarding_station_code: str,
        boarding_station_name: str,
        destination_station_code: str,
        destination_station_name: str,
        class_type: str,
        passengers: list,
        quota: str = "GN"
    ) -> Dict[str, Any]:
        """
        Create a new ticket
        
        Args:
            pnr: PNR number
            train_number: Train number
            train_name: Train name
            travel_date: Travel date (datetime)
            boarding_station_code: Boarding station code
            boarding_station_name: Boarding station name
            destination_station_code: Destination station code
            destination_station_name: Destination station name
            class_type: Class type (SL, 3A, 2A, 1A, CC, EC, 2S)
            passengers: List of passenger dictionaries
            quota: Quota (default: GN)
        
        Returns:
            Created ticket data
        """
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
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def get_all_tickets(self) -> list:
        """Get all tickets for current user"""
        url = f"{self.base_url}{self.api_prefix}/tickets"
        
        response = self.session.get(
            url,
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def get_ticket(self, ticket_id: str) -> Dict[str, Any]:
        """Get ticket by ID"""
        url = f"{self.base_url}{self.api_prefix}/tickets/{ticket_id}"
        
        response = self.session.get(
            url,
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def delete_ticket(self, ticket_id: str) -> Dict[str, Any]:
        """Delete a ticket"""
        url = f"{self.base_url}{self.api_prefix}/tickets/{ticket_id}"
        
        response = self.session.delete(
            url,
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()


def create_sample_ticket_data() -> Dict[str, Any]:
    """Create sample ticket data based on the provided format"""
    return {
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
                "coach": "D1",  # Note: 2S class may not have coach/seat in ticket
                "seat_number": 12,
                "berth_type": "LB",  # Note: 2S doesn't have berths, but required by model
                "booking_status": "CNF",
                "current_status": "CNF"
            }
        ]
    }


def create_sample_3a_ticket_data() -> Dict[str, Any]:
    """Create sample 3A class ticket data"""
    travel_date = datetime.now() + timedelta(days=30)
    
    return {
        "pnr": "4521678901",
        "train_number": "12301",
        "train_name": "HOWRAH RAJDHANI EXPRESS",
        "travel_date": travel_date,
        "boarding_station_code": "NDLS",
        "boarding_station_name": "NEW DELHI",
        "destination_station_code": "HWH",
        "destination_station_name": "HOWRAH JUNCTION",
        "class_type": "3A",
        "quota": "GN",
        "passengers": [
            {
                "name": "RAHUL KUMAR",
                "age": 35,
                "gender": "M",
                "coach": "B2",
                "seat_number": 45,
                "berth_type": "LB",
                "booking_status": "CNF",
                "current_status": "CNF"
            },
            {
                "name": "PRIYA KUMAR",
                "age": 32,
                "gender": "F",
                "coach": "B2",
                "seat_number": 47,
                "berth_type": "MB",
                "booking_status": "CNF",
                "current_status": "CNF"
            },
            {
                "name": "ARYAN KUMAR",
                "age": 8,
                "gender": "M",
                "coach": "B3",
                "seat_number": 12,
                "berth_type": "UB",
                "booking_status": "CNF",
                "current_status": "CNF"
            }
        ]
    }


def run_tests():
    """Run all ticket endpoint tests"""
    print("=" * 60)
    print("Tickets API Test Client")
    print("=" * 60)
    print()
    
    client = TicketsTestClient()
    
    try:
        # Test 1: Authentication
        print("Test 1: Authentication")
        print("-" * 60)
        auth_data = client.authenticate()
        print()
        
        # # Test 2: Create Ticket (2S class)
        # print("Test 2: Create Ticket (2S class - JANSHATABDI)")
        # print("-" * 60)
        # ticket_data_2s = create_sample_ticket_data()
        # created_ticket_2s = client.create_ticket(**ticket_data_2s)
        # print(f"✓ Created ticket: {created_ticket_2s['pnr']}")
        # print(f"  Train: {created_ticket_2s['train_name']}")
        # print(f"  From: {created_ticket_2s['boarding_station']['name']} → {created_ticket_2s['destination_station']['name']}")
        # print(f"  Passengers: {len(created_ticket_2s['passengers'])}")
        # print(f"  Is Scattered: {created_ticket_2s['is_scattered']}")
        # ticket_id_2s = created_ticket_2s['id']
        # print()
        
        # # Test 3: Create Ticket (3A class with multiple passengers)
        # print("Test 3: Create Ticket (3A class - RAJDHANI)")
        # print("-" * 60)
        # ticket_data_3a = create_sample_3a_ticket_data()
        # created_ticket_3a = client.create_ticket(**ticket_data_3a)
        # print(f"✓ Created ticket: {created_ticket_3a['pnr']}")
        # print(f"  Train: {created_ticket_3a['train_name']}")
        # print(f"  From: {created_ticket_3a['boarding_station']['name']} → {created_ticket_3a['destination_station']['name']}")
        # print(f"  Passengers: {len(created_ticket_3a['passengers'])}")
        # print(f"  Is Scattered: {created_ticket_3a['is_scattered']}")
        # ticket_id_3a = created_ticket_3a['id']
        # print()
        
        # # Test 4: Get All Tickets
        # print("Test 4: Get All Tickets")
        # print("-" * 60)
        # all_tickets = client.get_all_tickets()
        # print(f"✓ Retrieved {len(all_tickets)} tickets")
        # for ticket in all_tickets:
        #     print(f"  - {ticket['pnr']}: {ticket['train_name']} ({ticket['class_type']})")
        # print()
        
        # # Test 5: Get Ticket by ID
        # print("Test 5: Get Ticket by ID")
        # print("-" * 60)
        # ticket = client.get_ticket(ticket_id_3a)
        # print(f"✓ Retrieved ticket: {ticket['pnr']}")
        # print(f"  Train: {ticket['train_name']}")
        # print(f"  Passengers:")
        # for p in ticket['passengers']:
        #     print(f"    - {p['name']} ({p['age']}): {p['coach']}/{p['seat_number']}/{p['berth_type']}")
        # print()
        
        # Test 6: Upload Ticket Image (if image exists)
        print("Test 6: Upload Ticket Image")
        print("-" * 60)
        test_image_path = Path(__file__).parent / "ticket2.jpeg"
        print('#image path:', test_image_path)
        if test_image_path.exists():
            try:
                upload_result = client.upload_ticket_image(str(test_image_path))
                print(f"✓ Uploaded and processed ticket image")
                print(f"  Confidence: {upload_result.get('confidence', 0):.2%}")
                print('data in the image:', upload_result)
                if 'data' in upload_result:
                    data = upload_result['data']
                    if data.get('pnr'):
                        print(f"  Extracted PNR: {data['pnr']}")
                    if data.get('train_number'):
                        print(f"  Extracted Train: {data['train_number']} - {data.get('train_name', '')}")
            except Exception as e:
                print(f"✗ Upload failed: {e}")
        else:
            print(f"⚠ Test image not found at {test_image_path}")
            print("  Skipping upload test")
        print()
        
        # # Test 7: Delete Ticket
        # print("Test 7: Delete Ticket")
        # print("-" * 60)
        # delete_result = client.delete_ticket(ticket_id_2s)
        # print(f"✓ {delete_result['message']}")
        # print()
        
        # # Test 8: Verify Deletion
        # print("Test 8: Verify Deletion")
        # print("-" * 60)
        # try:
        #     client.get_ticket(ticket_id_2s)
        #     print("✗ Ticket still exists (unexpected)")
        # except requests.exceptions.HTTPError as e:
        #     if e.response.status_code == 404:
        #         print("✓ Ticket successfully deleted (404 as expected)")
        #     else:
        #         print(f"✗ Unexpected error: {e}")
        # print()
        
        # print("=" * 60)
        # print("All tests completed!")
        # print("=" * 60)
        
    except requests.exceptions.HTTPError as e:
        print(f"✗ HTTP Error: {e}")
        if e.response is not None:
            print(f"  Status: {e.response.status_code}")
            print(f"  Response: {e.response.text}")
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_tests()

