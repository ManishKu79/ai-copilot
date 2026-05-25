# backend/app/analyzers/base.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class IssueType(Enum):
    SECURITY = "security"
    PERFORMANCE = "performance"
    BUG = "bug"
    CODE_SMELL = "code_smell"
    BEST_PRACTICE = "best_practice"
    REACT_SPECIFIC = "react_specific"

@dataclass
class CodeIssue:
    line: int
    column: Optional[int]
    severity: Severity
    type: IssueType
    rule_id: str
    message: str
    suggestion: str
    fix_example: Optional[str] = None
    reference_url: Optional[str] = None

class BaseAnalyzer(ABC):
    def __init__(self):
        self.issues: List[CodeIssue] = []
    
    @abstractmethod
    def analyze(self, code: str, file_path: str = "") -> List[CodeIssue]:
        pass
    
    def add_issue(self, issue: CodeIssue):
        self.issues.append(issue)