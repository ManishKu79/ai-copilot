from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import math
from collections import defaultdict

class HealthAnalyzer:
    def __init__(self):
        self.quality_weights = {
            'maintainability': 0.30,
            'test_coverage': 0.25,
            'complexity': 0.20,
            'duplication': 0.15,
            'documentation': 0.10
        }
        
    def analyze_health(self, repository_data: Dict, risk_analysis: Dict = None) -> Dict:
        """Comprehensive health analysis of repository"""
        
        files = repository_data.get('files_preview', [])
        structure = repository_data.get('structure', {})
        
        # Calculate individual metrics
        maintainability = self._calculate_maintainability(files, risk_analysis)
        test_coverage = self._estimate_test_coverage(files)
        complexity_score = repository_data.get('complexity_score', 5.0)
        duplication_rate = self._estimate_duplication(files)
        documentation_score = self._calculate_documentation_score(files)
        
        # Calculate overall health score
        overall_score = (
            maintainability * self.quality_weights['maintainability'] +
            test_coverage * self.quality_weights['test_coverage'] +
            (1 - complexity_score / 10) * self.quality_weights['complexity'] +
            (1 - duplication_rate) * self.quality_weights['duplication'] +
            documentation_score * self.quality_weights['documentation']
        ) * 100
        
        # Calculate technical debt
        technical_debt = self._calculate_technical_debt(files, risk_analysis)
        
        # Generate trends (simulated for Phase 8)
        trends = self._generate_trends(overall_score, files)
        
        return {
            'overall_health_score': round(overall_score, 2),
            'grade': self._get_health_grade(overall_score),
            'metrics': {
                'maintainability': round(maintainability * 100, 2),
                'test_coverage': round(test_coverage * 100, 2),
                'complexity_score': complexity_score,
                'duplication_rate': round(duplication_rate * 100, 2),
                'documentation_score': round(documentation_score * 100, 2)
            },
            'technical_debt': technical_debt,
            'trends': trends,
            'recommendations': self._generate_recommendations(
                maintainability, test_coverage, complexity_score, duplication_rate, documentation_score
            ),
            'benchmarks': self._get_benchmarks(overall_score)
        }
    
    def _calculate_maintainability(self, files: List[Dict], risk_analysis: Dict = None) -> float:
        """Calculate maintainability index (0-1)"""
        if not files:
            return 0.7  # Default
        
        total_maintainability = 0
        valid_files = 0
        
        for file in files:
            if file.get('error'):
                continue
            
            complexity = file.get('complexity', 5)
            lines = file.get('lines', 100)
            
            # Calculate file-level maintainability
            # Lower complexity and fewer lines = better maintainability
            file_score = max(0, min(1, 1 - (complexity / 20) - (lines / 2000)))
            total_maintainability += file_score
            valid_files += 1
        
        if valid_files == 0:
            return 0.7
        
        return total_maintainability / valid_files
    
    def _estimate_test_coverage(self, files: List[Dict]) -> float:
        """Estimate test coverage based on file patterns"""
        if not files:
            return 0.5
        
        test_files = 0
        source_files = 0
        
        for file in files:
            name = file.get('name', '').lower()
            if 'test' in name or 'spec' in name:
                test_files += 1
            elif name.endswith(('.py', '.js', '.ts', '.jsx', '.tsx')):
                source_files += 1
        
        if source_files == 0:
            return 0.5
        
        # Estimate coverage based on test-to-source ratio
        ratio = min(1, test_files / source_files)
        # Base coverage of 60% + additional from ratio
        coverage = 0.6 + (ratio * 0.3)
        
        return min(0.95, coverage)
    
    def _estimate_duplication(self, files: List[Dict]) -> float:
        """Estimate code duplication rate (0-1)"""
        if len(files) < 5:
            return 0.1  # Low duplication for small projects
        
        # Simulate duplication detection
        # In production, use actual duplication analysis tools
        duplication_indicators = 0
        
        for file in files:
            name = file.get('name', '')
            if any(pattern in name.lower() for pattern in ['copy', 'duplicate', 'clone']):
                duplication_indicators += 1
        
        # Estimate duplication rate
        rate = min(0.3, duplication_indicators / len(files))
        
        return rate
    
    def _calculate_documentation_score(self, files: List[Dict]) -> float:
        """Calculate documentation coverage score"""
        if not files:
            return 0.5
        
        doc_files = 0
        has_readme = False
        has_api_docs = False
        
        for file in files:
            name = file.get('name', '').lower()
            if name == 'readme.md' or name == 'readme':
                has_readme = True
                doc_files += 1
            elif 'doc' in name or 'api' in name and name.endswith('.md'):
                has_api_docs = True
                doc_files += 1
        
        score = 0.3  # Base score
        if has_readme:
            score += 0.4
        if has_api_docs:
            score += 0.3
        
        return min(1.0, score)
    
    def _calculate_technical_debt(self, files: List[Dict], risk_analysis: Dict = None) -> Dict:
        """Calculate technical debt estimation"""
        total_debt_hours = 0
        debt_items = []
        
        for file in files:
            complexity = file.get('complexity', 1)
            lines = file.get('lines', 0)
            
            # Estimate refactoring time based on complexity
            if complexity > 7:
                hours = complexity * 2
                total_debt_hours += hours
                debt_items.append({
                    'file': file.get('name', 'unknown'),
                    'complexity': complexity,
                    'estimated_hours': hours,
                    'priority': 'high'
                })
            elif complexity > 4:
                hours = complexity
                total_debt_hours += hours
                debt_items.append({
                    'file': file.get('name', 'unknown'),
                    'complexity': complexity,
                    'estimated_hours': hours,
                    'priority': 'medium'
                })
        
        # Convert to business metrics
        debt_days = total_debt_hours / 8  # 8-hour workday
        debt_cost = total_debt_hours * 100  # $100/hour estimated
        
        return {
            'total_hours': round(total_debt_hours, 1),
            'total_days': round(debt_days, 1),
            'estimated_cost': round(debt_cost, 2),
            'debt_items': debt_items[:10],  # Top 10 debt items
            'severity': self._get_debt_severity(total_debt_hours)
        }
    
    def _get_debt_severity(self, hours: float) -> str:
        """Determine technical debt severity"""
        if hours > 100:
            return 'critical'
        elif hours > 50:
            return 'high'
        elif hours > 20:
            return 'medium'
        else:
            return 'low'
    
    def _generate_trends(self, current_score: float, files: List[Dict]) -> Dict:
        """Generate simulated trend data"""
        # Simulate last 6 months of data
        trends = []
        base_score = current_score - 15  # Start lower
        dates = []
        
        for i in range(6):
            date = datetime.now() - timedelta(days=(5 - i) * 30)
            dates.append(date.strftime('%b %Y'))
            
            # Simulate improvement over time
            variation = (i * 3) + (i * 2 if i > 2 else 0)
            score = min(100, base_score + variation + (i * 2))
            trends.append(round(score, 2))
        
        # Generate weekly trend for last 4 weeks
        weekly = []
        weekly_labels = []
        for i in range(4):
            week_score = current_score - (3 - i) * 1.5
            weekly.append(round(max(0, min(100, week_score)), 2))
            weekly_labels.append(f"Week {i+1}")
        
        return {
            'monthly': {
                'labels': dates,
                'values': trends
            },
            'weekly': {
                'labels': weekly_labels,
                'values': weekly
            },
            'improvement_rate': round((trends[-1] - trends[0]) / max(1, trends[0]) * 100, 1) if trends else 0
        }
    
    def _generate_recommendations(self, maintainability: float, coverage: float, 
                                  complexity: float, duplication: float, docs: float) -> List[Dict]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if maintainability < 0.6:
            recommendations.append({
                'priority': 'high',
                'category': 'maintainability',
                'title': 'Improve code maintainability',
                'description': 'Code is difficult to maintain and modify',
                'action': 'Refactor complex functions and reduce file sizes',
                'impact': 'Reduces bug risk by up to 40%'
            })
        
        if coverage < 0.7:
            recommendations.append({
                'priority': 'high',
                'category': 'testing',
                'title': 'Increase test coverage',
                'description': f'Current coverage is {round(coverage * 100)}%, below recommended 70%',
                'action': 'Add unit tests for critical paths and edge cases',
                'impact': 'Catches bugs before production deployment'
            })
        
        if complexity > 6:
            recommendations.append({
                'priority': 'medium',
                'category': 'complexity',
                'title': 'Reduce code complexity',
                'description': f'Average complexity is {round(complexity, 1)}/10',
                'action': 'Break down complex functions and use early returns',
                'impact': 'Makes code easier to understand and test'
            })
        
        if duplication > 0.15:
            recommendations.append({
                'priority': 'medium',
                'category': 'duplication',
                'title': 'Eliminate code duplication',
                'description': f'Duplication rate is {round(duplication * 100)}%',
                'action': 'Extract repeated code into shared functions or utilities',
                'impact': 'Reduces maintenance effort by 25%'
            })
        
        if docs < 0.6:
            recommendations.append({
                'priority': 'low',
                'category': 'documentation',
                'title': 'Improve documentation',
                'description': 'Missing README or API documentation',
                'action': 'Add README.md and document public APIs',
                'impact': 'Helps new developers onboard faster'
            })
        
        return recommendations
    
    def _get_health_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        if score >= 90:
            return 'A+'
        elif score >= 80:
            return 'A'
        elif score >= 70:
            return 'B'
        elif score >= 60:
            return 'C'
        elif score >= 50:
            return 'D'
        else:
            return 'F'
    
    def _get_benchmarks(self, score: float) -> Dict:
        """Get industry benchmarks for comparison"""
        benchmarks = {
            'top_25_percentile': 85,
            'median': 68,
            'bottom_25_percentile': 45
        }
        
        percentile = 'top'
        if score < benchmarks['median']:
            percentile = 'bottom'
        elif score < benchmarks['top_25_percentile']:
            percentile = 'average'
        
        return {
            'percentile': percentile,
            'compared_to_peers': f"Your score is {'above' if score > benchmarks['median'] else 'below'} the industry median",
            'benchmarks': benchmarks
        }