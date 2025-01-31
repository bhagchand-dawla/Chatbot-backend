from fastapi import APIRouter, HTTPException
from app.services.ai_model import get_answer

router = APIRouter()

@router.get("/qa/")
async def ask_question(query: str):
    try:
        answer = await get_answer(query)
        return {"question": query, "answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
