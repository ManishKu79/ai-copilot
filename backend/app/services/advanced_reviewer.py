# backend/app/services/advanced_reviewer.py
from typing import List, Dict, Any
from ..analyzers.python_analyzer import PythonAnalyzer
from ..analyzers.javascript_analyzer import JavaScriptAnalyzer
from ..analyzers.security_analyzer import SecurityAnalyzer
from ..analyzers.react_analyzer import ReactAnalyzer
from ..analyzers.performance_analyzer import PerformanceAnalyzer
from .base import CodeIssue, Severity

class AdvancedCodeReviewer:
    def __init__(self):
        self.security_analyzer = SecurityAnalyzer()
        self.react_analyzer = ReactAnalyzer()
        self.performance_analyzer = PerformanceAnalyzer()
        
    def review_code(self, code: str, language: str = "python", file_path: str = "") -> Dict[str, Any]:
        """Comprehensive code review with multiple analyzers"""
        all_issues = []
        
        # Security analysis (always run)
        security_issues = self.security_analyzer.analyze(code, file_path)
        all_issues.extend(security_issues)
        
        # React-specific analysis
        if file_path.endswith(('.jsx', '.tsx')) or 'react' in code.lower():
            react_issues = self.react_analyzer.analyze(code, file_path)
            all_issues.extend(react_issues)
        
        # Performance analysis
        perf_issues = self.performance_analyzer.analyze(code, file_path)
        all_issues.extend(perf_issues)
        
        # Generate severity scores
        severity_scores = {
            Severity.CRITICAL: 10,
            Severity.HIGH: 7,
            Severity.MEDIUM: 4,
            Severity.LOW: 2,
            Severity.INFO: 1
        }
        
        total_score = sum(severity_scores[issue.severity] for issue in all_issues)
        max_score = max(1, len(all_issues) * 10)
        quality_score = max(0, 100 - min(100, (total_score / max_score) * 100))
        
        # Categorize issues
        categorized = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": [],
            "info": []
        }
        
        for issue in all_issues:
            categorized[issue.severity.value].append({
                "line": issue.line,
                "column": issue.column,
                "type": issue.type.value,
                "rule_id": issue.rule_id,
                "message": issue.message,
                "suggestion": issue.suggestion,
                "fix_example": issue.fix_example,
                "reference_url": issue.reference_url
            })
        
        return {
            "quality_score": round(quality_score, 2),
            "total_issues": len(all_issues),
            "severity_breakdown": {
                "critical": len(categorized["critical"]),
                "high": len(categorized["high"]),
                "medium": len(categorized["medium"]),
                "low": len(categorized["low"]),
                "info": len(categorized["info"])
            },
            "issues_by_category": categorized,
            "maintainability_score": self._calculate_maintainability(all_issues, len(code.split('\n'))),
            "security_score": self._calculate_security_score(security_issues)
        }
    
    def _calculate_maintainability_score(self, issues: List[CodeIssue], lines: int) -> float:
        """Calculate maintainability index"""
        # Lower issues per line = better maintainability
        issue_density = len(issues) / max(1, lines) * 100
        base_score = 100 - min(100, issue_density * 2)
        
        # Penalize critical and high issues more
        penalty = sum(
            10 if i.severity == Severity.CRITICAL else
            5 if i.severity == Severity.HIGH else
            2 if i.severity == Severity.MEDIUM else 0
            for i in issues
        )
        
        return max(0, min(100, base_score - penalty))
    
    def _calculate_security_score(self, security_issues: List[CodeIssue]) -> float:
        """Calculate security score"""
        if not security_issues:
            return 100
        
        points = 100
        for issue in security_issues:
            if issue.severity == Severity.CRITICAL:
                points -= 25
            elif issue.severity == Severity.HIGH:
                points -= 15
            elif issue.severity == Severity.MEDIUM:
                points -= 8
            elif issue.severity == Severity.LOW:
                points -= 3
        
        return max(0, points)