import radon.complexity as radon_cc
import radon.metrics as radon_metrics
from typing import Dict, List, Any

class RadonAnalyzer:
    """Integration with Radon for cyclomatic complexity"""
    
    def analyze_complexity(self, code: str) -> List[Dict]:
        """Calculate cyclomatic complexity using Radon"""
        try:
            blocks = list(radon_cc.cc_visit(code))
            results = []
            
            for block in blocks:
                complexity = block.complexity
                severity = 'info'
                if complexity > 10:
                    severity = 'error'
                elif complexity > 6:
                    severity = 'warning'
                
                results.append({
                    'name': block.name,
                    'line': block.lineno,
                    'complexity': complexity,
                    'severity': severity,
                    'message': f"Cyclomatic complexity: {complexity}",
                    'suggestion': self.get_complexity_suggestion(complexity)
                })
            
            return results
        except Exception as e:
            print(f"Radon analysis error: {e}")
            return []
    
    def get_complexity_suggestion(self, complexity: int) -> str:
        """Get suggestion based on complexity score"""
        if complexity > 10:
            return "Function is too complex. Break it into smaller functions"
        elif complexity > 6:
            return "Consider simplifying this function"
        else:
            return "Complexity is acceptable"