from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from app.services.pr_reviewer import PRReviewer

router = APIRouter()
reviewer = PRReviewer()

class PRReviewRequest(BaseModel):
    diff: str
    files_changed: Optional[List[str]] = None
    pr_title: Optional[str] = ""
    pr_description: Optional[str] = ""

@router.post("/review")
async def review_pull_request(request: PRReviewRequest):
    """Review a pull request and provide feedback"""
    if not request.diff:
        raise HTTPException(status_code=400, detail="Diff content required")
    
    try:
        result = reviewer.review_pr(
            request.diff,
            request.files_changed,
            request.pr_title,
            request.pr_description
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PR review failed: {str(e)}")