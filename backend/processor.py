from typing import List
from internship import Internship

class Processor:
    """
    Processor module to evaluate, filter, and rank internships.
    """
    def __init__(self, candidate_profile: dict):
        self.candidate_profile = candidate_profile

    def evaluate_internship(self, internship: Internship) -> Internship:
        """
        Evaluates a single internship against the candidate profile.
        In a full implementation, this would use an LLM (LangChain) to 
        read the JD and give a detailed reasoning.
        """
        score = 0
        reasons = []

        # Simple skill matching logic for demonstration
        candidate_skills = [s.lower() for s in self.candidate_profile.get("skills", [])]
        found_skills = [s.lower() for s in internship.required_skills]
        
        matches = set(candidate_skills).intersection(set(found_skills))
        score += len(matches) * 10
        
        if matches:
            reasons.append(f"Matches skills: {', '.join(matches)}")

        # Location preference
        if any(loc.lower() in internship.location.lower() for loc in self.candidate_profile.get("locations", [])):
            score += 20
            reasons.append("Preferred location match.")

        # Target company bonus
        if any(company.lower() in internship.company_name.lower() for company in self.candidate_profile.get("target_companies", [])):
            score += 30
            reasons.append("Top-tier target company.")

        # Role Match
        target_roles = [r.lower() for r in self.candidate_profile.get("target_roles", [])]
        if any(role in internship.role_title.lower() for role in target_roles):
            score += 40
            reasons.append("Role name match.")

        internship.match_score = min(score, 100)
        internship.match_reasoning = " | ".join(reasons)
        
        print(f"Evaluated {internship.company_name} - {internship.role_title}: Score={internship.match_score}")
        
        # Priority for high scores or urgent deadlines
        if internship.match_score >= 70:
            internship.is_high_priority = True

        return internship

    def filter_and_rank(self, internships: List[Internship]) -> List[Internship]:
        """
        Sorts internships by score and priority.
        """
        evaluated = [self.evaluate_internship(i) for i in internships]
        # Filter out low matches if needed
        return sorted(evaluated, key=lambda x: x.match_score, reverse=True)
