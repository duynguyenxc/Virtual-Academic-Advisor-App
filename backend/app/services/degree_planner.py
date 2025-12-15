from sqlalchemy.orm import Session
from app.models.course import Course, DegreePlan
from app.schemas.student import StudentProfile, CourseGrade
from typing import List, Dict, Any
import json

class DegreePlannerService:
    def __init__(self, db: Session):
        self.db = db

    def generate_plan(self, student_profile: StudentProfile) -> Dict[str, Any]:
        # 1. Fetch Degree Requirements (BSCS 2024-2025)
        # simplistic fetch for now, assuming one main plan
        plan_model = self.db.query(DegreePlan).filter(DegreePlan.name.like("%BSCS%")).first()
        if not plan_model:
            return {"error": "No degree plan found in database."}
        
        # 2. Identify Taken Courses (Set of codes)
        taken_courses = {c.course_code.upper() for c in student_profile.taken_courses}
        
        # 3. Flatten Degree Plan to find all required courses
        target_plan = plan_model.plan_structure # JSON structure
        
        missing_courses = []
        
        # Simple traversal to find missing requirements
        # Structure: { "freshman": { "fall": [ { "course": "CSCI 111", ... } ] } }
        for year, semesters in target_plan.items():
            for semester, courses in semesters.items():
                for course_req in courses:
                    course_name = course_req.get("course")
                    # Handle "OR" logic roughly (e.g. "WRIT 100 or WRIT 101")
                    if " or " in course_name.lower():
                        options = [opt.strip().upper() for opt in course_name.split(" or ")]
                        if not any(opt in taken_courses for opt in options):
                             missing_courses.append(course_req)
                    elif "elective" in course_name.lower():
                        # Electives are tricky, simplistic check:
                        # If we have "Minor/Tech Elective", we assume it's missing unless user manually tracks it.
                        # For MVP, we just list it as needed.
                        missing_courses.append(course_req)
                    else:
                        if course_name.upper() not in taken_courses:
                            missing_courses.append(course_req)

        # 4. Create a Schedule (The "Magic")
        # For MVP, we just strictly follow the 4-year plan order for missing items.
        # A real solver would use constraint satisfaction (CSP).
        
        generated_schedule = []
        current_load = 0
        MAX_LOAD = 15 # Credits per semester
        
        semester_bucket = []
        
        for req in missing_courses:
            # Check prerequisites (Basic check against "taken_courses")
            # In a real engine, we'd check against the 'database' of prereqs. 
            # Here we trust the 'prerequisites' field in the JSON plan if it exists, 
            # but verifying against strict logic is better.
            
            # Add to bucket
            req_credits = req.get("credits", 3)
            if current_load + req_credits > MAX_LOAD:
                # Flush bucket to a new semester
                generated_schedule.append(semester_bucket)
                semester_bucket = []
                current_load = 0
            
            semester_bucket.append(req)
            current_load += req_credits
            
        if semester_bucket:
            generated_schedule.append(semester_bucket)

        return {
            "status": "success",
            "student": student_profile.dict(),
            "missing_count": len(missing_courses),
            "recommended_schedule": generated_schedule,
            "raw_plan": target_plan
        }
