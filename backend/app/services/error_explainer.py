import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

class ErrorCategory(Enum):
    SYNTAX = "syntax_error"
    RUNTIME = "runtime_error"
    IMPORT = "import_error"
    TYPE = "type_error"
    VALUE = "value_error"
    ATTRIBUTE = "attribute_error"
    INDEX = "index_error"
    KEY = "key_error"
    NETWORK = "network_error"
    DATABASE = "database_error"

@dataclass
class ErrorExplanation:
    error_type: str
    error_message: str
    category: ErrorCategory
    explanation: str
    probable_causes: List[str]
    fix_suggestions: List[str]
    code_example: Optional[str] = None
    related_docs: Optional[List[str]] = None

class ErrorExplainer:
    def __init__(self):
        self.error_patterns = self._init_error_patterns()
        self.fix_templates = self._init_fix_templates()
    
    def _init_error_patterns(self) -> Dict:
        """Initialize error pattern matching rules"""
        return {
            # Python Errors
            'SyntaxError': {
                'pattern': r'SyntaxError:\s*(.+?)(?:\n|$)',
                'category': ErrorCategory.SYNTAX,
                'explanation': "Python couldn't understand your code due to invalid syntax.",
                'common_causes': [
                    "Missing colon (:) after if/for/while/def/class",
                    "Unmatched parentheses, brackets, or quotes",
                    "Missing comma in list/dict",
                    "Invalid indentation",
                    "Using reserved keywords as variable names"
                ]
            },
            'IndentationError': {
                'pattern': r'IndentationError:\s*(.+?)(?:\n|$)',
                'category': ErrorCategory.SYNTAX,
                'explanation': "Python requires consistent indentation to define code blocks.",
                'common_causes': [
                    "Mixing tabs and spaces",
                    "Inconsistent number of spaces",
                    "Missing indentation after colon",
                    "Extra indentation"
                ]
            },
            'ImportError|ModuleNotFoundError': {
                'pattern': r'(?:ImportError|ModuleNotFoundError):\s*No module named [\'"](.+?)[\'"]',
                'category': ErrorCategory.IMPORT,
                'explanation': "Python cannot find the module you're trying to import.",
                'common_causes': [
                    "Module not installed",
                    "Incorrect module name",
                    "Module in wrong location",
                    "Virtual environment not activated"
                ]
            },
            'TypeError': {
                'pattern': r'TypeError:\s*(.+?)(?:\n|$)',
                'category': ErrorCategory.TYPE,
                'explanation': "You're trying to perform an operation on an incompatible data type.",
                'common_causes': [
                    "Adding string to integer",
                    "Calling non-callable object",
                    "Wrong number of arguments to function",
                    "Accessing attribute on None"
                ]
            },
            'ValueError': {
                'pattern': r'ValueError:\s*(.+?)(?:\n|$)',
                'category': ErrorCategory.VALUE,
                'explanation': "A function received an argument of correct type but inappropriate value.",
                'common_causes': [
                    "Converting invalid string to integer",
                    "Value outside expected range",
                    "Empty value where required",
                    "Invalid format"
                ]
            },
            'AttributeError': {
                'pattern': r'AttributeError:\s*[\'"]?(.+?)[\'"]?\s+object has no attribute [\'"]?(.+?)[\'"]?',
                'category': ErrorCategory.ATTRIBUTE,
                'explanation': "You're trying to access an attribute or method that doesn't exist.",
                'common_causes': [
                    "Typo in attribute name",
                    "Variable is None or wrong type",
                    "Method exists in different version",
                    "Forgetting to call parent constructor"
                ]
            },
            'KeyError': {
                'pattern': r'KeyError:\s*(.+?)(?:\n|$)',
                'category': ErrorCategory.KEY,
                'explanation': "You're trying to access a dictionary key that doesn't exist.",
                'common_causes': [
                    "Key doesn't exist in dictionary",
                    "Typo in key name",
                    "Dictionary is empty",
                    "Case sensitivity issue"
                ]
            },
            'IndexError': {
                'pattern': r'IndexError:\s*list index out of range',
                'category': ErrorCategory.INDEX,
                'explanation': "You're trying to access a list/array element that doesn't exist.",
                'common_causes': [
                    "Index exceeds list length",
                    "Negative index beyond list start",
                    "Empty list",
                    "Off-by-one error in loop"
                ]
            },
            'NameError': {
                'pattern': r'NameError:\s*name [\'"](.+?)[\'"] is not defined',
                'category': ErrorCategory.RUNTIME,
                'explanation': "You're trying to use a variable or function that hasn't been defined.",
                'common_causes': [
                    "Variable not assigned yet",
                    "Typo in variable name",
                    "Variable out of scope",
                    "Forgot to import module"
                ]
            },
            'ZeroDivisionError': {
                'pattern': r'ZeroDivisionError:\s*division by zero',
                'category': ErrorCategory.VALUE,
                'explanation': "You're trying to divide a number by zero.",
                'common_causes': [
                    "Denominator is zero",
                    "Variable not initialized",
                    "Empty list or collection"
                ]
            },
            
            # React/Vite Errors
            'React Error Boundary': {
                'pattern': r'error-boundary|React caught an error|Uncaught Error',
                'category': ErrorCategory.RUNTIME,
                'explanation': "A React component threw an error that wasn't handled properly.",
                'common_causes': [
                    "State or props accessed before initialization",
                    "Missing data from API",
                    "Error in useEffect",
                    "Failed to render component"
                ]
            },
            "Can't find variable": {
                'pattern': r"Can't find variable: (\w+)",
                'category': ErrorCategory.RUNTIME,
                'explanation': "JavaScript variable or function is not defined in scope.",
                'common_causes': [
                    "Missing import statement",
                    "Variable not declared",
                    "Typo in variable name",
                    "Variable referenced before declaration"
                ]
            },
            "Cannot read property": {
                'pattern': r"Cannot read property ['\"](\w+)['\"] of (undefined|null)",
                'category': ErrorCategory.ATTRIBUTE,
                'explanation': "Trying to access a property on undefined or null value.",
                'common_causes': [
                    "API response missing expected data",
                    "Async data not loaded yet",
                    "Optional chaining not used",
                    "State not initialized"
                ]
            },
            
            # FastAPI Errors
            '422 Unprocessable Entity': {
                'pattern': r'422|unprocessable entity|validation error',
                'category': ErrorCategory.TYPE,
                'explanation': "Request data doesn't match the expected schema.",
                'common_causes': [
                    "Missing required fields",
                    "Wrong data types in request",
                    "Invalid field values",
                    "Malformed JSON"
                ]
            },
            
            # Node.js Errors
            "Cannot find module": {
                'pattern': r"Cannot find module ['\"](.+?)['\"]",
                'category': ErrorCategory.IMPORT,
                'explanation': "Node.js cannot locate the module you're trying to require/import.",
                'common_causes': [
                    "Module not installed",
                    "Incorrect path to local module",
                    "Missing package.json dependencies",
                    "Module name typo"
                ]
            }
        }
    
    def _init_fix_templates(self) -> Dict:
        """Initialize fix templates for common errors"""
        return {
            'SyntaxError': {
                'fixes': [
                    "Check for missing colons after control statements",
                    "Verify all parentheses and brackets are properly closed",
                    "Ensure strings have matching quotes",
                    "Check for invalid indentation"
                ],
                'example': """
# ❌ Wrong
if x > 5
    print("x is greater than 5")

# ✅ Correct
if x > 5:
    print("x is greater than 5")
"""
            },
            'ImportError': {
                'fixes': [
                    f"Install the missing module using: pip install {self._get_module_name}",
                    "Check if module name is spelled correctly",
                    "Verify you're in the correct virtual environment",
                    "Add module to requirements.txt"
                ]
            },
            'TypeError': {
                'fixes': [
                    "Convert types explicitly (str(), int(), float())",
                    "Check function arguments count and types",
                    "Verify variable isn't None before accessing attributes",
                    "Use type checking (isinstance())"
                ],
                'example': """
# ❌ Wrong
number = "123"
result = number + 456  # Can't add string and int

# ✅ Correct
number = "123"
result = int(number) + 456  # Convert to int first
"""
            },
            'KeyError': {
                'fixes': [
                    "Use dict.get() method with default value",
                    "Check if key exists with 'in' operator",
                    "Verify dictionary contents before access",
                    "Use try/except block for missing keys"
                ],
                'example': """
# ❌ Wrong
user = {"name": "Alice"}
email = user["email"]  # KeyError: 'email'

# ✅ Correct - Method 1
email = user.get("email", "no-email@example.com")

# ✅ Correct - Method 2
if "email" in user:
    email = user["email"]
else:
    email = "no-email@example.com"
"""
            },
            'IndexError': {
                'fixes': [
                    "Check list length before accessing index",
                    "Use negative indexing carefully",
                    "Ensure loop doesn't exceed list bounds",
                    "Handle empty list case"
                ],
                'example': """
# ❌ Wrong
items = [1, 2, 3]
for i in range(len(items) + 1):
    print(items[i])  # IndexError on last iteration

# ✅ Correct
items = [1, 2, 3]
for i in range(len(items)):
    print(items[i])
"""
            }
        }
    
    def _get_module_name(self, error_msg: str) -> str:
        """Extract module name from error message"""
        match = re.search(r"No module named ['\"](.+?)['\"]", error_msg)
        return match.group(1) if match else "module"
    
    def explain_error(self, error_message: str, context: str = "") -> Dict[str, Any]:
        """Main entry point for error explanation"""
        # Parse error type
        error_type, clean_message = self._parse_error_type(error_message)
        
        # Find matching pattern
        explanation = self._get_explanation(error_type, clean_message)
        
        # Generate specific fixes based on context
        if context:
            explanation['contextual_fixes'] = self._generate_contextual_fixes(
                error_type, clean_message, context
            )
        
        # Add stack trace analysis if available
        stack_trace = self._parse_stack_trace(error_message)
        if stack_trace:
            explanation['stack_trace_analysis'] = stack_trace
        
        return explanation
    
    def _parse_error_type(self, error_message: str) -> tuple:
        """Extract error type from message"""
        # Common error patterns
        error_patterns = [
            (r'(\w+Error):', 'python'),
            (r'Uncaught (\w+Error):', 'javascript'),
            (r'TypeError: (.*)', 'javascript'),
            (r'ReferenceError: (.*)', 'javascript'),
            (r'SyntaxError: (.*)', 'javascript'),
        ]
        
        for pattern, lang in error_patterns:
            match = re.search(pattern, error_message)
            if match:
                error_type = match.group(1) if match.groups() else match.group(0)
                clean_msg = error_message.replace(match.group(0), '').strip()
                return error_type, clean_msg
        
        # Default fallback
        first_line = error_message.split('\n')[0]
        return "UnknownError", first_line
    
    def _get_explanation(self, error_type: str, error_message: str) -> Dict:
        """Get detailed explanation for error"""
        # Try to match known error patterns
        for pattern_key, pattern_info in self.error_patterns.items():
            if re.match(pattern_key, error_type) or pattern_key in error_type:
                # Extract specific details
                match = re.search(pattern_info['pattern'], error_message)
                specific_detail = match.group(1) if match else None
                
                return {
                    'error_type': error_type,
                    'category': pattern_info['category'].value,
                    'explanation': pattern_info['explanation'],
                    'probable_causes': pattern_info['common_causes'],
                    'fix_suggestions': self._get_fix_suggestions(error_type, specific_detail),
                    'code_example': self._get_code_example(error_type),
                    'related_docs': self._get_related_docs(error_type)
                }
        
        # Generic explanation for unknown errors
        return {
            'error_type': error_type,
            'category': ErrorCategory.RUNTIME.value,
            'explanation': f"An error of type '{error_type}' occurred. Review the error message for details.",
            'probable_causes': [
                "Check the error message for specific details",
                "Review recent code changes",
                "Verify input data and types",
                "Check for missing dependencies"
            ],
            'fix_suggestions': [
                "Read the full error message carefully",
                "Check line numbers indicated in the stack trace",
                "Search for the error message online",
                "Use debugging tools to inspect variable values"
            ],
            'code_example': None,
            'related_docs': ["https://docs.python.org/3/errors.html"]
        }
    
    def _get_fix_suggestions(self, error_type: str, specific_detail: Optional[str]) -> List[str]:
        """Get fix suggestions based on error type"""
        if error_type in self.fix_templates:
            fixes = self.fix_templates[error_type]['fixes'].copy()
            if specific_detail and 'module' in error_type.lower():
                fixes[0] = fixes[0].replace(self._get_module_name, specific_detail)
            return fixes
        
        # Generic fixes
        return [
            "Review the code at the line number indicated",
            "Check for typos in variable/function names",
            "Verify all required imports are present",
            "Test with sample input to isolate the issue"
        ]
    
    def _get_code_example(self, error_type: str) -> Optional[str]:
        """Get code example showing fix"""
        if error_type in self.fix_templates:
            return self.fix_templates[error_type].get('example')
        return None
    
    def _get_related_docs(self, error_type: str) -> List[str]:
        """Get links to related documentation"""
        docs_map = {
            'Python': "https://docs.python.org/3/tutorial/errors.html",
            'JavaScript': "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Errors",
            'React': "https://react.dev/errors",
            'FastAPI': "https://fastapi.tiangolo.com/errors/"
        }
        
        docs = []
        if 'python' in error_type.lower():
            docs.append(docs_map['Python'])
        elif 'javascript' in error_type.lower():
            docs.append(docs_map['JavaScript'])
        elif 'react' in error_type.lower():
            docs.append(docs_map['React'])
        elif 'fastapi' in error_type.lower():
            docs.append(docs_map['FastAPI'])
        else:
            docs.append(docs_map['Python'])
            docs.append(docs_map['JavaScript'])
        
        return docs
    
    def _parse_stack_trace(self, error_message: str) -> Dict:
        """Parse and analyze stack trace"""
        lines = error_message.split('\n')
        stack_lines = []
        file_pattern = r'File ["\'](.+?)["\'], line (\d+)'
        
        for line in lines:
            match = re.search(file_pattern, line)
            if match:
                stack_lines.append({
                    'file': match.group(1),
                    'line': int(match.group(2)),
                    'code': ''  # Would need file access to get actual code
                })
        
        if stack_lines:
            return {
                'frames': stack_lines,
                'root_cause': stack_lines[-1] if stack_lines else None,
                'suggestion': "The error originated at line {} in {}".format(
                    stack_lines[-1]['line'], stack_lines[-1]['file']
                ) if stack_lines else "Unable to parse stack trace"
            }
        
        return None
    
    def _generate_contextual_fixes(self, error_type: str, error_message: str, context: str) -> List[str]:
        """Generate fixes based on code context"""
        fixes = []
        
        # Context-specific suggestions
        if 'react' in context.lower():
            if 'undefined' in error_message:
                fixes.append("Use optional chaining (?.) to safely access nested properties")
                fixes.append("Initialize state with default values")
                fixes.append("Check if data is loaded before rendering")
            elif 'hook' in error_message:
                fixes.append("Ensure hooks are called at the top level of component")
                fixes.append("Don't call hooks inside conditions or loops")
                fixes.append("Verify custom hooks follow naming convention (use*)")
        
        elif 'fastapi' in context.lower():
            if 'validation' in error_message:
                fixes.append("Check request body matches Pydantic model schema")
                fixes.append("Verify required fields are present")
                fixes.append("Ensure data types match model definitions")
        
        elif 'database' in context.lower():
            if 'connection' in error_message:
                fixes.append("Verify database credentials and connection string")
                fixes.append("Check if database service is running")
                fixes.append("Ensure network/firewall allows connection")
        
        return fixes if fixes else None