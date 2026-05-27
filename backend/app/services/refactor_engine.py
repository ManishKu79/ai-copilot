import ast
import re
from typing import List, Dict, Any, Optional
from pathlib import Path

class RefactorEngine:
    def __init__(self):
        self.suggestion_types = {
            'function_too_long': {
                'severity': 'high',
                'category': 'structure',
                'title': 'Function is too long',
                'template': 'Function "{name}" has {lines} lines. Long functions are hard to understand and test.'
            },
            'too_many_parameters': {
                'severity': 'medium',
                'category': 'design',
                'title': 'Too many parameters',
                'template': 'Function "{name}" has {count} parameters. Too many parameters make functions harder to use.'
            },
            'deep_nesting': {
                'severity': 'high',
                'category': 'complexity',
                'title': 'Deep nesting detected',
                'template': 'Deep nesting level {depth} detected. Nested code is harder to follow and maintain.'
            },
            'duplicate_code': {
                'severity': 'medium',
                'category': 'duplication',
                'title': 'Duplicate code block',
                'template': 'Similar code block found in multiple places. Duplication increases maintenance cost.'
            },
            'large_file': {
                'severity': 'high',
                'category': 'structure',
                'title': 'File is too large',
                'message': 'File has {lines} lines. Large files are harder to navigate and maintain.'
            },
            'magic_numbers': {
                'severity': 'low',
                'category': 'readability',
                'title': 'Magic numbers detected',
                'template': 'Magic number "{value}" found. Use named constants for better readability.'
            },
            'complex_condition': {
                'severity': 'medium',
                'category': 'complexity',
                'title': 'Complex conditional',
                'template': 'Complex condition with {operators} operators. Simplify for better readability.'
            },
            'god_class': {
                'severity': 'high',
                'category': 'design',
                'title': 'God class detected',
                'template': 'Class "{name}" has {methods} methods and {lines} lines. Consider splitting into smaller classes.'
            }
        }
    
    def analyze_code(self, code: str, file_path: str = "", language: str = "python") -> List[Dict]:
        """Analyze code and return refactoring suggestions"""
        suggestions = []
        
        if language == "python":
            suggestions = self._analyze_python(code, file_path)
        elif language in ["javascript", "typescript"]:
            suggestions = self._analyze_javascript(code, file_path)
        else:
            suggestions = self._analyze_generic(code, file_path)
        
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        suggestions.sort(key=lambda x: severity_order.get(x.get('severity', 'low'), 4))
        
        return suggestions
    
    def analyze_from_metrics(self, files: List[Dict]) -> Dict:
        """Analyze repository using available metrics (when full code isn't available)"""
        suggestions = []
        complexity_score = 0
        
        for file in files:
            if file.get('error'):
                continue
            
            file_name = file.get('name', 'unknown')
            file_path = file.get('path', file_name)
            complexity = file.get('complexity', 0)
            lines = file.get('lines', 0)
            extension = file.get('extension', '')
            
            # Skip documentation and config files
            if extension in ['.md', '.txt', '.json', '.yml', '.yaml']:
                continue
            
            # Check for large files
            if lines > 300:
                suggestions.append({
                    'line': 1,
                    'severity': 'high',
                    'category': 'structure',
                    'title': 'File is too large',
                    'message': f'File "{file_name}" has {lines} lines. Large files are harder to maintain.',
                    'suggestion': 'Split this file into multiple smaller modules based on functionality.',
                    'code_example': self._get_example('large_file'),
                    'file': file_path,
                    'file_name': file_name,
                    'type': 'large_file'
                })
                complexity_score += 10
            elif lines > 200:
                suggestions.append({
                    'line': 1,
                    'severity': 'medium',
                    'category': 'structure',
                    'title': 'File is moderately large',
                    'message': f'File "{file_name}" has {lines} lines. Consider breaking it down.',
                    'suggestion': 'Split related functionality into separate modules.',
                    'code_example': self._get_example('split_file'),
                    'file': file_path,
                    'file_name': file_name,
                    'type': 'large_file'
                })
                complexity_score += 5
            
            # Check for high complexity files
            if complexity > 7:
                suggestions.append({
                    'line': 1,
                    'severity': 'high',
                    'category': 'complexity',
                    'title': 'High complexity detected',
                    'message': f'File "{file_name}" has complexity score {complexity}/10. High complexity indicates potential bugs.',
                    'suggestion': 'Break down complex functions into smaller, focused functions.',
                    'code_example': self._get_example('high_complexity'),
                    'file': file_path,
                    'file_name': file_name,
                    'type': 'high_complexity'
                })
                complexity_score += 10
            elif complexity > 5:
                suggestions.append({
                    'line': 1,
                    'severity': 'medium',
                    'category': 'complexity',
                    'title': 'Moderate complexity',
                    'message': f'File "{file_name}" has complexity score {complexity}/10. Consider simplifying.',
                    'suggestion': 'Review complex functions and look for simplification opportunities.',
                    'code_example': self._get_example('moderate_complexity'),
                    'file': file_path,
                    'file_name': file_name,
                    'type': 'moderate_complexity'
                })
                complexity_score += 5
            
            # Check for utility file bloat
            if any(pattern in file_name.lower() for pattern in ['util', 'helper', 'common', 'base']):
                if lines > 150:
                    suggestions.append({
                        'line': 1,
                        'severity': 'medium',
                        'category': 'structure',
                        'title': 'Utility file may be too broad',
                        'message': f'Utility file "{file_name}" has {lines} lines. Utility files often become dumping grounds.',
                        'suggestion': 'Split into more focused modules (string_utils, file_utils, etc.)',
                        'code_example': self._get_example('split_utils'),
                        'file': file_path,
                        'file_name': file_name,
                        'type': 'split_utils'
                    })
                    complexity_score += 5
            
            # Check for potential duplicate file names
            if any(pattern in file_name.lower() for pattern in ['_copy', '_duplicate', 'copy_', 'dup_']):
                suggestions.append({
                    'line': 1,
                    'severity': 'medium',
                    'category': 'duplication',
                    'title': 'Potential duplicate file',
                    'message': f'File "{file_name}" appears to be a copy of another file.',
                    'suggestion': 'Consolidate duplicate files and extract common code into shared modules.',
                    'code_example': self._get_example('remove_duplicates'),
                    'file': file_path,
                    'file_name': file_name,
                    'type': 'duplicate_file'
                })
                complexity_score += 5
            
            # Check for test file naming issues
            if 'test' in file_name.lower() and not file_name.startswith('test_') and not file_name.endswith('_test'):
                suggestions.append({
                    'line': 1,
                    'severity': 'low',
                    'category': 'convention',
                    'title': 'Test file naming convention',
                    'message': f'Test file "{file_name}" should follow naming conventions.',
                    'suggestion': 'Rename test files to start with "test_" or end with "_test".',
                    'code_example': '# Rename test_utils.py or utils_test.py',
                    'file': file_path,
                    'file_name': file_name,
                    'type': 'test_naming'
                })
                complexity_score += 2
        
        # Add helpful suggestions if no major issues found
        if not suggestions:
            suggestions = self._get_helpful_suggestions()
        elif len(suggestions) < 3:
            # Add some helpful suggestions alongside real ones
            helpful = self._get_helpful_suggestions()
            suggestions.extend(helpful[:2])
        
        # Sort by severity
        severity_order = {'high': 0, 'medium': 1, 'low': 2}
        suggestions.sort(key=lambda x: severity_order.get(x.get('severity', 'low'), 3))
        
        # Remove duplicates based on title and file
        unique_suggestions = []
        seen = set()
        for s in suggestions:
            key = f"{s['title']}_{s.get('file_name', '')}"
            if key not in seen:
                seen.add(key)
                unique_suggestions.append(s)
        
        return {
            'total_suggestions': len(unique_suggestions),
            'high_severity': sum(1 for s in unique_suggestions if s['severity'] == 'high'),
            'medium_severity': sum(1 for s in unique_suggestions if s['severity'] == 'medium'),
            'low_severity': sum(1 for s in unique_suggestions if s['severity'] == 'low'),
            'suggestions': unique_suggestions[:20],
            'refactoring_priority': 'high' if complexity_score > 30 else 'medium' if complexity_score > 15 else 'low',
            'estimated_effort_hours': round(max(1, complexity_score / 5), 1),
            'categories': self._group_by_category(unique_suggestions)
        }
    
    def _get_example(self, example_type: str) -> str:
        """Get code example for a specific refactoring type"""
        examples = {
            'large_file': '''
# Before: Single large file with everything (500+ lines)

# After: Split into modules
# user_service.py
class UserService:
    def get_user(self, user_id):
        # User-specific logic
        pass

# order_service.py  
class OrderService:
    def get_order(self, order_id):
        # Order-specific logic
        pass

# main.py
from user_service import UserService
from order_service import OrderService
''',
            'split_file': '''
# Before: Mixed responsibilities in one file

# After: Separate concerns
# database.py - Database operations
# validators.py - Input validation
# formatters.py - Output formatting
''',
            'high_complexity': '''
# Before: Complex nested logic
def process_data(data):
    result = []
    for item in data:
        if item['active']:
            if item['type'] == 'user':
                for sub in item['items']:
                    if sub['valid']:
                        result.append(process(sub))
    return result

# After: Extract functions
def is_active_user(item):
    return item['active'] and item['type'] == 'user'

def process_valid_items(item):
    return [process(sub) for sub in item['items'] if sub['valid']]

def process_data(data):
    result = []
    for item in data:
        if is_active_user(item):
            result.extend(process_valid_items(item))
    return result
''',
            'moderate_complexity': '''
# Before: Hard to follow
def calculate_price(price, tax, discount, shipping):
    after_tax = price * (1 + tax)
    after_discount = after_tax * (1 - discount)
    total = after_discount + shipping
    return total

# After: Clear step-by-step
def calculate_price(price, tax_rate, discount_rate, shipping_cost):
    price_with_tax = price * (1 + tax_rate)
    price_with_discount = price_with_tax * (1 - discount_rate)
    total_price = price_with_discount + shipping_cost
    return total_price
''',
            'split_utils': '''
# Before: utils.py (500+ lines)
def string_helper(): pass
def file_helper(): pass
def date_helper(): pass
def math_helper(): pass

# After: Split into modules
# utils/string_utils.py
def format_string(): pass

# utils/file_utils.py  
def read_file(): pass

# utils/date_utils.py
def format_date(): pass
''',
            'remove_duplicates': '''
# Before: Duplicate code
# file1.py
def calculate_total(prices):
    total = 0
    for p in prices:
        total += p
    return total

# file2.py  
def calculate_sum(prices):
    total = 0
    for p in prices:
        total += p
    return total

# After: Shared utility
# utils/math_utils.py
def calculate_sum(numbers):
    return sum(numbers)

# file1.py
from utils.math_utils import calculate_sum
'''
        }
        return examples.get(example_type, '# Review and refactor this code for better maintainability')
    
    def _get_helpful_suggestions(self) -> List[Dict]:
        """Get helpful suggestions for any codebase"""
        return [
            {
                'line': 1,
                'severity': 'low',
                'category': 'documentation',
                'title': 'Add docstrings to functions',
                'message': 'Documentation helps others understand your code and serves as inline documentation.',
                'suggestion': 'Add docstrings to all public functions explaining parameters, return values, and side effects.',
                'code_example': '''
def calculate_total(items, tax_rate=0.1):
    """Calculate total price including tax.
    
    Args:
        items: List of item objects with 'price' attribute
        tax_rate: Tax rate as decimal (default 0.1 for 10%)
        
    Returns:
        float: Total sum including tax
        
    Example:
        >>> items = [Item(price=10), Item(price=20)]
        >>> calculate_total(items)
        33.0
    """
    subtotal = sum(item.price for item in items)
    return subtotal * (1 + tax_rate)
''',
                'file': 'suggestion.py',
                'file_name': 'suggestion.py',
                'type': 'add_docstrings'
            },
            {
                'line': 1,
                'severity': 'low',
                'category': 'testing',
                'title': 'Add unit tests',
                'message': 'Tests help catch bugs, document expected behavior, and enable confident refactoring.',
                'suggestion': 'Add unit tests for critical functionality and edge cases.',
                'code_example': '''
import unittest

class TestCalculator(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.calc = Calculator()
    
    def test_add_positive_numbers(self):
        """Test adding two positive numbers"""
        result = self.calc.add(2, 3)
        self.assertEqual(result, 5)
    
    def test_add_negative_numbers(self):
        """Test adding two negative numbers"""
        result = self.calc.add(-1, -2)
        self.assertEqual(result, -3)
    
    def test_divide_by_zero(self):
        """Test division by zero raises exception"""
        with self.assertRaises(ValueError):
            self.calc.divide(10, 0)

if __name__ == '__main__':
    unittest.main()
''',
                'file': 'suggestion.py',
                'file_name': 'suggestion.py',
                'type': 'add_tests'
            },
            {
                'line': 1,
                'severity': 'low',
                'category': 'error_handling',
                'title': 'Add proper error handling',
                'message': 'Graceful error handling improves user experience and prevents crashes.',
                'suggestion': 'Use try/except blocks and validate inputs before processing.',
                'code_example': '''
def divide_numbers(a, b):
    """Safe division with error handling"""
    try:
        # Input validation
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            raise TypeError("Arguments must be numbers")
        
        # Operation with error handling
        if b == 0:
            raise ValueError("Cannot divide by zero")
        
        return a / b
        
    except TypeError as e:
        print(f"Type error: {e}")
        return None
    except ValueError as e:
        print(f"Value error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
''',
                'file': 'suggestion.py',
                'file_name': 'suggestion.py',
                'type': 'error_handling'
            },
            {
                'line': 1,
                'severity': 'low',
                'category': 'performance',
                'title': 'Optimize loops and data structures',
                'message': 'Efficient code runs faster and uses less memory.',
                'suggestion': 'Use list comprehensions, avoid repeated calculations, and choose appropriate data structures.',
                'code_example': '''
# Before: Inefficient
def find_duplicates(items):
    duplicates = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] == items[j] and items[i] not in duplicates:
                duplicates.append(items[i])
    return duplicates

# After: Optimized using sets
def find_duplicates(items):
    seen = set()
    duplicates = set()
    for item in items:
        if item in seen:
            duplicates.add(item)
        else:
            seen.add(item)
    return list(duplicates)
''',
                'file': 'suggestion.py',
                'file_name': 'suggestion.py',
                'type': 'performance'
            }
        ]
    
    def _analyze_python(self, code: str, file_path: str) -> List[Dict]:
        """Analyze Python code using AST"""
        suggestions = []
        lines = code.split('\n')
        
        if len(lines) > 500:
            suggestions.append(self._create_suggestion(
                'large_file',
                {'lines': len(lines)},
                line=1,
                file_path=file_path
            ))
        
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_lines = node.end_lineno - node.lineno if node.end_lineno else 0
                    if func_lines > 50:
                        suggestions.append(self._create_suggestion(
                            'function_too_long',
                            {'name': node.name, 'lines': func_lines},
                            line=node.lineno,
                            file_path=file_path
                        ))
                    
                    num_params = len(node.args.args)
                    if num_params > 5:
                        suggestions.append(self._create_suggestion(
                            'too_many_parameters',
                            {'name': node.name, 'count': num_params},
                            line=node.lineno,
                            file_path=file_path
                        ))
                    
                    depth = self._get_nesting_depth(node)
                    if depth > 4:
                        suggestions.append(self._create_suggestion(
                            'deep_nesting',
                            {'depth': depth},
                            line=node.lineno,
                            file_path=file_path
                        ))
                
                elif isinstance(node, ast.ClassDef):
                    methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                    class_lines = node.end_lineno - node.lineno if node.end_lineno else 0
                    if len(methods) > 15 or class_lines > 300:
                        suggestions.append(self._create_suggestion(
                            'god_class',
                            {'name': node.name, 'methods': len(methods), 'lines': class_lines},
                            line=node.lineno,
                            file_path=file_path
                        ))
                
                elif isinstance(node, ast.Constant):
                    if isinstance(node.value, (int, float)) and not self._is_allowed_number(node.value, code, node.lineno):
                        if node.value not in [0, 1, -1, 100]:
                            suggestions.append(self._create_suggestion(
                                'magic_numbers',
                                {'value': node.value},
                                line=node.lineno,
                                file_path=file_path
                            ))
                
                elif isinstance(node, ast.If):
                    condition_complexity = self._get_condition_complexity(node.test)
                    if condition_complexity > 3:
                        suggestions.append(self._create_suggestion(
                            'complex_condition',
                            {'operators': condition_complexity},
                            line=node.lineno,
                            file_path=file_path
                        ))
        
        except SyntaxError:
            pass
        
        duplicates = self._find_duplicate_blocks(code)
        for dup in duplicates[:3]:
            suggestions.append(self._create_suggestion(
                'duplicate_code',
                {},
                line=dup['line'],
                file_path=file_path,
                custom_message=f"Similar code found on lines {dup['line']} and {dup['duplicate_line']}"
            ))
        
        return suggestions
    
    def _analyze_javascript(self, code: str, file_path: str) -> List[Dict]:
        """Analyze JavaScript/TypeScript code"""
        suggestions = []
        lines = code.split('\n')
        
        if len(lines) > 500:
            suggestions.append(self._create_suggestion(
                'large_file',
                {'lines': len(lines)},
                line=1,
                file_path=file_path
            ))
        
        for i, line in enumerate(lines, 1):
            if len(line) > 120:
                suggestions.append({
                    'line': i,
                    'severity': 'low',
                    'category': 'readability',
                    'title': 'Line is too long',
                    'message': f'Line has {len(line)} characters. Consider breaking it into multiple lines.',
                    'suggestion': 'Split long lines or extract complex expressions into variables.',
                    'code_example': '// Before: long line\n// After: break into multiple lines',
                    'file': file_path
                })
            
            if 'console.log' in line and not line.strip().startswith('//'):
                suggestions.append({
                    'line': i,
                    'severity': 'low',
                    'category': 'debugging',
                    'title': 'Console.log statement found',
                    'message': 'Debug statement left in code.',
                    'suggestion': 'Remove console.log statements in production code or use proper logging.',
                    'code_example': '// Use proper logging\nlogger.debug("message")',
                    'file': file_path
                })
            
            if re.search(r'\bvar\s+\w+\s*=', line):
                suggestions.append({
                    'line': i,
                    'severity': 'medium',
                    'category': 'best_practice',
                    'title': 'Using "var" instead of "let"/"const"',
                    'message': 'var has function scope and can cause bugs.',
                    'suggestion': 'Use const for values that don\'t change, let for variables that do.',
                    'code_example': '// Instead of var x = 10;\nconst x = 10; // or let x = 10;',
                    'file': file_path
                })
            
            if '==' in line and '===' not in line:
                suggestions.append({
                    'line': i,
                    'severity': 'high',
                    'category': 'bug_risk',
                    'title': 'Loose equality operator',
                    'message': 'Using == can lead to type coercion bugs.',
                    'suggestion': 'Use strict equality (===) or inequality (!==) operators.',
                    'code_example': '// Instead of if (x == 5)\nif (x === 5)',
                    'file': file_path
                })
        
        return suggestions
    
    def _analyze_generic(self, code: str, file_path: str) -> List[Dict]:
        """Generic analysis for other languages"""
        suggestions = []
        lines = code.split('\n')
        
        if len(lines) > 500:
            suggestions.append(self._create_suggestion(
                'large_file',
                {'lines': len(lines)},
                line=1,
                file_path=file_path
            ))
        
        for i, line in enumerate(lines, 1):
            if 'TODO' in line.upper():
                suggestions.append({
                    'line': i,
                    'severity': 'low',
                    'category': 'task',
                    'title': 'TODO comment found',
                    'message': 'Unresolved TODO comment.',
                    'suggestion': 'Address the TODO or create a task to track it.',
                    'code_example': None,
                    'file': file_path
                })
            
            if len(line) > 120:
                suggestions.append({
                    'line': i,
                    'severity': 'low',
                    'category': 'readability',
                    'title': 'Line is too long',
                    'message': f'Line has {len(line)} characters.',
                    'suggestion': 'Break long lines for better readability.',
                    'code_example': None,
                    'file': file_path
                })
        
        return suggestions
    
    def _create_suggestion(self, suggestion_type: str, params: Dict, line: int, file_path: str, custom_message: str = None) -> Dict:
        """Create a suggestion dictionary"""
        template = self.suggestion_types.get(suggestion_type, {})
        
        message = custom_message or template.get('template', '').format(**params)
        
        code_example = self._get_example(suggestion_type)
        
        return {
            'line': line,
            'severity': template.get('severity', 'medium'),
            'category': template.get('category', 'general'),
            'title': template.get('title', 'Code improvement needed'),
            'message': message,
            'suggestion': self._get_actionable_suggestion(suggestion_type, params),
            'code_example': code_example,
            'file': file_path,
            'type': suggestion_type
        }
    
    def _get_actionable_suggestion(self, suggestion_type: str, params: Dict) -> str:
        """Get actionable suggestion text"""
        suggestions_map = {
            'function_too_long': 'Extract smaller functions from the long function. Each function should do one thing.',
            'too_many_parameters': 'Group related parameters into a configuration object or dataclass.',
            'deep_nesting': 'Use guard clauses (early returns) or extract nested logic into separate functions.',
            'large_file': 'Split the file into multiple modules based on functionality.',
            'magic_numbers': 'Define named constants at the top of the file.',
            'complex_condition': 'Extract the complex condition into a well-named function or variable.',
            'god_class': 'Split the class into smaller, focused classes using Single Responsibility Principle.',
            'duplicate_code': 'Extract the duplicate code into a shared function or utility.'
        }
        
        return suggestions_map.get(suggestion_type, 'Review and refactor this code.')
    
    def _get_nesting_depth(self, node: ast.AST, current_depth: int = 0) -> int:
        """Calculate nesting depth of AST node"""
        max_depth = current_depth
        
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.Try)):
                depth = self._get_nesting_depth(child, current_depth + 1)
                max_depth = max(max_depth, depth)
        
        return max_depth
    
    def _get_condition_complexity(self, node: ast.AST) -> int:
        """Count boolean operators in condition"""
        count = 0
        for child in ast.walk(node):
            if isinstance(child, (ast.And, ast.Or)):
                count += 1
            elif isinstance(child, ast.Compare):
                count += len(child.ops)
        return count
    
    def _is_allowed_number(self, value, code: str, line_num: int) -> bool:
        """Check if a number is commonly allowed (0, 1, -1, etc.)"""
        allowed = [0, 1, -1, 100]
        if value in allowed:
            return True
        
        lines = code.split('\n')
        if line_num <= len(lines):
            line = lines[line_num - 1]
            if f'[{value}]' in line:
                return True
        
        return False
    
    def _find_duplicate_blocks(self, code: str, min_lines: int = 3) -> List[Dict]:
        """Find duplicate code blocks"""
        lines = [line.strip() for line in code.split('\n') if line.strip()]
        duplicates = []
        
        line_signatures = {}
        
        for i, line in enumerate(lines):
            if len(line) > 30:
                signature = line[:50]
                if signature in line_signatures:
                    duplicates.append({
                        'line': line_signatures[signature] + 1,
                        'duplicate_line': i + 1,
                        'content': line[:100]
                    })
                else:
                    line_signatures[signature] = i
        
        return duplicates
    
    def _group_by_category(self, suggestions: List[Dict]) -> Dict:
        """Group suggestions by category"""
        categories = {}
        for suggestion in suggestions:
            cat = suggestion.get('category', 'other')
            if cat not in categories:
                categories[cat] = 0
            categories[cat] += 1
        return categories
    
    def analyze_repository_refactors(self, files: List[Dict]) -> Dict:
        """Analyze entire repository for refactoring opportunities"""
        return self.analyze_from_metrics(files)