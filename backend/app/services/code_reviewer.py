import ast
import re
from typing import List, Dict, Any, Optional
from pathlib import Path

class CodeReviewer:
    def __init__(self):
        self.patterns = {
            'todo': r'#\s*TODO|//\s*TODO',
            'fixme': r'#\s*FIXME|//\s*FIXME',
            'print': r'print\(|console\.log\(|console\.error\(',
            'debugger': r'debugger;',
            'password': r'password\s*=\s*[\'"]\S+[\'"]|secret\s*=\s*[\'"]\S+[\'"]',
            'api_key': r'api_key\s*=\s*[\'"]\S+[\'"]|apikey\s*=\s*[\'"]\S+[\'"]',
        }
    
    def review_code(self, code: str, language: str = 'python') -> Dict[str, Any]:
        """Main entry point for code review"""
        issues = []
        
        if language == 'python':
            issues = self.review_python(code)
        elif language in ['javascript', 'typescript']:
            issues = self.review_javascript(code)
        else:
            issues = self.review_generic(code)
        
        # Calculate overall score
        severity_scores = {'error': 10, 'warning': 5, 'info': 1}
        total_score = sum(severity_scores.get(issue['severity'], 0) for issue in issues)
        max_score = max(1, len(issues) * 10)
        quality_score = max(0, 100 - min(100, (total_score / max_score) * 100))
        
        return {
            'issues': issues,
            'quality_score': round(quality_score, 2),
            'total_issues': len(issues),
            'severity_breakdown': {
                'error': sum(1 for i in issues if i['severity'] == 'error'),
                'warning': sum(1 for i in issues if i['severity'] == 'warning'),
                'info': sum(1 for i in issues if i['severity'] == 'info')
            }
        }
    
    def review_python(self, code: str) -> List[Dict]:
        """Review Python code using AST"""
        issues = []
        
        # Check for common issues with regex
        issues.extend(self.check_regex_patterns(code, 'python'))
        
        # AST-based analysis
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                # Check function length
                if isinstance(node, ast.FunctionDef):
                    if len(node.body) > 30:
                        issues.append({
                            'line': node.lineno,
                            'severity': 'warning',
                            'category': 'function_length',
                            'message': f"Function '{node.name}' is too long ({len(node.body)} lines)",
                            'suggestion': 'Break this function into smaller, focused functions'
                        })
                    
                    # Check too many arguments
                    if len(node.args.args) > 5:
                        issues.append({
                            'line': node.lineno,
                            'severity': 'warning',
                            'category': 'too_many_arguments',
                            'message': f"Function '{node.name}' has {len(node.args.args)} arguments",
                            'suggestion': 'Consider using a configuration object or reducing parameters'
                        })
                
                # Check nested depth
                elif isinstance(node, (ast.If, ast.While, ast.For)):
                    depth = self.get_nesting_depth(node, tree)
                    if depth > 3:
                        issues.append({
                            'line': node.lineno,
                            'severity': 'error',
                            'category': 'deep_nesting',
                            'message': f'Deep nesting detected (depth: {depth})',
                            'suggestion': 'Refactor using guard clauses or extract nested logic into functions'
                        })
                
                # Check bare except
                elif isinstance(node, ast.ExceptHandler):
                    if node.type is None:
                        issues.append({
                            'line': node.lineno,
                            'severity': 'error',
                            'category': 'bare_except',
                            'message': 'Bare except clause catches all exceptions',
                            'suggestion': 'Specify exception types to catch (e.g., except ValueError:)'
                        })
                
                # Check for mutable default arguments
                elif isinstance(node, ast.FunctionDef):
                    for default in node.args.defaults:
                        if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                            issues.append({
                                'line': node.lineno,
                                'severity': 'warning',
                                'category': 'mutable_default',
                                'message': f"Function '{node.name}' has mutable default argument",
                                'suggestion': 'Use None as default and create mutable inside function'
                            })
                            break
                
                # Check for unused variables (simplified)
                elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                    if node.id in ['i', 'j', 'k', 'x', 'y', 'temp', 'tmp']:
                        if not self.is_variable_used(node.id, tree):
                            issues.append({
                                'line': node.lineno,
                                'severity': 'info',
                                'category': 'unclear_naming',
                                'message': f"Variable '{node.id}' has unclear meaning",
                                'suggestion': 'Use descriptive variable names'
                            })
        
        except SyntaxError as e:
            issues.append({
                'line': e.lineno or 0,
                'severity': 'error',
                'category': 'syntax_error',
                'message': f'Syntax error: {str(e)}',
                'suggestion': 'Fix the syntax error before proceeding'
            })
        
        return issues
    
    def review_javascript(self, code: str) -> List[Dict]:
        """Review JavaScript/TypeScript code"""
        issues = []
        
        # Check for common patterns
        issues.extend(self.check_regex_patterns(code, 'javascript'))
        
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for var usage (should use let/const)
            if re.search(r'\bvar\s+', line):
                issues.append({
                    'line': i,
                    'severity': 'warning',
                    'category': 'var_usage',
                    'message': 'Using `var` for variable declaration',
                    'suggestion': 'Use `const` for constants and `let` for variables that change'
                })
            
            # Check for == instead of ===
            if '==' in line and '!=' in line:
                issues.append({
                    'line': i,
                    'severity': 'error',
                    'category': 'loose_equality',
                    'message': 'Using loose equality (== or !=)',
                    'suggestion': 'Use strict equality (=== or !==) to avoid type coercion'
                })
            
            # Check line length
            if len(line) > 100:
                issues.append({
                    'line': i,
                    'severity': 'info',
                    'category': 'line_length',
                    'message': f'Line is too long ({len(line)} characters)',
                    'suggestion': 'Break long lines for better readability'
                })
            
            # Check for console.log in production code
            if 'console.log' in line and '//' not in line.split('console.log')[0]:
                issues.append({
                    'line': i,
                    'severity': 'warning',
                    'category': 'console_log',
                    'message': 'Console.log statement found',
                    'suggestion': 'Remove debug console statements in production code'
                })
        
        # Check for callback hell (simplified)
        if code.count('})') > 3:
            issues.append({
                'line': 0,
                'severity': 'warning',
                'category': 'callback_hell',
                'message': 'Deep callback nesting detected',
                'suggestion': 'Use Promises or async/await for better readability'
            })
        
        return issues
    
    def review_generic(self, code: str) -> List[Dict]:
        """Generic review for other languages"""
        issues = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for TODO/FIXME
            if re.search(self.patterns['todo'], line, re.IGNORECASE):
                issues.append({
                    'line': i,
                    'severity': 'info',
                    'category': 'todo',
                    'message': 'TODO comment found',
                    'suggestion': 'Address TODO items before finalizing code'
                })
            
            # Check line length
            if len(line) > 100:
                issues.append({
                    'line': i,
                    'severity': 'info',
                    'category': 'line_length',
                    'message': f'Line is too long ({len(line)} characters)',
                    'suggestion': 'Break long lines for better readability'
                })
            
            # Check for trailing whitespace
            if line.endswith(' ') or line.endswith('\t'):
                issues.append({
                    'line': i,
                    'severity': 'info',
                    'category': 'trailing_whitespace',
                    'message': 'Trailing whitespace detected',
                    'suggestion': 'Remove trailing whitespace'
                })
        
        return issues
    
    def check_regex_patterns(self, code: str, language: str) -> List[Dict]:
        """Check code against common regex patterns"""
        issues = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for TODO/FIXME
            if re.search(self.patterns['todo'], line, re.IGNORECASE):
                issues.append({
                    'line': i,
                    'severity': 'info',
                    'category': 'todo',
                    'message': 'TODO comment found',
                    'suggestion': 'Track TODO items or implement required changes'
                })
            
            if re.search(self.patterns['fixme'], line, re.IGNORECASE):
                issues.append({
                    'line': i,
                    'severity': 'warning',
                    'category': 'fixme',
                    'message': 'FIXME comment found',
                    'suggestion': 'Fix the identified issue before merging'
                })
            
            # Check for print/debug statements
            if re.search(self.patterns['print'], line):
                if '//' not in line.split('print')[0] if '//' in line else True:
                    issues.append({
                        'line': i,
                        'severity': 'warning',
                        'category': 'debug_statement',
                        'message': 'Debug print statement found',
                        'suggestion': 'Remove debug statements or use proper logging'
                    })
            
            # Check for hardcoded secrets (basic)
            if re.search(self.patterns['password'], line, re.IGNORECASE):
                issues.append({
                    'line': i,
                    'severity': 'error',
                    'category': 'hardcoded_secret',
                    'message': 'Possible hardcoded password or secret',
                    'suggestion': 'Use environment variables or secrets manager'
                })
        
        return issues
    
    def get_nesting_depth(self, node: ast.AST, tree: ast.AST) -> int:
        """Calculate nesting depth of a node"""
        depth = 0
        current = node
        
        # Simplified depth calculation
        for parent in ast.walk(tree):
            if hasattr(parent, 'body') and current in parent.body:
                depth += 1
                current = parent
        
        return depth
    
    def is_variable_used(self, var_name: str, tree: ast.AST) -> bool:
        """Check if a variable is used after declaration"""
        # Simplified check - always return True for now
        # Full implementation would track variable usage
        return True

    def detect_duplicate_code(self, code: str) -> List[Dict]:
        """Detect duplicate code blocks (simplified)"""
        lines = [line.strip() for line in code.split('\n') if line.strip()]
        duplicates = []
        
        # Look for repeated line patterns
        line_count = {}
        for i, line in enumerate(lines):
            if len(line) > 20:  # Only check substantial lines
                if line in line_count:
                    line_count[line].append(i)
                else:
                    line_count[line] = [i]
        
        for line, positions in line_count.items():
            if len(positions) > 1:
                duplicates.append({
                    'line': positions[0] + 1,
                    'severity': 'warning',
                    'category': 'duplicate_code',
                    'message': f'Duplicate code found (appears {len(positions)} times)',
                    'suggestion': 'Extract repeated code into a reusable function'
                })
                break  # Report first duplicate only
        
        return duplicates