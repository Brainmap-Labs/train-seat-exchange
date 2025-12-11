"""
PNR Lookup Service for Indian Railways
Fetches ticket details using PNR number from Indian Railways APIs
"""

import httpx
from typing import Dict, Any, Optional
from datetime import datetime
from app.utils.indian_railways import validate_pnr, get_station_name

class PNRService:
    """Service for fetching ticket details using PNR number"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://indianrailapi.com/api/v2"):
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = 10.0
    
    async def get_ticket_details(self, pnr: str) -> Dict[str, Any]:
        """
        Fetch ticket details from PNR number
        
        Args:
            pnr: 10-digit PNR number
            
        Returns:
            Dictionary containing ticket data in our format
        """
        if not validate_pnr(pnr):
            raise ValueError("Invalid PNR format. PNR must be 10 digits.")
        
        # Check if API key is configured
        if not self.api_key:
            raise Exception(
                "PNR API key not configured. Please set INDIAN_RAIL_API_KEY in your .env file. "
                "Get a free API key from https://indianrailapi.com or use image upload instead."
            )
        
        try:
            # Try primary API (Indian Rail API)
            data = await self._fetch_from_indian_rail_api(pnr)
            if data:
                return self._parse_pnr_response(data, pnr)
        except Exception as e:
            print(f"Primary PNR API failed: {e}")
        
        # Fallback to alternative API or return None
        try:
            data = await self._fetch_from_alternative_api(pnr)
            if data:
                return self._parse_pnr_response(data, pnr)
        except Exception as e:
            print(f"Alternative PNR API failed: {e}")
        
        raise Exception("Unable to fetch PNR details. Please try again later or use image upload.")
    
    async def _fetch_from_indian_rail_api(self, pnr: str) -> Optional[Dict[str, Any]]:
        """Fetch from Indian Rail API (indianrailapi.com)"""
        if not self.api_key:
            return None
        
        url = f"{self.base_url}/PNRCheck/apikey/{self.api_key}/PNRNumber/{pnr}"
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url)
            if response.status_code == 200:
                return response.json()
        return None
    
    async def _fetch_from_alternative_api(self, pnr: str) -> Optional[Dict[str, Any]]:
        """
        Fallback API - using a free/public endpoint
        Note: This is a placeholder. You may need to use a different service
        """
        # Example: Using a public PNR checker
        # You can integrate with services like:
        # - RailYatri API
        # - ConfirmTkt API
        # - Or scrape from official IRCTC (not recommended)
        
        # For now, return None to indicate no alternative available
        return None
    
    def _parse_pnr_response(self, data: Dict[str, Any], pnr: str) -> Dict[str, Any]:
        """
        Parse PNR API response into our ticket format
        
        This method adapts different API response formats to our standard format
        """
        # Common PNR API response structure (adapt based on actual API)
        result = {
            "pnr": pnr,
            "train_number": None,
            "train_name": None,
            "travel_date": None,
            "boarding_station": None,
            "destination_station": None,
            "class_type": None,
            "passengers": [],
            "confidence": 1.0,  # PNR data is always 100% accurate
        }
        
        # Parse based on common API response formats
        # Indian Rail API format
        if "TrainNo" in data or "trainNo" in data:
            result["train_number"] = str(data.get("TrainNo") or data.get("trainNo", ""))
            result["train_name"] = data.get("TrainName") or data.get("trainName", "").strip()
        
        # Date parsing
        date_str = data.get("JourneyDate") or data.get("journeyDate") or data.get("DateOfJourney")
        if date_str:
            try:
                # Try different date formats
                if isinstance(date_str, str):
                    # Format: "15-Jan-2025" or "2025-01-15"
                    if "-" in date_str:
                        parts = date_str.split("-")
                        if len(parts) == 3:
                            if len(parts[2]) == 4:  # YYYY format
                                result["travel_date"] = date_str
                            else:  # DD-MMM-YY format
                                result["travel_date"] = date_str
                result["travel_date"] = date_str
            except:
                pass
        
        # Station codes
        boarding_code = data.get("BoardingStationCode") or data.get("from") or data.get("From")
        dest_code = data.get("DestinationStationCode") or data.get("to") or data.get("To")
        
        if boarding_code:
            boarding_name = get_station_name(boarding_code) or data.get("BoardingStationName", "")
            result["boarding_station"] = f"{boarding_code} - {boarding_name}" if boarding_name else boarding_code
        
        if dest_code:
            dest_name = get_station_name(dest_code) or data.get("DestinationStationName", "")
            result["destination_station"] = f"{dest_code} - {dest_name}" if dest_name else dest_code
        
        # Class
        result["class_type"] = data.get("Class") or data.get("class") or data.get("JourneyClass", "")
        
        # Passengers
        passengers_data = data.get("PassengerStatus") or data.get("passengers") or data.get("Passengers", [])
        if isinstance(passengers_data, list):
            for p in passengers_data:
                # Extract passenger details with consistent keys
                name = p.get("Name") or p.get("name") or p.get("PassengerName") or "Unknown"
                age = p.get("Age") or p.get("age") or 0
                gender_str = p.get("Gender") or p.get("gender") or p.get("Sex") or "M"
                coach = str(p.get("Coach") or p.get("coach") or p.get("CurrentCoach", ""))
                seat = p.get("Seat") or p.get("seat") or p.get("SeatNumber") or p.get("BerthNo")
                berth = p.get("Berth") or p.get("berth") or p.get("BerthType", "")
                booking_status = p.get("BookingStatus") or p.get("bookingStatus") or "CNF"
                
                # Normalize gender
                gender_str = str(gender_str).upper()
                if gender_str in ["M", "MALE"]:
                    gender = "M"
                elif gender_str in ["F", "FEMALE"]:
                    gender = "F"
                else:
                    gender = "O"
                
                # Normalize age
                try:
                    age = int(age) if age else 0
                except (ValueError, TypeError):
                    age = 0
                
                if coach and seat:
                    result["passengers"].append({
                        "name": str(name).title(),  # Title case for consistency
                        "age": age,
                        "gender": gender,
                        "coach": coach.upper(),
                        "seat_number": int(seat) if isinstance(seat, (int, str)) and str(seat).isdigit() else 0,
                        "berth_type": berth.upper() if berth else "LB",
                        "booking_status": booking_status,
                        "current_status": booking_status,
                    })
        
        return result
    
    def _get_mock_pnr_data(self, pnr: str) -> Dict[str, Any]:
        """Return mock data for development/testing when API is unavailable"""
        return {
            "pnr": pnr,
            "train_number": "12301",
            "train_name": "HOWRAH RAJDHANI EXPRESS",
            "travel_date": "15-Jan-2025",
            "boarding_station": "NDLS - New Delhi",
            "destination_station": "HWH - Howrah Junction",
            "class_type": "3A",
            "passengers": [
                {
                    "name": "Rahul Kumar",
                    "age": 35,
                    "gender": "M",
                    "coach": "B2",
                    "seat_number": 45,
                    "berth_type": "LB",
                    "booking_status": "CNF",
                    "current_status": "CNF",
                },
                {
                    "name": "Priya Kumar",
                    "age": 32,
                    "gender": "F",
                    "coach": "B2",
                    "seat_number": 47,
                    "berth_type": "MB",
                    "booking_status": "CNF",
                    "current_status": "CNF",
                },
                {
                    "name": "Aryan Kumar",
                    "age": 8,
                    "gender": "M",
                    "coach": "B3",
                    "seat_number": 12,
                    "berth_type": "UB",
                    "booking_status": "CNF",
                    "current_status": "CNF",
                },
            ],
            "confidence": 1.0,
        }

