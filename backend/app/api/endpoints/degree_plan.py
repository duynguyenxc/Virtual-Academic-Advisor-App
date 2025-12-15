from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.student import StudentProfile
from app.services.degree_planner import DegreePlannerService

router = APIRouter()

@router.post("/generate", response_model=dict)
async def generate_degree_plan(profile: StudentProfile, db: Session = Depends(get_db)):
    planner = DegreePlannerService(db)
    result = planner.generate_plan(profile)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
        
    return result
