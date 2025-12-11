from typing import List, Dict, Any, Optional
from datetime import datetime
from beanie import PydanticObjectId
import openai
import json
import asyncio
from app.core.config import settings

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
    
    def __init__(self):
        """Initialize OpenAI client if enabled"""
        self.use_openai_matching = getattr(settings, 'USE_OPENAI_MATCHING', False)
        if self.use_openai_matching and getattr(settings, 'OPENAI_API_KEY', None):
            openai.api_key = settings.OPENAI_API_KEY
    
    async def find_matches(
        self,
        ticket: Ticket,
        preferences: Dict[str, Any] = {},
        use_ai_enhancement: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Find potential exchange matches for a ticket
        
        Args:
            ticket: The ticket to find matches for
            preferences: User preferences for filtering
            use_ai_enhancement: If True, uses OpenAI for enhanced matching
            
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
            
            # Calculate match score using traditional method
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
                    "ai_enhanced": False,
                })
        
        # If AI enhancement is enabled and we have OpenAI configured, enhance scores
        if use_ai_enhancement and self.use_openai_matching and matches:
            matches = await self._enhance_matches_with_openai(ticket, matches)
        
        # Sort by match score descending
        matches.sort(key=lambda x: x["match_score"], reverse=True)
        
        return matches[:10]  # Return top 10 matches
    
    async def batch_find_matches(
        self,
        tickets: List[Ticket],
        use_ai_enhancement: bool = False
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Find matches for multiple tickets efficiently (for 10s of users at once)
        
        Args:
            tickets: List of tickets to find matches for
            use_ai_enhancement: If True, uses OpenAI for enhanced matching
            
        Returns:
            Dictionary mapping ticket_id to list of matches
        """
        results = {}
        
        # Process tickets in parallel batches of 3 to avoid overwhelming the API
        for i in range(0, len(tickets), 3):
            batch = tickets[i:i+3]
            batch_tasks = [
                self.find_matches(ticket, {}, use_ai_enhancement)
                for ticket in batch
            ]
            batch_results = await asyncio.gather(*batch_tasks)
            
            for ticket, matches in zip(batch, batch_results):
                results[str(ticket.id)] = matches
        
        return results
    
    async def _enhance_matches_with_openai(
        self,
        ticket: Ticket,
        matches: List[Dict[str, Any]],
        top_n: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Use OpenAI to intelligently re-rank matches based on complex criteria
        
        Args:
            ticket: The user's ticket
            matches: Initial matches from traditional scoring
            top_n: Number of top matches to send to OpenAI for re-ranking
            
        Returns:
            Enhanced matches with adjusted scores and AI insights
        """
        try:
            # Prepare a concise summary for OpenAI
            my_passengers_info = [
                {
                    "name": p.name,
                    "coach": p.coach,
                    "seat": p.seat_number,
                    "berth": p.berth_type,
                    "status": p.booking_status
                }
                for p in ticket.passengers
            ]
            
            # Take top N matches for AI analysis
            top_matches = matches[:top_n]
            matches_data = [
                {
                    "match_rank": i + 1,
                    "other_user": m["user_name"],
                    "other_user_rating": m["user_rating"],
                    "current_score": m["match_score"],
                    "available_seats": m["available_seats"][:3],  # Limit data size
                    "benefits": m["benefit_description"]
                }
                for i, m in enumerate(top_matches)
            ]
            
            # Prompt for OpenAI
            prompt = f"""Analyze these train seat exchange matches and re-rank them based on overall compatibility and exchange quality.

My ticket passengers:
{json.dumps(my_passengers_info, indent=2)}

Potential matches:
{json.dumps(matches_data, indent=2)}

Evaluate each match considering:
1. How well the other person's seats complement mine for family grouping
2. User reliability (rating)
3. Practical feasibility of the exchange
4. How many people can be brought together

Respond with ONLY a valid JSON object (no markdown, no extra text):
{{
    "reranked_matches": [
        {{
            "match_rank": <original match rank>,
            "ai_score": <0-100 new score based on AI analysis>,
            "reasoning": "<brief explanation in 1-2 sentences>",
            "confidence": <0-1 confidence in this assessment>
        }}
    ],
    "overall_recommendation": "<brief insight about best options>"
}}"""
            
            response = await asyncio.to_thread(
                openai.ChatCompletion.create,
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at analyzing train seat exchange scenarios. Respond only with valid JSON."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Parse AI response
            ai_result = json.loads(response_text)
            
            # Create a mapping of original match rank to AI scores
            ai_scores = {}
            for reranked in ai_result.get("reranked_matches", []):
                ai_scores[reranked["match_rank"]] = {
                    "ai_score": reranked["ai_score"],
                    "reasoning": reranked["reasoning"],
                    "confidence": reranked["confidence"]
                }
            
            # Update matches with AI scores (blend traditional and AI scores)
            enhanced_matches = []
            for i, match in enumerate(top_matches):
                rank = i + 1
                if rank in ai_scores:
                    ai_data = ai_scores[rank]
                    # Blend scores: 60% traditional, 40% AI
                    blended_score = (
                        match["match_score"] * 0.6 +
                        ai_data["ai_score"] * 0.4
                    )
                    match["match_score"] = round(blended_score, 1)
                    match["ai_reasoning"] = ai_data["reasoning"]
                    match["ai_confidence"] = ai_data["confidence"]
                    match["ai_enhanced"] = True
                
                enhanced_matches.append(match)
            
            # Add remaining matches (not analyzed by AI)
            enhanced_matches.extend(matches[top_n:])
            
            return enhanced_matches
            
        except json.JSONDecodeError as e:
            print(f"Failed to parse OpenAI response: {e}")
            # Return original matches if parsing fails
            return matches
        except Exception as e:
            print(f"Error enhancing matches with OpenAI: {e}")
            # Return original matches if any error occurs
            return matches
    
    def _prepare_batch_analysis_prompt(
        self,
        tickets_with_matches: List[Dict[str, Any]]
    ) -> str:
        """
        Prepare a batch analysis prompt for analyzing multiple users' matches at once
        """
        analysis_data = []
        for item in tickets_with_matches[:5]:  # Limit to 5 tickets per batch
            analysis_data.append({
                "user": item["user_name"],
                "passengers": item["passengers_count"],
                "train": item["train_number"],
                "scattered": item["is_scattered"],
                "top_3_matches": [
                    {
                        "with": m["user_name"],
                        "score": m["match_score"],
                        "benefits": m["benefit_description"]
                    }
                    for m in item["matches"][:3]
                ]
            })
        
        prompt = f"""Batch analyze these train seat exchange scenarios and provide insights:

{json.dumps(analysis_data, indent=2)}

For each user, evaluate:
1. How realistic are their top matches?
2. What percentage of their group can potentially be reunited?
3. Any red flags or concerns?

Respond with JSON:
{{
    "analyses": [
        {{
            "user": "<user name>",
            "reunification_potential": <0-100>,
            "recommended_match": "<best match reason>",
            "risks": ["<risk1>", "<risk2>"]
        }}
    ]
}}"""
        return prompt
    
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

