from sqlalchemy import Column, Integer, String, Boolean, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    course_code = Column(String, unique=True, index=True) # e.g., "CSCI 111"
    title = Column(String)
    credits = Column(Integer)
    description = Column(Text)
    prerequisites_raw = Column(Text) # The raw string from the catalog
    
    # Store parsed logic as JSON if needed later, or just keep raw for now
    metadata_json = Column(JSON, nullable=True) 

class DegreePlan(Base):
    __tablename__ = "degree_plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String) # e.g., "BSCS 2024-2025"
    catalog_year = Column(String)
    
    # Stores the entire 4-year structure as a JSON blob for easy retrieval
    # Structure: { "freshman": { "fall": [...], "spring": [...] }, ... }
    plan_structure = Column(JSON) 
