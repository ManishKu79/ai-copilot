from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
import tempfile
import os
from app.services.analyzer import RepositoryAnalyzer
from app.services.github_service import GitHubService

router = APIRouter()
analyzer = RepositoryAnalyzer()
github_service = GitHubService()

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
        # Analyze the repository
        result = analyzer.analyze_zip(tmp_path)
        return {
            "success": True,
            "analysis": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
    finally:
        # Clean up temp file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

@router.post("/github")
async def analyze_github(request: AnalyzeRepoRequest):
    """Analyze GitHub repository"""
    if not request.repo_url:
        raise HTTPException(status_code=400, detail="GitHub URL is required")
    
    owner, repo = github_service.parse_github_url(request.repo_url)
    if not owner or not repo:
        raise HTTPException(status_code=400, detail="Invalid GitHub URL")
    
    # Get repository info from GitHub
    repo_info = github_service.get_repo_info(owner, repo)
    if not repo_info:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    # Analyze the repository
    analysis = analyzer.analyze_github_repo(request.repo_url)
    
    return {
        "success": True,
        "analysis": {
            **analysis,
            "github_info": {
                "stars": repo_info.get('stargazers_count', 0),
                "forks": repo_info.get('forks_count', 0),
                "description": repo_info.get('description', ''),
                "default_branch": repo_info.get('default_branch', 'main')
            }
        }
    }