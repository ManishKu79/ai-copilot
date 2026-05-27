from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from app.services.dependency_graph import DependencyGraphBuilder

router = APIRouter()
graph_builder = DependencyGraphBuilder()

class GraphRequest(BaseModel):
    repository_data: Dict[str, Any]

class ModuleImpactRequest(BaseModel):
    module_name: str
    dependencies: Dict[str, Any]

@router.post("/build")
async def build_dependency_graph(request: GraphRequest):
    """Build dependency graph from repository"""
    if not request.repository_data:
        raise HTTPException(status_code=400, detail="Repository data required")
    
    try:
        result = graph_builder.build_graph(request.repository_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Graph building failed: {str(e)}")

@router.post("/impact")
async def get_module_impact(request: ModuleImpactRequest):
    """Get impact analysis for a module"""
    if not request.module_name:
        raise HTTPException(status_code=400, detail="Module name required")
    
    try:
        result = graph_builder.get_module_impact(request.module_name, request.dependencies)
        return {
            "success": True,
            "impact": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Impact analysis failed: {str(e)}")