import os
import json
import asyncio
from sqlalchemy.future import select
from app.core.database import SessionLocal, engine, Base
from app.models.course import Course, DegreePlan

# Import for filesystem traversal
BASE_DATA_DIR = os.path.join(os.path.dirname(__file__), "olemiss", "bscs", "2024_2025")

def init_db():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created.")

def ingest_courses():
    session = SessionLocal()
    try:
        courses_file = os.path.join(BASE_DATA_DIR, "csci_courses_full.json")
        if not os.path.exists(courses_file):
            print(f"File not found: {courses_file}")
            return

        with open(courses_file, "r", encoding="utf-8") as f:
            courses_data = json.load(f)

        print(f"Found {len(courses_data)} courses. Ingesting...")
        
        for c_data in courses_data:
            # Extract code from title (e.g., "CIS 111: ...")
            title_parts = c_data["title"].split(":", 1)
            code = title_parts[0].strip()
            title = title_parts[1].strip() if len(title_parts) > 1 else c_data["title"]
            
            # Check if exists
            existing = session.query(Course).filter(Course.course_code == code).first()
            if not existing:
                new_course = Course(
                    course_code=code,
                    title=title,
                    credits=int(c_data["credits"]) if c_data["credits"].isdigit() else 3, # Default to 3 if weird
                    description=c_data["description"],
                    prerequisites_raw=c_data["prerequisites"],
                    metadata_json=c_data
                )
                session.add(new_course)
        
        session.commit()
        print("Courses ingested successfully.")

    except Exception as e:
        print(f"Error ingesting courses: {e}")
        session.rollback()
    finally:
        session.close()

def ingest_degree_plan():
    session = SessionLocal()
    try:
        plan_file = os.path.join(BASE_DATA_DIR, "four_year_plan.json")
        if not os.path.exists(plan_file):
            print(f"File not found: {plan_file}")
            return

        with open(plan_file, "r", encoding="utf-8") as f:
            plan_data = json.load(f)

        plan_name = f"{plan_data.get('program', 'BSCS')} {plan_data.get('catalog_year', 'Unknown')}"
        
        # Check if exists
        existing = session.query(DegreePlan).filter(DegreePlan.name == plan_name).first()
        if not existing:
            new_plan = DegreePlan(
                name=plan_name,
                catalog_year=plan_data.get("catalog_year"),
                plan_structure=plan_data.get("plan")
            )
            session.add(new_plan)
            print(f"Ingested Degree Plan: {plan_name}")
        else:
            print(f"Degree Plan {plan_name} already exists.")
            
        session.commit()

    except Exception as e:
        print(f"Error ingesting degree plan: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    # Ensure we are in the root directory context for imports to work if running as script from root
    # But for simplicity, we assume this is run via `python -m data.ingest_structured` from root
    init_db()
    ingest_courses()
    ingest_degree_plan()
