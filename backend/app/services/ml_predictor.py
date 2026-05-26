import numpy as np
from typing import List, Dict, Any
from collections import defaultdict
import math

class MLBugPredictor:
    """
    Simplified ML-based bug prediction using statistical analysis
    In production, this would use scikit-learn with historical data
    """
    
    def __init__(self):
        # Weights learned from historical data (simulated)
        self.feature_weights = {
            'complexity': 0.35,
            'code_churn': 0.25,
            'developer_experience': 0.15,
            'test_coverage': 0.15,
            'dependency_count': 0.10
        }
        
    def predict_bug_probability(self, file_metrics: Dict) -> float:
        """Predict probability of bugs in a file (0-1)"""
        # Extract features
        features = self._extract_features(file_metrics)
        
        # Calculate weighted probability
        probability = sum(
            features.get(feature, 0) * weight 
            for feature, weight in self.feature_weights.items()
        )
        
        # Add random noise for realism (small variance)
        probability += np.random.normal(0, 0.05)
        
        # Clamp between 0 and 1
        return max(0, min(1, probability))
    
    def _extract_features(self, metrics: Dict) -> Dict[str, float]:
        """Extract numerical features from metrics"""
        complexity = metrics.get('complexity', 1)
        lines = metrics.get('lines', 0)
        
        # Normalize complexity to 0-1 range
        normalized_complexity = min(1, complexity / 10)
        
        # Code churn (simulated based on file size and complexity)
        code_churn = min(1, (complexity * lines) / 5000)
        
        # Developer experience (simulated - would use git blame)
        developer_exp = 0.7  # Default medium experience
        
        # Test coverage (simulated)
        test_coverage = self._estimate_test_coverage(metrics)
        
        # Dependency count impact
        dependency_impact = min(1, metrics.get('import_count', 0) / 20)
        
        return {
            'complexity': normalized_complexity,
            'code_churn': code_churn,
            'developer_experience': developer_exp,
            'test_coverage': test_coverage,
            'dependency_count': dependency_impact
        }
    
    def _estimate_test_coverage(self, metrics: Dict) -> float:
        """Estimate test coverage based on file patterns"""
        file_name = metrics.get('name', '')
        
        # Test files themselves have high coverage
        if 'test' in file_name.lower():
            return 0.9
        
        # Core logic files might have medium coverage
        if any(pattern in file_name.lower() for pattern in ['core', 'base', 'util']):
            return 0.6
        
        # Configuration files
        if 'config' in file_name.lower():
            return 0.8
        
        # Default moderate coverage
        return 0.5
    
    def identify_risk_patterns(self, files_analysis: List[Dict]) -> List[Dict]:
        """Identify patterns that indicate high risk"""
        patterns = []
        
        # Pattern 1: Files with high complexity and many changes
        high_risk_files = [f for f in files_analysis if f.get('risk_score', 0) > 0.7]
        if len(high_risk_files) > 3:
            patterns.append({
                'pattern': 'Multiple high-risk files clustered',
                'impact': 'Systematic code quality issue',
                'suggestion': 'Conduct team code review and establish quality gates'
            })
        
        # Pattern 2: Circular dependencies (simplified)
        # This would require full dependency graph analysis
        
        # Pattern 3: Recently modified high-risk files
        # Would use git history
        
        return patterns