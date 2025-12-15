import re
import pdfplumber
from typing import List
from app.schemas.student import StudentProfile, CourseGrade

class TranscriptParser:
    def parse_pdf(self, file_path: str) -> StudentProfile:
        text_content = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text_content += page.extract_text() + "\n"
        
        return self._extract_data_from_text(text_content)

    def _extract_data_from_text(self, text: str) -> StudentProfile:
        profile = StudentProfile()
        
        # 1. Extract Courses (Simple Regex based on Ole Miss format commonly seen)
        # Pattern: CSCI 111  Computer Science I   3.00   A
        # This is a heuristic and might need fine-tuning with real usage
        course_pattern = re.compile(r"(CSCI|MATH|WRIT|BISC|CHEM|PHYS|ECON|PSY|SOC|Fine Arts|Humanities)\s+(\d{3})\s+.*?\s+(\d+\.\d{2})\s+([A-Z][+-]?)")
        
        matches = course_pattern.findall(text)
        for m in matches:
            dept, num, creds, grade = m
            profile.taken_courses.append(CourseGrade(
                course_code=f"{dept} {num}",
                grade=grade,
                credits=float(creds)
            ))

        # 2. Extract GPA
        # Pattern: Cumulative GPA: 3.56
        gpa_pattern = re.compile(r"Cumulative GPA\s*[:]\s*(\d+\.\d+)")
        gpa_match = gpa_pattern.search(text)
        if gpa_match:
            profile.gpa = float(gpa_match.group(1))

        # 3. Calculate total credits
        profile.credits_earned = sum(c.credits for c in profile.taken_courses)

        return profile

parser_service = TranscriptParser()
