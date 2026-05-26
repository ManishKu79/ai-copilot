from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.services.bug_predictor import BugPredictor
from app.services.ml_predictor import MLBugPredictor

router = APIRouter()
bug_predictor = BugPredictor()
ml_predictor = MLBugPredictor()

class RiskAnalysisRequest(BaseModel):
    repo_id: str
    files_data: List[Dict[str, Any]]

class FileRiskRequest(BaseModel):
    file_path: str
    file_metrics: Dict[str, Any]

@router.post("/analyze")
async def analyze_repository_risk(request: RiskAnalysisRequest):
    """Analyze repository for bug risk"""
    if not request.files_data:
        raise HTTPException(status_code=400, detail="No file data provided")
    
    try:
        repository_data = {
            'files': request.files_data,
            'repo_id': request.repo_id
        }
        
        result = bug_predictor.analyze_repository_risk(repository_data)
        
        # Add ML predictions for each file
        for file_result in result.get('high_risk_files', []):
            ml_probability = ml_predictor.predict_bug_probability(file_result)
            file_result['ml_bug_probability'] = round(ml_probability * 100, 1)
        
        # Identify risk patterns
        risk_patterns = ml_predictor.identify_risk_patterns(request.files_data)
        result['risk_patterns'] = risk_patterns
        
        return {
            "success": True,
            "analysis": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Risk analysis failed: {str(e)}")

@router.post("/predict-file")
async def predict_file_risk(request: FileRiskRequest):
    """Predict risk for a single file"""
    try:
        file_metrics = request.file_metrics
        file_metrics['path'] = request.file_path
        file_metrics['name'] = request.file_path.split('/')[-1]
        
        risk_analysis = bug_predictor._analyze_file_risk(file_metrics)
        ml_probability = ml_predictor.predict_bug_probability(file_metrics)
        
        risk_analysis['ml_bug_probability'] = round(ml_probability * 100, 1)
        
        return {
            "success": True,
            "risk_analysis": risk_analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")