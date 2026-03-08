from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Internship(BaseModel):
    id: Optional[str] = None
    company_name: str
    role_title: str
    location: str
    duration: Optional[str] = None
    required_skills: List[str]
    eligibility_criteria: Optional[str] = None
    application_deadline: Optional[str] = None
    application_link: str
    posted_date: Optional[str] = None
    match_score: Optional[int] = 0
    match_reasoning: Optional[str] = None
    is_high_priority: bool = False
    found_at: datetime = Field(default_factory=datetime.now)

class InternshipReport(BaseModel):
    date: str
    total_found: int
    internships: List[Internship]
    top_recommendations: List[Internship]
    urgent_deadlines: List[Internship]
