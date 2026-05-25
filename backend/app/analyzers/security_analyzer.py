# backend/app/analyzers/security_analyzer.py
import re
from typing import List, Optional
from .base import BaseAnalyzer, CodeIssue, Severity, IssueType

class SecurityAnalyzer(BaseAnalyzer):
    def __init__(self):
        super().__init__()
        self.sql_patterns = [
            (r'\.execute\(f?["\'].*?\+.*?["\']', "String concatenation in SQL query"),
            (r'\.execute\(f?["\'].*?\{.*?\}.*?["\']', "f-string formatting in SQL query"),
            (r'\.raw\(', "Raw SQL query execution"),
        ]
        
        self.credential_patterns = [
            (r'password\s*=\s*["\'][^"\']+["\']', "Hardcoded password"),
            (r'api_key\s*=\s*["\'][^"\']+["\']', "Hardcoded API key"),
            (r'token\s*=\s*["\'][^"\']+["\']', "Hardcoded token"),
            (r'secret\s*=\s*["\'][^"\']+["\']', "Hardcoded secret"),
            (r'Authorization\s*:\s*["\']Bearer\s+[^"\']+["\']', "Hardcoded bearer token"),
        ]
        
        self.xss_patterns = [
            (r'dangerouslySetInnerHTML', "Unsafe HTML rendering"),
            (r'innerHTML\s*=', "Direct innerHTML manipulation"),
            (r'insertAdjacentHTML', "Unsafe HTML insertion"),
            (r'eval\(', "Use of eval()"),
            (r'new Function\(', "Dynamic function creation"),
        ]
        
        self.validation_patterns = [
            (r'\.get\(["\'][^"\']+["\'']\)', "Unsafe dict access without validation"),
            (r'int\(input\(', "Unvalidated user input conversion"),
        ]
    
    def analyze(self, code: str, file_path: str = "") -> List[CodeIssue]:
        self.issues = []
        
        # SQL Injection Detection
        self._check_sql_injection(code)
        
        # Hardcoded Credentials
        self._check_hardcoded_credentials(code)
        
        # XSS and Unsafe Rendering
        self._check_xss_vulnerabilities(code)
        
        # Input Validation
        self._check_input_validation(code)
        
        # Path Traversal
        self._check_path_traversal(code)
        
        # Command Injection
        self._check_command_injection(code)
        
        return self.issues
    
    def _check_sql_injection(self, code: str):
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            for pattern, description in self.sql_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    self.add_issue(CodeIssue(
                        line=i,
                        column=None,
                        severity=Severity.CRITICAL,
                        type=IssueType.SECURITY,
                        rule_id="SQL001",
                        message=f"Potential SQL Injection: {description}",
                        suggestion="Use parameterized queries or an ORM",
                        fix_example="cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))",
                        reference_url="https://owasp.org/www-community/attacks/SQL_Injection"
                    ))
    
    def _check_hardcoded_credentials(self, code: str):
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            # Skip comments
            if line.strip().startswith(('#', '//', '/*')):
                continue
            
            for pattern, description in self.credential_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    self.add_issue(CodeIssue(
                        line=i,
                        column=None,
                        severity=Severity.CRITICAL,
                        type=IssueType.SECURITY,
                        rule_id="SEC001",
                        message=f"Hardcoded credential detected: {description}",
                        suggestion="Use environment variables or a secrets manager",
                        fix_example="import os; password = os.environ.get('DB_PASSWORD')",
                        reference_url="https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html"
                    ))
                    break  # Only report one per line
    
    def _check_xss_vulnerabilities(self, code: str):
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            for pattern, description in self.xss_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    self.add_issue(CodeIssue(
                        line=i,
                        column=None,
                        severity=Severity.HIGH,
                        type=IssueType.SECURITY,
                        rule_id="XSS001",
                        message=f"Potential XSS vulnerability: {description}",
                        suggestion="Sanitize user input and use safe DOM APIs",
                        fix_example="Use textContent instead of innerHTML, or sanitize with DOMPurify",
                        reference_url="https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html"
                    ))
    
    def _check_input_validation(self, code: str):
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            # Check for direct input usage without validation
            if re.search(r'(input|request\.args\.get|request\.form\.get|params\.)', line, re.IGNORECASE):
                next_lines = '\n'.join(lines[i:i+3])
                if not re.search(r'(validate|sanitize|is_valid|check_)', next_lines, re.IGNORECASE):
                    self.add_issue(CodeIssue(
                        line=i,
                        column=None,
                        severity=Severity.MEDIUM,
                        type=IssueType.SECURITY,
                        rule_id="VAL001",
                        message="User input used without validation",
                        suggestion="Always validate and sanitize user input",
                        fix_example="if not validate_email(email): raise ValidationError('Invalid email')"
                    ))
    
    def _check_path_traversal(self, code: str):
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            if re.search(r'(open\(|Path\(|file\.read\()', line):
                if re.search(r'(\.\./|\.\.\\)', line):
                    self.add_issue(CodeIssue(
                        line=i,
                        column=None,
                        severity=Severity.HIGH,
                        type=IssueType.SECURITY,
                        rule_id="PATH001",
                        message="Path traversal vulnerability detected",
                        suggestion="Validate file paths and use allowlists",
                        fix_example="normalized = os.path.normpath(path); if not normalized.startswith(base_dir): raise ValueError"
                    ))
    
    def _check_command_injection(self, code: str):
        lines = code.split('\n')
        dangerous_funcs = [
            (r'os\.system\(', "os.system()"),
            (r'subprocess\.call\(.*shell=True', "subprocess.call with shell=True"),
            (r'eval\(', "eval()"),
            (r'exec\(', "exec()"),
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern, func_name in dangerous_funcs:
                if re.search(pattern, line, re.IGNORECASE):
                    self.add_issue(CodeIssue(
                        line=i,
                        column=None,
                        severity=Severity.CRITICAL,
                        type=IssueType.SECURITY,
                        rule_id="CMD001",
                        message=f"Command injection risk: {func_name}",
                        suggestion="Use safer alternatives with proper input validation",
                        fix_example="subprocess.run(['ls', '-la'], capture_output=True, text=True)"
                    ))