from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from app.services.test_generator import TestGenerator

router = APIRouter()
generator = TestGenerator()

class TestRequest(BaseModel):
    code: str
    language: str = "python"
    function_name: Optional[str] = None

class EdgeCaseRequest(BaseModel):
    code: str
    language: str = "python"

class ApiTestRequest(BaseModel):
    endpoints: List[Dict[str, str]]

@router.post("/generate")
async def generate_tests(request: TestRequest):
    """Generate unit tests for code"""
    if not request.code:
        raise HTTPException(status_code=400, detail="Code required")
    
    try:
        result = generator.generate_tests(
            request.code,
            request.language,
            request.function_name
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test generation failed: {str(e)}")

@router.post("/edge-cases")
async def generate_edge_cases(request: EdgeCaseRequest):
    """Generate edge case test scenarios"""
    if not request.code:
        raise HTTPException(status_code=400, detail="Code required")
    
    try:
        edge_cases = generator.generate_edge_cases(request.code, request.language)
        return {
            "success": True,
            "edge_cases": edge_cases,
            "total_cases": len(edge_cases)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Edge case generation failed: {str(e)}")

@router.post("/api-tests")
async def generate_api_tests(request: ApiTestRequest):
    """Generate API tests from endpoint definitions"""
    if not request.endpoints:
        raise HTTPException(status_code=400, detail="Endpoints required")
    
    try:
        test_code = generator.generate_api_tests(request.endpoints)
        return {
            "success": True,
            "test_code": test_code,
            "endpoints_count": len(request.endpoints)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"API test generation failed: {str(e)}")