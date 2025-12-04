from typing import List, Dict, Literal
from dataclasses import dataclass

BerthType = Literal["LB", "MB", "UB", "SL", "SU"]
ClassType = Literal["SL", "3A", "2A", "1A", "CC", "EC"]

@dataclass
class BerthInfo:
    number: int
    berth_type: BerthType
    bay_number: int
    position: str  # 'main' or 'side'

class CoachLayoutService:
    """Service for Indian Railways coach layouts and berth calculations"""
    
    # Coach configurations
    COACH_CONFIGS = {
        "SL": {"total_berths": 72, "bay_size": 8, "has_middle": True},
        "3A": {"total_berths": 64, "bay_size": 8, "has_middle": True},
        "2A": {"total_berths": 48, "bay_size": 6, "has_middle": False},
        "1A": {"total_berths": 24, "bay_size": 4, "has_middle": False},
        "CC": {"total_berths": 78, "bay_size": 5, "has_middle": False},
    }
    
    def get_berth_type(self, seat_number: int, class_type: ClassType) -> BerthType:
        """Get the berth type for a given seat number"""
        config = self.COACH_CONFIGS.get(class_type)
        if not config:
            return "LB"  # Default
        
        bay_size = config["bay_size"]
        has_middle = config["has_middle"]
        
        pos_in_bay = seat_number % bay_size or bay_size
        
        if class_type in ["SL", "3A"]:
            # 8 berths per bay: 1-LB, 2-MB, 3-UB, 4-LB, 5-MB, 6-UB, 7-SL, 8-SU
            berth_map = {1: "LB", 2: "MB", 3: "UB", 4: "LB", 5: "MB", 6: "UB", 7: "SL", 8: "SU"}
            return berth_map.get(pos_in_bay, "LB")
        
        elif class_type == "2A":
            # 6 berths per bay: 1-LB, 2-UB, 3-LB, 4-UB, 5-SL, 6-SU
            berth_map = {1: "LB", 2: "UB", 3: "LB", 4: "UB", 5: "SL", 6: "SU"}
            return berth_map.get(pos_in_bay, "LB")
        
        elif class_type == "1A":
            # 4 berths per coupe: 1-LB, 2-UB, 3-LB, 4-UB
            berth_map = {1: "LB", 2: "UB", 3: "LB", 4: "UB"}
            return berth_map.get(pos_in_bay, "LB")
        
        return "LB"
    
    def get_bay_number(self, seat_number: int, class_type: ClassType) -> int:
        """Get the bay number for a given seat"""
        config = self.COACH_CONFIGS.get(class_type, {"bay_size": 8})
        return (seat_number - 1) // config["bay_size"] + 1
    
    def get_bay_seats(self, bay_number: int, class_type: ClassType) -> List[int]:
        """Get all seat numbers in a specific bay"""
        config = self.COACH_CONFIGS.get(class_type, {"bay_size": 8, "total_berths": 72})
        bay_size = config["bay_size"]
        start = (bay_number - 1) * bay_size + 1
        end = min(start + bay_size, config["total_berths"] + 1)
        return list(range(start, end))
    
    def are_seats_adjacent(self, seat1: int, seat2: int, class_type: ClassType) -> bool:
        """Check if two seats are adjacent (useful for families)"""
        bay1 = self.get_bay_number(seat1, class_type)
        bay2 = self.get_bay_number(seat2, class_type)
        
        # Must be in same bay
        if bay1 != bay2:
            return False
        
        # Check if they share a vertical column (e.g., 1,4 or 2,5 or 3,6)
        config = self.COACH_CONFIGS.get(class_type, {"bay_size": 8})
        pos1 = seat1 % config["bay_size"] or config["bay_size"]
        pos2 = seat2 % config["bay_size"] or config["bay_size"]
        
        if class_type in ["SL", "3A"]:
            # Adjacent pairs: (1,4), (2,5), (3,6), (7,8)
            adjacent_pairs = [(1, 4), (2, 5), (3, 6), (7, 8)]
            return (pos1, pos2) in adjacent_pairs or (pos2, pos1) in adjacent_pairs
        
        return abs(pos1 - pos2) <= 1
    
    def get_lower_berths_in_bay(self, bay_number: int, class_type: ClassType) -> List[int]:
        """Get all lower berth numbers in a bay"""
        bay_seats = self.get_bay_seats(bay_number, class_type)
        return [s for s in bay_seats if self.get_berth_type(s, class_type) in ["LB", "SL"]]
    
    def generate_coach_layout(self, class_type: ClassType) -> Dict:
        """Generate complete coach layout for visualization"""
        config = self.COACH_CONFIGS.get(class_type, {"total_berths": 72, "bay_size": 8})
        total_berths = config["total_berths"]
        bay_size = config["bay_size"]
        total_bays = (total_berths + bay_size - 1) // bay_size
        
        layout = {
            "class_type": class_type,
            "total_berths": total_berths,
            "bay_size": bay_size,
            "bays": []
        }
        
        for bay_num in range(1, total_bays + 1):
            bay = {
                "bay_number": bay_num,
                "berths": []
            }
            
            for seat in self.get_bay_seats(bay_num, class_type):
                if seat <= total_berths:
                    berth_type = self.get_berth_type(seat, class_type)
                    bay["berths"].append({
                        "number": seat,
                        "type": berth_type,
                        "position": "side" if berth_type in ["SL", "SU"] else "main"
                    })
            
            layout["bays"].append(bay)
        
        return layout

