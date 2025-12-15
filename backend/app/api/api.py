from app.api.endpoints import transcript, degree_plan, chat

api_router = APIRouter()
api_router.include_router(transcript.router, prefix="/transcript", tags=["transcript"])
api_router.include_router(degree_plan.router, prefix="/planner", tags=["planner"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
