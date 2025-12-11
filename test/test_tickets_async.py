"""
Async test client for Tickets API endpoints using httpx
Usage: python -m pytest test/test_tickets_async.py -v
   or: python test/test_tickets_async.py
"""

import asyncio
import httpx
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import os
from pathlib import Path

# Configuration
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_PREFIX = "/api"


class AsyncTicketsTestClient:
    """Async test client for Tickets API using httpx"""
    
    def __init__(self, base_url: str = BASE_URL, api_prefix: str = API_PREFIX):
        self.base_url = base_url
        self.api_prefix = api_prefix
        self.token: Optional[str] = None
        self.user_id: Optional[str] = None
        self.client = httpx.AsyncClient(base_url=base_url, timeout=30.0)
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with authentication token"""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    async def authenticate(self, phone: str = "9876543210", use_debug_otp: bool = True) -> Dict[str, Any]:
        """
        Authenticate and get access token
        
        Args:
            phone: Phone number (10 digits)
            use_debug_otp: If True, use "123456" as OTP (works in DEBUG mode)
        
        Returns:
            Authentication response with token
        """
        # Step 1: Send OTP
        send_otp_url = f"{self.api_prefix}/auth/send-otp"
        response = await self.client.post(
            send_otp_url,
            json={"phone": phone}
        )
        response.raise_for_status()
        otp_data = response.json()
        
        # Step 2: Verify OTP
        verify_otp_url = f"{self.api_prefix}/auth/verify-otp"
        otp = "123456" if use_debug_otp else otp_data.get("debug_otp", "123456")
        
        response = await self.client.post(
            verify_otp_url,
            json={"phone": phone, "otp": otp}
        )
        response.raise_for_status()
        token_data = response.json()
        
        self.token = token_data["access_token"]
        self.user_id = token_data["user"]["id"]
        
        print(f"✓ Authenticated as user: {token_data['user']['name']} (ID: {self.user_id})")
        return token_data
    
    async def upload_ticket_image(
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
        url = f"{self.api_prefix}/tickets/upload"
        
        with open(image_path, "rb") as f:
            files = {"file": (os.path.basename(image_path), f, content_type)}
            headers = {}
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"
            
            response = await self.client.post(url, files=files, headers=headers)
            response.raise_for_status()
            return response.json()
    
    async def create_ticket(
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
        url = f"{self.api_prefix}/tickets"
        
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
        
        response = await self.client.post(
            url,
            json=payload,
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    async def get_all_tickets(self) -> list:
        """Get all tickets for current user"""
        url = f"{self.api_prefix}/tickets"
        
        response = await self.client.get(
            url,
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    async def get_ticket(self, ticket_id: str) -> Dict[str, Any]:
        """Get ticket by ID"""
        url = f"{self.api_prefix}/tickets/{ticket_id}"
        
        response = await self.client.get(
            url,
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    async def delete_ticket(self, ticket_id: str) -> Dict[str, Any]:
        """Delete a ticket"""
        url = f"{self.api_prefix}/tickets/{ticket_id}"
        
        response = await self.client.delete(
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
                "coach": "D1",
                "seat_number": 12,
                "berth_type": "LB",
                "booking_status": "CNF",
                "current_status": "CNF"
            }
        ]
    }


async def run_async_tests():
    """Run all ticket endpoint tests asynchronously"""
    print("=" * 60)
    print("Tickets API Async Test Client")
    print("=" * 60)
    print()
    
    client = AsyncTicketsTestClient()
    
    try:
        # Test 1: Authentication
        print("Test 1: Authentication")
        print("-" * 60)
        auth_data = await client.authenticate()
        print()
        
        # Test 2: Create Ticket (2S class)
        print("Test 2: Create Ticket (2S class - JANSHATABDI)")
        print("-" * 60)
        ticket_data_2s = create_sample_ticket_data()
        created_ticket_2s = await client.create_ticket(**ticket_data_2s)
        print(f"✓ Created ticket: {created_ticket_2s['pnr']}")
        print(f"  Train: {created_ticket_2s['train_name']}")
        print(f"  From: {created_ticket_2s['boarding_station']['name']} → {created_ticket_2s['destination_station']['name']}")
        print(f"  Passengers: {len(created_ticket_2s['passengers'])}")
        print(f"  Is Scattered: {created_ticket_2s['is_scattered']}")
        ticket_id_2s = created_ticket_2s['id']
        print()
        
        # Test 3: Get All Tickets
        print("Test 3: Get All Tickets")
        print("-" * 60)
        all_tickets = await client.get_all_tickets()
        print(f"✓ Retrieved {len(all_tickets)} tickets")
        for ticket in all_tickets:
            print(f"  - {ticket['pnr']}: {ticket['train_name']} ({ticket['class_type']})")
        print()
        
        # Test 4: Get Ticket by ID
        print("Test 4: Get Ticket by ID")
        print("-" * 60)
        ticket = await client.get_ticket(ticket_id_2s)
        print(f"✓ Retrieved ticket: {ticket['pnr']}")
        print(f"  Train: {ticket['train_name']}")
        print()
        
        # Test 5: Delete Ticket
        print("Test 5: Delete Ticket")
        print("-" * 60)
        delete_result = await client.delete_ticket(ticket_id_2s)
        print(f"✓ {delete_result['message']}")
        print()
        
        print("=" * 60)
        print("All async tests completed!")
        print("=" * 60)
        
    except httpx.HTTPStatusError as e:
        print(f"✗ HTTP Error: {e}")
        if e.response is not None:
            print(f"  Status: {e.response.status_code}")
            print(f"  Response: {e.response.text}")
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(run_async_tests())

