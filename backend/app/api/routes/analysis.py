from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
import tempfile
import os
from app.services.analyzer import RepositoryAnalyzer

router = APIRouter()
analyzer = RepositoryAnalyzer()

class AnalyzeRepoRequest(BaseModel):
    repo_url: Optional[str] = None

@router.post("/upload")
async def analyze_upload(file: UploadFile = File(...)):
    """Analyze uploaded ZIP file"""
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Only ZIP files are accepted")
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_path = tmp_file.name
    
    try:
        result = analyzer.analyze_zip(tmp_path)
        return {
            "success": True,
            "analysis": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

@router.post("/github")
async def analyze_github(request: AnalyzeRepoRequest):
    """Analyze GitHub repository from URL"""
    if not request.repo_url:
        raise HTTPException(status_code=400, detail="GitHub URL is required")
    
    try:
        result = analyzer.analyze_github_repo(request.repo_url)
        
        if result.get('error'):
            raise HTTPException(status_code=404, detail=result.get('message', 'Repository not found'))
        
        return {
            "success": True,
            "analysis": result
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"GitHub analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"GitHub analysis failed: {str(e)}")