from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from app.services.code_reviewer import CodeReviewer

router = APIRouter()
reviewer = CodeReviewer()

class CodeReviewRequest(BaseModel):
    code: str
    language: str = "python"

class CodeReviewResponse(BaseModel):
    issues: List[Dict[str, Any]]
    quality_score: float
    total_issues: int
    severity_breakdown: Dict[str, int]

@router.post("/", response_model=CodeReviewResponse)
async def review_code(request: CodeReviewRequest):
    """Review code and return issues with suggestions"""
    if not request.code or len(request.code.strip()) == 0:
        raise HTTPException(status_code=400, detail="No code provided for review")
    
    try:
        # Limit code size to prevent performance issues
        if len(request.code) > 50000:
            raise HTTPException(status_code=400, detail="Code too large (max 50,000 characters)")
        
        result = reviewer.review_code(request.code, request.language)
        
        # Add duplicate code detection
        duplicates = reviewer.detect_duplicate_code(request.code)
        result['issues'].extend(duplicates)
        
        # Recalculate totals
        result['total_issues'] = len(result['issues'])
        severity_scores = {'error': 10, 'warning': 5, 'info': 1}
        total_score = sum(severity_scores.get(issue['severity'], 0) for issue in result['issues'])
        max_score = max(1, len(result['issues']) * 10)
        result['quality_score'] = round(max(0, 100 - min(100, (total_score / max_score) * 100)), 2)
        
        # Update severity breakdown
        result['severity_breakdown'] = {
            'error': sum(1 for i in result['issues'] if i['severity'] == 'error'),
            'warning': sum(1 for i in result['issues'] if i['severity'] == 'warning'),
            'info': sum(1 for i in result['issues'] if i['severity'] == 'info')
        }
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Review failed: {str(e)}")