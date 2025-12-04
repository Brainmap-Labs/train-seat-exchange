from typing import List, Dict, Any, Optional
from datetime import datetime
from beanie import PydanticObjectId

from app.models.ticket import Ticket, Passenger
from app.models.user import User

class MatchingService:
    """Service for finding potential seat exchange matches"""
    
    # Berth preferences for scoring
    BERTH_PREFERENCES = {
        "LB": 5,  # Lower berth - most preferred
        "SL": 4,  # Side lower
        "MB": 3,  # Middle berth
        "SU": 2,  # Side upper
        "UB": 1,  # Upper berth - least preferred
    }
    
    async def find_matches(
        self,
        ticket: Ticket,
        preferences: Dict[str, Any] = {}
    ) -> List[Dict[str, Any]]:
        """
        Find potential exchange matches for a ticket
        
        Args:
            ticket: The ticket to find matches for
            preferences: User preferences for filtering
            
        Returns:
            List of potential matches with scores
        """
        # Find other tickets on the same train and date
        other_tickets = await Ticket.find(
            Ticket.train_number == ticket.train_number,
            Ticket.travel_date == ticket.travel_date,
            Ticket.user_id != ticket.user_id,
            Ticket.status == "active",
        ).to_list()
        
        matches = []
        
        for other_ticket in other_tickets:
            # Get the other user
            other_user = await User.get(other_ticket.user_id)
            if not other_user:
                continue
            
            # Calculate match score
            match_result = self._calculate_match_score(
                ticket, other_ticket, preferences
            )
            
            if match_result["score"] > 0:
                matches.append({
                    "user_id": str(other_user.id),
                    "user_name": other_user.name,
                    "user_rating": other_user.rating,
                    "ticket_id": str(other_ticket.id),
                    "available_seats": [
                        {
                            "passenger_id": p.id,
                            "passenger_name": p.name,
                            "coach": p.coach,
                            "seat_number": p.seat_number,
                            "berth_type": p.berth_type,
                        }
                        for p in other_ticket.passengers
                    ],
                    "match_score": match_result["score"],
                    "benefit_description": match_result["description"],
                })
        
        # Sort by match score descending
        matches.sort(key=lambda x: x["match_score"], reverse=True)
        
        return matches[:10]  # Return top 10 matches
    
    def _calculate_match_score(
        self,
        my_ticket: Ticket,
        other_ticket: Ticket,
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate how good a potential match is
        
        Returns:
            Dictionary with score (0-100) and description
        """
        score = 0
        benefits = []
        
        my_coaches = set(p.coach for p in my_ticket.passengers)
        other_coaches = set(p.coach for p in other_ticket.passengers)
        
        my_seats = {(p.coach, p.seat_number): p for p in my_ticket.passengers}
        other_seats = {(p.coach, p.seat_number): p for p in other_ticket.passengers}
        
        # Check for same coach potential
        common_coaches = my_coaches & other_coaches
        if common_coaches:
            score += 30
            benefits.append(f"Same coach ({', '.join(common_coaches)})")
        
        # Check for adjacent seats (same bay)
        for (my_coach, my_seat), my_passenger in my_seats.items():
            for (other_coach, other_seat), other_passenger in other_seats.items():
                if my_coach == other_coach:
                    # Check if in same bay (group of 8)
                    my_bay = (my_seat - 1) // 8
                    other_bay = (other_seat - 1) // 8
                    
                    if my_bay == other_bay:
                        score += 20
                        benefits.append(f"Same bay as seat {other_seat}")
                    
                    # Check if adjacent
                    if abs(my_seat - other_seat) <= 1:
                        score += 15
                        benefits.append(f"Adjacent to seat {other_seat}")
        
        # Check berth type improvements
        for other_p in other_ticket.passengers:
            other_berth_score = self.BERTH_PREFERENCES.get(other_p.berth_type, 0)
            
            for my_p in my_ticket.passengers:
                my_berth_score = self.BERTH_PREFERENCES.get(my_p.berth_type, 0)
                
                # If other berth is better than mine
                if other_berth_score > my_berth_score:
                    score += 10
                    benefits.append(f"Better berth: {other_p.berth_type}")
        
        # Apply preference filters
        if preferences.get("same_coach_only") and not common_coaches:
            return {"score": 0, "description": "No matching coaches"}
        
        # Cap score at 100
        score = min(score, 100)
        
        description = " • ".join(benefits) if benefits else "Potential exchange available"
        
        return {"score": score, "description": description}
    
    def calculate_togetherness_score(self, passengers: List[Passenger]) -> float:
        """
        Calculate how "together" a group of passengers is
        
        Higher score = passengers are closer together
        """
        if len(passengers) <= 1:
            return 100.0
        
        score = 100.0
        
        # Group by coach
        coach_groups = {}
        for p in passengers:
            if p.coach not in coach_groups:
                coach_groups[p.coach] = []
            coach_groups[p.coach].append(p)
        
        # Penalty for multiple coaches
        if len(coach_groups) > 1:
            score -= 30 * (len(coach_groups) - 1)
        
        # Check bay distribution within each coach
        for coach, group in coach_groups.items():
            if len(group) > 1:
                bays = set((p.seat_number - 1) // 8 for p in group)
                if len(bays) > 1:
                    score -= 10 * (len(bays) - 1)
        
        return max(score, 0)

