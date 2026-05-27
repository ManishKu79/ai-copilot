from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from app.services.commit_generator import CommitMessageGenerator

router = APIRouter()
generator = CommitMessageGenerator()

class CommitRequest(BaseModel):
    diff: Optional[str] = None
    files_changed: Optional[List[str]] = None
    description: Optional[str] = None
    commit_type: Optional[str] = "feat"
    scope: Optional[str] = None

class ParseRequest(BaseModel):
    commit_message: str

@router.post("/generate")
async def generate_commit(request: CommitRequest):
    """Generate commit message from diff or description"""
    try:
        if request.diff:
            result = generator.generate_from_diff(request.diff, request.files_changed)
        elif request.description:
            if request.scope:
                result = generator.generate_with_scope(request.description, request.commit_type, request.scope)
            else:
                result = generator.generate_simple_message(request.description, request.commit_type)
        else:
            raise HTTPException(status_code=400, detail="Either diff or description required")
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

@router.post("/parse")
async def parse_commit(request: ParseRequest):
    """Parse a conventional commit message"""
    if not request.commit_message:
        raise HTTPException(status_code=400, detail="Commit message required")
    
    try:
        result = generator.parse_conventional_commit(request.commit_message)
        return {
            "success": True,
            "parsed": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parse failed: {str(e)}")

@router.get("/types")
async def get_commit_types():
    """Get available commit types"""
    return {
        "success": True,
        "types": generator.commit_types
    }