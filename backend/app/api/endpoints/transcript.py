from fastapi import APIRouter, UploadFile, File, HTTPException
from app.schemas.student import StudentProfile, TranscriptUploadResponse
from app.services.transcript_parser import parser_service
import shutil
import os
import tempfile

router = APIRouter()

@router.post("/upload", response_model=TranscriptUploadResponse)
async def upload_transcript(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # Save temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        # Parse
        profile = parser_service.parse_pdf(tmp_path)
        return TranscriptUploadResponse(
            success=True,
            profile=profile,
            message="Transcript parsed successfully"
        )
    except Exception as e:
        return TranscriptUploadResponse(
            success=False,
            profile=StudentProfile(),
            message=f"Error parsing transcript: {str(e)}"
        )
    finally:
        # Cleanup
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
