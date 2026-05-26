
### Backend - `app/api/routes/documentation.py`

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from app.services.doc_generator import DocumentationGenerator

router = APIRouter()
doc_generator = DocumentationGenerator()

class ReadmeRequest(BaseModel):
    repo_analysis: Dict[str, Any]

class ApiDocsRequest(BaseModel):
    code: str
    language: str = "python"

class CodeSummaryRequest(BaseModel):
    code: str
    file_path: str

@router.post("/generate-readme")
async def generate_readme(request: ReadmeRequest):
    """Generate README.md from repository analysis"""
    if not request.repo_analysis:
        raise HTTPException(status_code=400, detail="Repository analysis data required")
    
    try:
        readme = doc_generator.generate_readme(request.repo_analysis)
        
        return {
            "success": True,
            "readme": readme,
            "format": "markdown",
            "filename": "README.md"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"README generation failed: {str(e)}")

@router.post("/generate-api-docs")
async def generate_api_docs(request: ApiDocsRequest):
    """Generate API documentation from code"""
    if not request.code:
        raise HTTPException(status_code=400, detail="Code required for API documentation")
    
    try:
        docs = doc_generator.generate_api_documentation(request.code, request.language)
        
        return {
            "success": True,
            "documentation": docs,
            "format": "markdown",
            "filename": "API_DOCS.md"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"API docs generation failed: {str(e)}")

@router.post("/summarize-code")
async def summarize_code(request: CodeSummaryRequest):
    """Generate summary for a code file"""
    if not request.code:
        raise HTTPException(status_code=400, detail="Code required for summarization")
    
    try:
        summary = doc_generator.generate_code_summary(request.code, request.file_path)
        
        return {
            "success": True,
            "summary": summary,
            "file_path": request.file_path
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Code summarization failed: {str(e)}")