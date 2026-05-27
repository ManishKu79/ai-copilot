import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import Counter

class PRReviewer:
    def __init__(self):
        self.review_categories = {
            'bug_risk': {'severity': 'high', 'emoji': '🐛'},
            'security': {'severity': 'critical', 'emoji': '🔒'},
            'performance': {'severity': 'medium', 'emoji': '⚡'},
            'style': {'severity': 'low', 'emoji': '💄'},
            'documentation': {'severity': 'low', 'emoji': '📝'},
            'testing': {'severity': 'medium', 'emoji': '✅'},
            'complexity': {'severity': 'medium', 'emoji': '🔄'},
            'best_practice': {'severity': 'low', 'emoji': '✨'}
        }
        
        self.issue_patterns = {
            'todo': {
                'pattern': r'//\s*TODO|#\s*TODO',
                'category': 'documentation',
                'message': 'TODO comment found. Should this be addressed before merging?'
            },
            'console_log': {
                'pattern': r'console\.log\(|print\(',
                'category': 'best_practice',
                'message': 'Debug statement left in code. Remove before merging.'
            },
            'hardcoded_password': {
                'pattern': r'password\s*=\s*["\'][^"\']+["\']',
                'category': 'security',
                'message': 'Hardcoded password detected! Use environment variables.'
            },
            'sql_injection': {
                'pattern': r'execute\(f?["\'].*?\+.*?["\']',
                'category': 'security',
                'message': 'Potential SQL injection vulnerability. Use parameterized queries.'
            },
            'long_function': {
                'pattern': r'def\s+\w+\s*\([^)]*\):\s*\n(?:[^\n]*\n){50,}',
                'category': 'complexity',
                'message': 'Function is too long (>50 lines). Consider refactoring.'
            },
            'no_error_handling': {
                'pattern': r'try:\s*\n.*?\n(?!except)',
                'category': 'bug_risk',
                'message': 'Try block without except. Add error handling.'
            },
            'missing_type_hints': {
                'pattern': r'def\s+\w+\s*\([^:)]*\)\s*:',
                'category': 'best_practice',
                'message': 'Missing type hints. Add type annotations for better code clarity.'
            }
        }
    
    def review_pr(self, diff: str, files_changed: List[str] = None, 
                  pr_title: str = "", pr_description: str = "") -> Dict[str, Any]:
        """Review a pull request and generate feedback"""
        
        # Parse diff
        changes = self._parse_diff(diff, files_changed)
        
        # Find issues in changes
        issues = self._find_issues(diff, changes)
        
        # Generate overall assessment
        assessment = self._generate_assessment(issues, changes)
        
        # Generate inline comments
        inline_comments = self._generate_inline_comments(diff, issues)
        
        # Generate summary
        summary = self._generate_summary(issues, changes, pr_title, pr_description)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(issues, changes)
        
        # Calculate PR score
        score = self._calculate_pr_score(issues, changes)
        
        return {
            'success': True,
            'pr_score': score,
            'grade': self._get_grade(score),
            'summary': summary,
            'issues': issues,
            'issues_by_severity': self._group_by_severity(issues),
            'inline_comments': inline_comments,
            'recommendations': recommendations,
            'assessment': assessment,
            'statistics': {
                'files_changed': len(changes.get('files', [])),
                'additions': changes.get('additions', 0),
                'deletions': changes.get('deletions', 0),
                'issues_found': len(issues),
                'critical_issues': sum(1 for i in issues if i['severity'] == 'critical'),
                'high_issues': sum(1 for i in issues if i['severity'] == 'high')
            }
        }
    
    def _parse_diff(self, diff: str, files_changed: List[str] = None) -> Dict:
        """Parse git diff to extract changes"""
        changes = {
            'files': [],
            'additions': 0,
            'deletions': 0,
            'functions_added': [],
            'functions_modified': [],
            'functions_deleted': [],
            'lines_changed': []
        }
        
        if not diff:
            return changes
        
        lines = diff.split('\n')
        current_file = None
        
        for line in lines:
            if line.startswith('diff --git'):
                # Extract file name
                match = re.search(r'b/(.+)$', line)
                if match:
                    current_file = match.group(1)
                    changes['files'].append(current_file)
            
            elif line.startswith('+') and not line.startswith('+++'):
                changes['additions'] += 1
                # Detect added functions
                func_match = re.search(r'def\s+(\w+)\s*\(', line)
                if func_match:
                    changes['functions_added'].append(func_match.group(1))
                
                js_func_match = re.search(r'function\s+(\w+)\s*\(', line)
                if js_func_match:
                    changes['functions_added'].append(js_func_match.group(1))
            
            elif line.startswith('-') and not line.startswith('---'):
                changes['deletions'] += 1
                # Detect deleted functions
                func_match = re.search(r'def\s+(\w+)\s*\(', line)
                if func_match:
                    changes['functions_deleted'].append(func_match.group(1))
        
        return changes
    
    def _find_issues(self, diff: str, changes: Dict) -> List[Dict]:
        """Find issues in the PR changes"""
        issues = []
        lines = diff.split('\n')
        
        for i, line in enumerate(lines):
            if not line.startswith('+') or line.startswith('+++'):
                continue
            
            # Check each pattern
            for issue_key, issue_info in self.issue_patterns.items():
                if re.search(issue_info['pattern'], line, re.IGNORECASE):
                    issues.append({
                        'line': i + 1,
                        'file': self._get_current_file(lines, i),
                        'code': line[1:].strip()[:100],  # Remove + and truncate
                        'type': issue_key,
                        'category': issue_info['category'],
                        'severity': self.review_categories[issue_info['category']]['severity'],
                        'emoji': self.review_categories[issue_info['category']]['emoji'],
                        'message': issue_info['message'],
                        'suggestion': self._get_suggestion(issue_key)
                    })
        
        # Check for missing tests
        if changes['additions'] > 50 and not self._has_test_changes(lines):
            issues.append({
                'line': 0,
                'file': 'General',
                'code': '',
                'type': 'missing_tests',
                'category': 'testing',
                'severity': 'high',
                'emoji': '✅',
                'message': 'Large code change without corresponding test updates',
                'suggestion': 'Add unit tests for new functionality'
            })
        
        # Check function length
        if len(changes['functions_added']) > 3:
            issues.append({
                'line': 0,
                'file': 'General',
                'code': '',
                'type': 'multiple_functions',
                'category': 'complexity',
                'severity': 'medium',
                'emoji': '🔄',
                'message': f'Added {len(changes["functions_added"])} new functions in one PR',
                'suggestion': 'Consider splitting into smaller, focused PRs'
            })
        
        return issues
    
    def _has_test_changes(self, lines: List[str]) -> bool:
        """Check if PR includes test changes"""
        for line in lines:
            if 'test' in line.lower() and ('+' in line or '-' in line):
                return True
        return False
    
    def _get_current_file(self, lines: List[str], current_line: int) -> str:
        """Get file name from diff"""
        for i in range(current_line, -1, -1):
            if lines[i].startswith('diff --git'):
                match = re.search(r'b/(.+)$', lines[i])
                if match:
                    return match.group(1)
        return 'unknown'
    
    def _get_suggestion(self, issue_type: str) -> str:
        """Get fix suggestion for issue type"""
        suggestions = {
            'todo': 'Either implement the TODO or remove the comment',
            'console_log': 'Remove debug statements or use proper logging',
            'hardcoded_password': 'Move to environment variables or secrets manager',
            'sql_injection': 'Use parameterized queries or an ORM',
            'long_function': 'Break into smaller, focused functions',
            'no_error_handling': 'Add except block or use context managers',
            'missing_type_hints': 'Add type hints for parameters and return values',
            'missing_tests': 'Write unit tests covering the new functionality',
            'multiple_functions': 'Split into multiple smaller PRs for easier review'
        }
        return suggestions.get(issue_type, 'Review and fix the issue')
    
    def _generate_assessment(self, issues: List[Dict], changes: Dict) -> str:
        """Generate overall PR assessment"""
        if not issues:
            return "✅ Excellent! No issues found. Ready to merge."
        
        critical = sum(1 for i in issues if i['severity'] == 'critical')
        high = sum(1 for i in issues if i['severity'] == 'high')
        
        if critical > 0:
            return f"🔴 **Needs Work** - Found {critical} critical issue(s) that must be addressed before merging."
        elif high > 0:
            return f"🟡 **Changes Requested** - Found {high} high severity issue(s) that should be fixed."
        else:
            return f"🟢 **Good Progress** - {len(issues)} minor issue(s) found. Can merge after addressing."
    
    def _generate_inline_comments(self, diff: str, issues: List[Dict]) -> List[Dict]:
        """Generate inline review comments"""
        comments = []
        for issue in issues[:10]:  # Limit to 10 inline comments
            if issue['line'] > 0:
                comments.append({
                    'file': issue['file'],
                    'line': issue['line'],
                    'comment': f"{issue['emoji']} **{issue['category'].upper()}**: {issue['message']}\n\n💡 **Suggestion:** {issue['suggestion']}",
                    'severity': issue['severity']
                })
        return comments
    
    def _generate_summary(self, issues: List[Dict], changes: Dict, 
                          pr_title: str, pr_description: str) -> str:
        """Generate PR summary for review"""
        summary_parts = []
        
        summary_parts.append("## 📋 Pull Request Review Summary\n")
        
        # Overview
        summary_parts.append(f"**Changes:** +{changes['additions']} / -{changes['deletions']} lines")
        summary_parts.append(f"**Files:** {len(changes['files'])} files changed\n")
        
        # Functions changed
        if changes['functions_added']:
            summary_parts.append(f"### ✨ Functions Added")
            for func in changes['functions_added'][:5]:
                summary_parts.append(f"- `{func}()`")
            summary_parts.append("")
        
        if changes['functions_deleted']:
            summary_parts.append(f"### 🗑️ Functions Removed")
            for func in changes['functions_deleted'][:5]:
                summary_parts.append(f"- `{func}()`")
            summary_parts.append("")
        
        # Issues by severity
        if issues:
            summary_parts.append("### 🔍 Issues Found\n")
            by_severity = self._group_by_severity(issues)
            
            if by_severity.get('critical'):
                summary_parts.append("#### 🔴 Critical Issues (Must Fix)")
                for i in by_severity['critical'][:3]:
                    summary_parts.append(f"- `{i['file']}`: {i['message']}")
                summary_parts.append("")
            
            if by_severity.get('high'):
                summary_parts.append("#### 🟠 High Severity")
                for i in by_severity['high'][:3]:
                    summary_parts.append(f"- `{i['file']}`: {i['message']}")
                summary_parts.append("")
            
            if by_severity.get('medium'):
                summary_parts.append("#### 🟡 Medium Severity")
                for i in by_severity['medium'][:3]:
                    summary_parts.append(f"- `{i['file']}`: {i['message']}")
                summary_parts.append("")
        
        return '\n'.join(summary_parts)
    
    def _generate_recommendations(self, issues: List[Dict], changes: Dict) -> List[Dict]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Group by category
        categories = {}
        for issue in issues:
            cat = issue['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(issue)
        
        for category, cat_issues in categories.items():
            if category == 'security':
                recommendations.append({
                    'priority': 'critical',
                    'category': category,
                    'title': 'Security issues detected',
                    'action': 'Fix security vulnerabilities before merging',
                    'details': f'Found {len(cat_issues)} security issue(s)'
                })
            elif category == 'bug_risk':
                recommendations.append({
                    'priority': 'high',
                    'category': category,
                    'title': 'Potential bugs detected',
                    'action': 'Review and add error handling',
                    'details': f'Found {len(cat_issues)} bug risk(s)'
                })
            elif category == 'testing':
                recommendations.append({
                    'priority': 'medium',
                    'category': category,
                    'title': 'Missing or insufficient tests',
                    'action': 'Add unit tests for new functionality',
                    'details': 'Test coverage should be maintained'
                })
        
        if changes['additions'] > 200:
            recommendations.append({
                'priority': 'medium',
                'category': 'size',
                'title': 'Large PR detected',
                'action': 'Consider splitting into smaller PRs',
                'details': f'{changes["additions"]} additions makes review difficult'
            })
        
        return recommendations
    
    def _group_by_severity(self, issues: List[Dict]) -> Dict:
        """Group issues by severity"""
        groups = {'critical': [], 'high': [], 'medium': [], 'low': []}
        for issue in issues:
            severity = issue.get('severity', 'low')
            if severity in groups:
                groups[severity].append(issue)
        return groups
    
    def _calculate_pr_score(self, issues: List[Dict], changes: Dict) -> int:
        """Calculate PR quality score (0-100)"""
        score = 100
        
        # Deduct for issues
        for issue in issues:
            severity = issue.get('severity', 'low')
            if severity == 'critical':
                score -= 25
            elif severity == 'high':
                score -= 15
            elif severity == 'medium':
                score -= 8
            else:
                score -= 3
        
        # Bonus for tests
        if self._has_test_changes([]):  # Simplified
            score = min(100, score + 5)
        
        return max(0, score)
    
    def _get_grade(self, score: int) -> str:
        """Convert score to letter grade"""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'