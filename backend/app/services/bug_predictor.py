import os
import ast
import math
from typing import Dict, List, Any, Tuple
from collections import Counter
from datetime import datetime
import json

class BugPredictor:
    def __init__(self):
        self.risk_weights = {
            'complexity': 0.35,
            'churn': 0.25,
            'dependency_count': 0.20,
            'test_coverage': 0.20
        }
        
        self.complexity_thresholds = {
            'low': 3,
            'medium': 6,
            'high': 8
        }
        
    def analyze_repository_risk(self, repository_data: Dict) -> Dict[str, Any]:
        """Main entry point for repository risk analysis"""
        files = repository_data.get('files', [])
        structure = repository_data.get('structure', {})
        
        # Analyze each file
        risk_analysis = []
        total_risk_score = 0
        
        for file in files:
            if file.get('error'):
                continue
                
            file_risk = self._analyze_file_risk(file)
            risk_analysis.append(file_risk)
            total_risk_score += file_risk['risk_score']
        
        # Calculate overall metrics
        avg_risk = total_risk_score / max(1, len(risk_analysis))
        
        # Identify high-risk files
        high_risk_files = [f for f in risk_analysis if f['risk_level'] == 'high']
        medium_risk_files = [f for f in risk_analysis if f['risk_level'] == 'medium']
        
        # Generate recommendations
        recommendations = self._generate_recommendations(risk_analysis, repository_data)
        
        return {
            'overall_risk_score': round(avg_risk, 2),
            'risk_level': self._get_risk_level(avg_risk),
            'total_files_analyzed': len(risk_analysis),
            'high_risk_files_count': len(high_risk_files),
            'medium_risk_files_count': len(medium_risk_files),
            'high_risk_files': high_risk_files[:10],  # Top 10 high-risk files
            'risk_distribution': self._calculate_risk_distribution(risk_analysis),
            'recommendations': recommendations,
            'maintainability_score': self._calculate_maintainability_score(risk_analysis),
            'prediction_confidence': self._calculate_confidence(risk_analysis)
        }
    
    def _analyze_file_risk(self, file: Dict) -> Dict[str, Any]:
        """Analyze individual file risk factors"""
        file_path = file.get('path', '')
        file_name = file.get('name', '')
        complexity = file.get('complexity', 1.0)
        lines = file.get('lines', 0)
        
        # Calculate individual risk factors
        complexity_risk = self._calculate_complexity_risk(complexity, lines)
        size_risk = self._calculate_size_risk(lines)
        dependency_risk = self._calculate_dependency_risk(file_path)
        history_risk = self._simulate_history_risk(file_name)  # Simulated for Phase 5
        
        # Weighted risk score
        risk_score = (
            complexity_risk * self.risk_weights['complexity'] +
            size_risk * 0.15 +
            dependency_risk * self.risk_weights['dependency_count'] +
            history_risk * self.risk_weights['churn']
        )
        
        # Determine risk level
        risk_level = self._get_risk_level(risk_score)
        
        # Generate specific predictions
        predictions = self._generate_predictions(file, risk_score, risk_level)
        
        return {
            'file_path': file_path,
            'file_name': file_name,
            'risk_score': round(risk_score, 2),
            'risk_level': risk_level,
            'complexity_risk': round(complexity_risk, 2),
            'size_risk': round(size_risk, 2),
            'dependency_risk': round(dependency_risk, 2),
            'history_risk': round(history_risk, 2),
            'lines_of_code': lines,
            'complexity': complexity,
            'predictions': predictions,
            'suggested_actions': self._suggest_actions(risk_level, file)
        }
    
    def _calculate_complexity_risk(self, complexity: float, lines: int) -> float:
        """Calculate risk based on code complexity"""
        # Normalize complexity (0-10 scale)
        normalized_complexity = min(10, complexity)
        
        # Higher complexity = higher risk
        if normalized_complexity <= 3:
            return 0.2  # Low risk
        elif normalized_complexity <= 6:
            return 0.5  # Medium risk
        elif normalized_complexity <= 8:
            return 0.8  # High risk
        else:
            return 1.0  # Critical risk
    
    def _calculate_size_risk(self, lines: int) -> float:
        """Calculate risk based on file size"""
        if lines <= 100:
            return 0.1
        elif lines <= 300:
            return 0.3
        elif lines <= 500:
            return 0.6
        elif lines <= 1000:
            return 0.8
        else:
            return 1.0
    
    def _calculate_dependency_risk(self, file_path: str) -> float:
        """Calculate risk based on number of dependencies"""
        # Simplified: More imports = higher risk
        try:
            if file_path.endswith('.py'):
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    import_count = content.count('import ') + content.count('from ')
                    if import_count <= 5:
                        return 0.2
                    elif import_count <= 15:
                        return 0.5
                    else:
                        return 0.8
        except:
            pass
        
        return 0.3  # Default medium risk
    
    def _simulate_history_risk(self, file_name: str) -> float:
        """Simulate historical change frequency (would use git in production)"""
        # In production, this would analyze git history
        # For Phase 5, we use heuristics based on file name patterns
        
        high_churn_patterns = ['util', 'helper', 'common', 'base', 'core']
        medium_churn_patterns = ['service', 'handler', 'controller', 'manager']
        
        file_lower = file_name.lower()
        
        for pattern in high_churn_patterns:
            if pattern in file_lower:
                return 0.8  # High historical change frequency
        
        for pattern in medium_churn_patterns:
            if pattern in file_lower:
                return 0.5  # Medium historical change frequency
        
        return 0.3  # Low historical change frequency
    
    def _get_risk_level(self, score: float) -> str:
        """Convert numeric score to risk level"""
        if score >= 0.7:
            return 'high'
        elif score >= 0.4:
            return 'medium'
        else:
            return 'low'
    
    def _generate_predictions(self, file: Dict, risk_score: float, risk_level: str) -> List[str]:
        """Generate specific bug predictions for the file"""
        predictions = []
        complexity = file.get('complexity', 0)
        lines = file.get('lines', 0)
        
        if risk_level == 'high':
            predictions.append("High probability of bugs in complex conditional logic")
            if complexity > 7:
                predictions.append("Cyclomatic complexity is very high - likely to have hidden bugs")
            if lines > 500:
                predictions.append("File is too large - hard to maintain and test")
            predictions.append("Consider refactoring before adding new features")
            
        elif risk_level == 'medium':
            predictions.append("Moderate bug risk - review edge cases")
            if complexity > 5:
                predictions.append("Function complexity may hide logic errors")
            predictions.append("Add more unit tests to catch potential issues")
            
        else:
            predictions.append("Low bug probability - maintain current quality")
            predictions.append("Continue with regular code reviews")
        
        # Language-specific predictions
        if file.get('path', '').endswith('.py'):
            predictions.append("Watch for type-related errors (TypeError, ValueError)")
        elif file.get('path', '').endswith(('.js', '.jsx')):
            predictions.append("Watch for undefined variable errors")
            predictions.append("Be careful with async/await error handling")
        
        return predictions[:5]  # Limit to 5 predictions
    
    def _suggest_actions(self, risk_level: str, file: Dict) -> List[str]:
        """Suggest actions based on risk level"""
        actions = []
        
        if risk_level == 'high':
            actions.append("🔴 PRIORITY: Refactor this file immediately")
            actions.append("Add comprehensive unit tests (>80% coverage)")
            actions.append("Break down large functions into smaller ones")
            actions.append("Add detailed error handling and logging")
            actions.append("Request peer code review before merging")
            
        elif risk_level == 'medium':
            actions.append("🟡 Review code for potential edge cases")
            actions.append("Increase test coverage for critical paths")
            actions.append("Consider simplifying complex functions")
            actions.append("Add inline documentation for complex logic")
            
        else:
            actions.append("🟢 Maintain current quality standards")
            actions.append("Continue regular code reviews")
            actions.append("Monitor for future complexity increases")
        
        return actions
    
    def _calculate_risk_distribution(self, risk_analysis: List[Dict]) -> Dict:
        """Calculate percentage distribution of risk levels"""
        total = len(risk_analysis)
        if total == 0:
            return {'high': 0, 'medium': 0, 'low': 0}
        
        high_count = sum(1 for f in risk_analysis if f['risk_level'] == 'high')
        medium_count = sum(1 for f in risk_analysis if f['risk_level'] == 'medium')
        low_count = sum(1 for f in risk_analysis if f['risk_level'] == 'low')
        
        return {
            'high': round((high_count / total) * 100, 1),
            'medium': round((medium_count / total) * 100, 1),
            'low': round((low_count / total) * 100, 1)
        }
    
    def _calculate_maintainability_score(self, risk_analysis: List[Dict]) -> float:
        """Calculate overall maintainability score (0-100)"""
        if not risk_analysis:
            return 100.0
        
        # Average risk score converted to maintainability
        avg_risk = sum(f['risk_score'] for f in risk_analysis) / len(risk_analysis)
        
        # Convert risk (0-1) to maintainability (100-0)
        maintainability = 100 - (avg_risk * 100)
        
        # Penalize for high-risk files
        high_risk_count = sum(1 for f in risk_analysis if f['risk_level'] == 'high')
        penalty = min(20, high_risk_count * 5)
        
        return max(0, round(maintainability - penalty, 1))
    
    def _calculate_confidence(self, risk_analysis: List[Dict]) -> float:
        """Calculate confidence in predictions"""
        if not risk_analysis:
            return 0.0
        
        # More data = higher confidence
        confidence = min(95, len(risk_analysis) * 2)
        
        # Adjust based on risk distribution
        high_risk_ratio = sum(1 for f in risk_analysis if f['risk_level'] == 'high') / len(risk_analysis)
        if high_risk_ratio > 0.5:
            confidence *= 0.8  # Lower confidence with many high-risk files
        
        return round(confidence, 1)
    
    def _generate_recommendations(self, risk_analysis: List[Dict], repo_data: Dict) -> List[Dict]:
        """Generate overall repository recommendations"""
        recommendations = []
        
        # Overall quality recommendation
        high_risk_count = sum(1 for f in risk_analysis if f['risk_level'] == 'high')
        if high_risk_count > 5:
            recommendations.append({
                'priority': 'critical',
                'title': 'Multiple high-risk files detected',
                'description': f'Found {high_risk_count} files with high bug probability. Prioritize refactoring.',
                'action': 'Schedule a code review session for these files'
            })
        
        # Complexity recommendation
        high_complexity_files = [f for f in risk_analysis if f['complexity'] > 7]
        if high_complexity_files:
            recommendations.append({
                'priority': 'high',
                'title': 'High complexity files need attention',
                'description': f'{len(high_complexity_files)} files have very high complexity scores',
                'action': 'Break down complex functions and add documentation'
            })
        
        # Size recommendation
        large_files = [f for f in risk_analysis if f.get('lines_of_code', 0) > 500]
        if large_files:
            recommendations.append({
                'priority': 'medium',
                'title': 'Large files reduce maintainability',
                'description': f'{len(large_files)} files exceed 500 lines',
                'action': 'Split large files into smaller, focused modules'
            })
        
        # Test coverage recommendation (simulated)
        recommendations.append({
            'priority': 'medium',
            'title': 'Improve test coverage',
            'description': 'Test coverage appears low in risk-prone areas',
            'action': 'Add unit tests for high-risk files first'
        })
        
        return recommendations[:5]  # Top 5 recommendations