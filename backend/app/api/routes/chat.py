from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from app.services.ai_chat import AIChatAssistant

router = APIRouter()
chat_assistant = AIChatAssistant()

class ChatRequest(BaseModel):
    message: str
    repository_data: Dict[str, Any]
    conversation_id: Optional[str] = None

@router.post("/message")
async def chat_message(request: ChatRequest):
    """Send message to AI chat assistant"""
    if not request.message:
        raise HTTPException(status_code=400, detail="Message required")
    
    if not request.repository_data:
        raise HTTPException(status_code=400, detail="Repository data required")
    
    try:
        result = chat_assistant.chat(
            request.message,
            request.repository_data,
            request.conversation_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@router.get("/history/{conversation_id}")
async def get_history(conversation_id: str):
    """Get conversation history"""
    try:
        result = chat_assistant.get_conversation_history(conversation_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")

@router.post("/suggestions")
async def get_suggestions(repository_data: Dict[str, Any]):
    """Get suggested questions based on repository"""
    return {
        "success": True,
        "suggestions": [
            "Explain the architecture of this project",
            "What technologies are used?",
            "How can I improve code quality?",
            "What are the main dependencies?",
            "Show me the most complex parts"
        ]
    }