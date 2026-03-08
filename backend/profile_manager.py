import json
import os
from io import BytesIO
from typing import List, Optional
from pypdf import PdfReader
from internship import Internship

PROFILE_FILE = "user_profile.json"

class ProfileManager:
    def __init__(self):
        self.profile = self.load_profile()

    def load_profile(self) -> dict:
        if os.path.exists(PROFILE_FILE):
            try:
                with open(PROFILE_FILE, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading profile: {e}")
        
        # Default profile if none exists
        return {
            "name": "",
            "education": "4th Year Integrated MSc in Data Science",
            "skills": ["Python", "ML", "Classification", "Deep Learning", "Django", "Pandas", "NumPy", "Web Scraping", "SQL"],
            "target_roles": ["Data Science Intern", "AI Research Intern", "Machine Learning Engineer"],
            "target_companies": ["Google", "Microsoft", "Amazon", "Nvidia", "OpenAI", "Flipkart", "Swiggy", "Razorpay"],
            "locations": ["India", "Bangalore", "Hyderabad", "Chennai", "Pune", "Remote"],
            "resume_text": ""
        }

    def save_profile(self, profile_data: dict):
        self.profile.update(profile_data)
        with open(PROFILE_FILE, "w") as f:
            json.dump(self.profile, f, indent=4)
        return self.profile

    def extract_text_from_pdf(self, file_content: bytes) -> str:
        """Extracts text from a PDF file."""
        try:
            reader = PdfReader(BytesIO(file_content))
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            print(f"Error extracting PDF text: {e}")
            return ""

    def parse_resume_to_profile(self, resume_text: str) -> dict:
        """
        Parses resume text to extract skills and education.
        In a production app, this would use an LLM for high accuracy.
        Here, we use a keyword-based approach for demonstration.
        """
        parsed_data = {}
        
        # Simple skill extraction (keyword matching)
        common_skills = ["Python", "Machine Learning", "ML", "Deep Learning", "SQL", "Django", "React", "C++", "Java", "Tableau", "PowerBI"]
        skills_found = []
        for skill in common_skills:
            if skill.lower() in resume_text.lower():
                skills_found.append(skill)
        
        if skills_found:
            parsed_data["skills"] = list(set(skills_found + self.profile.get("skills", [])))

        # Simple education check
        if "MSc" in resume_text or "Master" in resume_text:
            parsed_data["education"] = "MSc Data Science (Extracted from Resume)"
        
        parsed_data["resume_text"] = resume_text
        return parsed_data
