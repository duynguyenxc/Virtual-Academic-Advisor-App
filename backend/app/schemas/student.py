from pydantic import BaseModel
from typing import List, Optional

class CourseGrade(BaseModel):
    course_code: str # e.g. "CSCI 111"
    grade: str # e.g. "A", "B+", "W"
    semester: Optional[str] = None # e.g. "Fall 2023"
    credits: float = 3.0

class StudentProfile(BaseModel):
    student_name: Optional[str] = None
    major: str = "Computer Science"
    catalog_year: str = "2024-2025" # Default, can be extracted
    gpa: float = 0.0
    taken_courses: List[CourseGrade] = []
    
    # Calculated fields
    credits_earned: float = 0.0

class TranscriptUploadResponse(BaseModel):
    success: bool
    profile: StudentProfile
    message: str
