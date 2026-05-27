import ast
import re
from typing import Dict, List, Any, Optional
from datetime import datetime

class TestGenerator:
    def __init__(self):
        self.test_frameworks = {
            'python': {
                'name': 'pytest',
                'imports': 'import pytest\nfrom unittest.mock import Mock, patch',
                'assertions': {
                    'equality': 'assert {actual} == {expected}',
                    'truthy': 'assert {actual}',
                    'falsey': 'assert not {actual}',
                    'exception': 'with pytest.raises({exception}):',
                    'in': 'assert {item} in {collection}'
                }
            },
            'javascript': {
                'name': 'jest',
                'imports': "const {{ describe, it, expect, beforeEach }} = require('@jest/globals');",
                'assertions': {
                    'equality': 'expect({actual}).toBe({expected})',
                    'truthy': 'expect({actual}).toBeTruthy()',
                    'falsey': 'expect({actual}).toBeFalsy()',
                    'exception': 'expect(() => {{ {code} }}).toThrow()',
                    'in': 'expect({collection}).toContain({item})'
                }
            }
        }
    
    def generate_tests(self, code: str, language: str = 'python', 
                       function_name: str = None) -> Dict[str, Any]:
        """Generate unit tests for given code"""
        
        if language == 'python':
            tests = self._generate_python_tests(code, function_name)
        elif language in ['javascript', 'typescript']:
            tests = self._generate_javascript_tests(code, function_name)
        else:
            tests = self._generate_generic_tests(code)
        
        return {
            'success': True,
            'language': language,
            'framework': self.test_frameworks[language]['name'] if language in self.test_frameworks else 'custom',
            'test_code': tests,
            'test_count': self._count_tests(tests),
            'coverage_estimate': self._estimate_coverage(code, tests)
        }
    
    def _generate_python_tests(self, code: str, function_name: str = None) -> str:
        """Generate Python/pytest tests"""
        test_parts = []
        
        # Add imports
        test_parts.append("import pytest")
        test_parts.append("from unittest.mock import Mock, patch, MagicMock")
        test_parts.append("")
        
        # Parse code to find functions
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if function_name and node.name != function_name:
                        continue
                    
                    # Generate tests for this function
                    func_tests = self._generate_function_tests_python(node, code)
                    test_parts.extend(func_tests)
                    
        except SyntaxError:
            # Fallback for invalid code
            test_parts.append("def test_function():")
            test_parts.append("    \"\"\"Test the function\"\"\"")
            test_parts.append("    # TODO: Implement tests based on function logic")
            test_parts.append("    assert True")
        
        return '\n'.join(test_parts)
    
    def _generate_function_tests_python(self, func_node: ast.FunctionDef, code: str) -> List[str]:
        """Generate tests for a specific Python function"""
        tests = []
        func_name = func_node.name
        
        # Extract parameters
        params = [arg.arg for arg in func_node.args.args]
        defaults = func_node.args.defaults
        
        # Basic test case
        tests.append(f"\ndef test_{func_name}_basic():")
        tests.append(f"    \"\"\"Test {func_name} with valid inputs\"\"\"")
        
        # Generate test data based on parameter names
        test_args = []
        for param in params:
            test_value = self._generate_test_value(param)
            test_args.append(test_value)
        
        args_str = ', '.join(test_args)
        tests.append(f"    result = {func_name}({args_str})")
        tests.append("    assert result is not None  # Replace with actual assertion")
        tests.append("")
        
        # Edge case test
        tests.append(f"\ndef test_{func_name}_edge_cases():")
        tests.append(f"    \"\"\"Test {func_name} with edge cases\"\"\"")
        
        # Test with None values
        if params:
            none_args = ['None' if p in params else '' for p in params]
            none_str = ', '.join(none_args)
            tests.append(f"    # Test with None values")
            tests.append(f"    result = {func_name}({none_str})")
            tests.append("    # Handle None appropriately")
            tests.append("")
        
        # Exception test
        tests.append(f"\ndef test_{func_name}_exception_handling():")
        tests.append(f"    \"\"\"Test {func_name} exception handling\"\"\"")
        tests.append("    with pytest.raises(Exception):")
        tests.append(f"        {func_name}(None)  # Replace with invalid input")
        
        return tests
    
    def _generate_javascript_tests(self, code: str, function_name: str = None) -> str:
        """Generate JavaScript/Jest tests"""
        test_parts = []
        
        test_parts.append("const { describe, it, expect, beforeEach } = require('@jest/globals');")
        test_parts.append("")
        test_parts.append("// Import the functions to test")
        test_parts.append("const { " + (function_name or "yourFunction") + " } = require('./your-module');")
        test_parts.append("")
        
        test_parts.append("describe('Function Tests', () => {")
        
        if function_name:
            test_parts.append(f"    describe('{function_name}', () => {{")
            test_parts.append(f"        it('should handle valid input', () => {{")
            test_parts.append(f"            const result = {function_name}('test');")
            test_parts.append("            expect(result).toBeDefined();")
            test_parts.append("        });")
            test_parts.append("")
            test_parts.append(f"        it('should handle edge cases', () => {{")
            test_parts.append(f"            expect(() => {function_name}(null)).not.toThrow();")
            test_parts.append("        });")
            test_parts.append("    });")
        else:
            test_parts.append("    it('should pass basic test', () => {")
            test_parts.append("        expect(true).toBe(true);")
            test_parts.append("    });")
        
        test_parts.append("});")
        
        return '\n'.join(test_parts)
    
    def _generate_generic_tests(self, code: str) -> str:
        """Generate generic test structure"""
        return """# Generic Test Template

def test_function():
    \"\"\"Basic test case\"\"\"
    # Arrange
    input_data = None
    
    # Act
    result = function_to_test(input_data)
    
    # Assert
    assert result is not None

# Add more test cases for edge conditions
"""
    
    def _generate_test_value(self, param_name: str) -> str:
        """Generate appropriate test value based on parameter name"""
        name_lower = param_name.lower()
        
        if 'id' in name_lower or 'count' in name_lower:
            return '1'
        elif 'name' in name_lower or 'title' in name_lower:
            return '"test"'
        elif 'email' in name_lower:
            return '"test@example.com"'
        elif 'age' in name_lower:
            return '25'
        elif 'active' in name_lower or 'enabled' in name_lower:
            return 'True'
        elif 'items' in name_lower or 'list' in name_lower:
            return '[]'
        elif 'data' in name_lower:
            return '{}'
        else:
            return 'None'
    
    def _count_tests(self, test_code: str) -> int:
        """Count number of test functions/cases"""
        # Count pytest test functions
        pytest_count = len(re.findall(r'def test_\w+', test_code))
        # Count jest test blocks
        jest_count = len(re.findall(r'(it|test)\s*\(', test_code))
        
        return max(pytest_count, jest_count, 1)
    
    def _estimate_coverage(self, code: str, tests: str) -> int:
        """Estimate test coverage percentage"""
        # Simple heuristic based on code complexity
        lines = len(code.split('\n'))
        functions = len(re.findall(r'def \w+\(', code))
        test_functions = len(re.findall(r'def test_\w+', tests))
        
        if functions == 0:
            return 80
        
        coverage = min(95, (test_functions / functions) * 80 + 20)
        return int(coverage)
    
    def generate_edge_cases(self, function_code: str, language: str = 'python') -> List[Dict]:
        """Generate edge case test scenarios"""
        edge_cases = []
        
        # Common edge cases
        edge_case_templates = [
            {
                'name': 'Null/None Input',
                'description': 'Function handles null/None values gracefully',
                'input': 'None',
                'expected': 'Should not crash, return appropriate default or error'
            },
            {
                'name': 'Empty Input',
                'description': 'Function handles empty strings/collections',
                'input': '"" or []',
                'expected': 'Should return empty result or handle appropriately'
            },
            {
                'name': 'Very Large Input',
                'description': 'Function performs well with large data sets',
                'input': '10,000+ items',
                'expected': 'Should complete within reasonable time'
            },
            {
                'name': 'Invalid Type',
                'description': 'Function validates input types',
                'input': 'Wrong data type',
                'expected': 'Should raise appropriate TypeError or handle gracefully'
            },
            {
                'name': 'Boundary Values',
                'description': 'Function handles boundary conditions',
                'input': 'Min/max values',
                'expected': 'Should behave correctly at boundaries'
            },
            {
                'name': 'Concurrent Calls',
                'description': 'Function is thread-safe (if applicable)',
                'input': 'Multiple simultaneous calls',
                'expected': 'Should not have race conditions'
            }
        ]
        
        # Language-specific edge cases
        if language == 'python':
            edge_cases.append({
                'name': 'Very Large Integer',
                'description': 'Function handles arbitrary precision integers',
                'input': '10**100',
                'expected': 'Should handle without overflow'
            })
        elif language in ['javascript', 'typescript']:
            edge_cases.append({
                'name': 'Undefined vs Null',
                'description': 'Function distinguishes between undefined and null',
                'input': 'undefined, null',
                'expected': 'Should handle both appropriately'
            })
        
        edge_cases.extend(edge_case_templates)
        
        return edge_cases
    
    def generate_api_tests(self, endpoints: List[Dict]) -> str:
        """Generate API tests for given endpoints"""
        test_parts = []
        
        test_parts.append("import pytest")
        test_parts.append("import requests")
        test_parts.append("")
        test_parts.append("BASE_URL = 'http://localhost:8000'")
        test_parts.append("")
        
        for endpoint in endpoints:
            method = endpoint.get('method', 'GET')
            path = endpoint.get('path', '/')
            
            test_parts.append(f"\ndef test_{method.lower()}_{path.replace('/', '_')}:")
            test_parts.append(f'    """Test {method} {path}"""')
            test_parts.append(f"    response = requests.{method.lower()}(f'{{BASE_URL}}{path}')")
            test_parts.append("    assert response.status_code == 200")
            test_parts.append("    data = response.json()")
            test_parts.append("    assert data is not None")
            test_parts.append("")
        
        return '\n'.join(test_parts)