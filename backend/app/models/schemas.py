from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class RepositoryInfo(BaseModel):
    name: str
    files_count: int
    languages: dict
    complexity_score: float

class CodeIssue(BaseModel):
    line: int
    severity: str  # error, warning, info
    message: str
    suggestion: Optional[str] = None

class AnalysisResult(BaseModel):
    repository: RepositoryInfo
    issues: List[CodeIssue]
    created_at: datetime