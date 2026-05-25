from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services.error_explainer import ErrorExplainer

router = APIRouter()
explainer = ErrorExplainer()

class ErrorExplainRequest(BaseModel):
    error_message: str
    language: str = "python"
    context: Optional[str] = None

@router.post("/explain")
async def explain_error(request: ErrorExplainRequest):
    """Explain error message and provide fixes"""
    if not request.error_message or len(request.error_message.strip()) == 0:
        raise HTTPException(status_code=400, detail="No error message provided")
    
    try:
        explanation = explainer.explain_error(
            request.error_message,
            request.context or request.language
        )
        
        return {
            "success": True,
            "explanation": explanation
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error explanation failed: {str(e)}")