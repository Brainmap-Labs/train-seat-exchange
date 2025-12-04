"""
Indian Railways utilities and data
"""

from typing import Dict, List, Optional

# Major station codes
STATION_CODES: Dict[str, str] = {
    "NDLS": "New Delhi",
    "BCT": "Mumbai Central",
    "CSMT": "Chhatrapati Shivaji Maharaj Terminus",
    "HWH": "Howrah Junction",
    "SDAH": "Sealdah",
    "MAS": "Chennai Central",
    "SBC": "KSR Bengaluru",
    "SC": "Secunderabad Junction",
    "ADI": "Ahmedabad Junction",
    "PUNE": "Pune Junction",
    "JP": "Jaipur Junction",
    "LKO": "Lucknow Charbagh",
    "CNB": "Kanpur Central",
    "PRYJ": "Prayagraj Junction",
    "BPL": "Bhopal Junction",
    "NGP": "Nagpur Junction",
    "GHY": "Guwahati",
    "PNBE": "Patna Junction",
    "JAT": "Jammu Tawi",
    "ASR": "Amritsar Junction",
}

# Popular train routes
POPULAR_ROUTES = [
    ("NDLS", "HWH", ["12301", "12302"]),  # Rajdhani
    ("NDLS", "BCT", ["12951", "12952"]),  # Mumbai Rajdhani
    ("NDLS", "MAS", ["12621", "12622"]),  # Tamil Nadu Express
    ("NDLS", "SBC", ["12627", "12628"]),  # Karnataka Express
    ("HWH", "MAS", ["12839", "12840"]),  # Coromandel Express
]

# Class configurations
CLASS_CONFIG = {
    "1A": {
        "name": "First AC",
        "berths_per_coach": 24,
        "bay_size": 4,
        "has_middle": False,
    },
    "2A": {
        "name": "Second AC",
        "berths_per_coach": 48,
        "bay_size": 6,
        "has_middle": False,
    },
    "3A": {
        "name": "Third AC",
        "berths_per_coach": 64,
        "bay_size": 8,
        "has_middle": True,
    },
    "SL": {
        "name": "Sleeper",
        "berths_per_coach": 72,
        "bay_size": 8,
        "has_middle": True,
    },
    "CC": {
        "name": "Chair Car",
        "berths_per_coach": 78,
        "bay_size": 5,
        "has_middle": False,
    },
    "EC": {
        "name": "Executive Chair",
        "berths_per_coach": 56,
        "bay_size": 4,
        "has_middle": False,
    },
    "2S": {
        "name": "Second Sitting",
        "berths_per_coach": 108,
        "bay_size": 6,
        "has_middle": False,
    },
}


def get_station_name(code: str) -> Optional[str]:
    """Get station name from code"""
    return STATION_CODES.get(code.upper())


def validate_pnr(pnr: str) -> bool:
    """Validate PNR format (10 digits)"""
    return len(pnr) == 10 and pnr.isdigit()


def validate_train_number(train_no: str) -> bool:
    """Validate train number format (5 digits)"""
    return len(train_no) == 5 and train_no.isdigit()


def get_coach_prefix(class_type: str) -> str:
    """Get coach prefix for class type"""
    prefixes = {
        "1A": "H",
        "2A": "A",
        "3A": "B",
        "SL": "S",
        "CC": "C",
        "EC": "E",
        "2S": "D",
    }
    return prefixes.get(class_type, "S")


def calculate_togetherness_penalty(coaches: List[str], seats: List[int]) -> float:
    """
    Calculate penalty for scattered seats
    Returns 0 for perfect togetherness, higher for more scattered
    """
    if len(coaches) <= 1:
        return 0.0
    
    penalty = 0.0
    
    # Penalty for different coaches
    unique_coaches = set(coaches)
    penalty += (len(unique_coaches) - 1) * 30
    
    # Penalty for different bays within same coach
    coach_seats = {}
    for coach, seat in zip(coaches, seats):
        if coach not in coach_seats:
            coach_seats[coach] = []
        coach_seats[coach].append(seat)
    
    for coach, seat_list in coach_seats.items():
        bays = set((s - 1) // 8 for s in seat_list)
        penalty += (len(bays) - 1) * 10
    
    return penalty

