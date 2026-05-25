# backend/app/analyzers/react_analyzer.py
import re
from typing import List, Dict, Set
from .base import BaseAnalyzer, CodeIssue, Severity, IssueType

class ReactAnalyzer(BaseAnalyzer):
    def __init__(self):
        super().__init__()
        self.hooks_pattern = re.compile(r'useState|useEffect|useCallback|useMemo|useRef')
        self.effect_deps_pattern = re.compile(r'useEffect\([^,]*,\s*\[(.*?)\]')
        
    def analyze(self, code: str, file_path: str = "") -> List[CodeIssue]:
        self.issues = []
        
        if not self._is_react_file(file_path, code):
            return self.issues
        
        # Memory Leak Detection
        self._check_memory_leaks(code)
        
        # useEffect Cleanup
        self._check_effect_cleanup(code)
        
        # Stale State Updates
        self._check_stale_state(code)
        
        # Performance Bottlenecks
        self._check_performance_issues(code)
        
        # Missing Dependencies
        self._check_hook_dependencies(code)
        
        # State Update Anti-patterns
        self._check_state_anti_patterns(code)
        
        return self.issues
    
    def _is_react_file(self, file_path: str, code: str) -> bool:
        """Check if file is a React component"""
        if file_path.endswith(('.jsx', '.tsx')):
            return True
        
        # Check for React imports
        if re.search(r"import\s+React\s+from\s+['\"]react['\"]", code):
            return True
        
        if re.search(r"import\s+.*?\s+from\s+['\"]react['\"]", code):
            return True
        
        return False
    
    def _check_memory_leaks(self, code: str):
        """Detect potential memory leaks in React components"""
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for setInterval/requestAnimationFrame without cleanup
            if re.search(r'setInterval\(|requestAnimationFrame\(', line):
                # Look ahead for cleanup
                component_end = i + 20  # Check next 20 lines
                cleanup_found = False
                
                for j in range(i, min(component_end, len(lines))):
                    if re.search(r'clearInterval\(|cancelAnimationFrame\(', lines[j]):
                        cleanup_found = True
                        break
                
                if not cleanup_found:
                    self.add_issue(CodeIssue(
                        line=i,
                        column=None,
                        severity=Severity.HIGH,
                        type=IssueType.REACT_SPECIFIC,
                        rule_id="REACT001",
                        message="Potential memory leak: setInterval/requestAnimationFrame without cleanup",
                        suggestion="Clear interval/frame in useEffect cleanup function",
                        fix_example="useEffect(() => { const id = setInterval(...); return () => clearInterval(id); }, [])"
                    ))
            
            # Check for event listeners without cleanup
            if re.search(r'addEventListener\(', line):
                self.add_issue(CodeIssue(
                    line=i,
                    column=None,
                    severity=Severity.MEDIUM,
                    type=IssueType.REACT_SPECIFIC,
                    rule_id="REACT002",
                    message="Event listener added without cleanup",
                    suggestion="Remove event listener in useEffect cleanup function",
                    fix_example="useEffect(() => { window.addEventListener('resize', handler); return () => window.removeEventListener('resize', handler); }, [])"
                ))
    
    def _check_effect_cleanup(self, code: str):
        """Check for useEffect with subscriptions but no cleanup"""
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            if re.search(r'useEffect\(.*=>\s*{', line):
                # Find the useEffect block
                effect_body = []
                brace_count = 0
                started = False
                
                for j in range(i, min(i + 30, len(lines))):
                    line_content = lines[j]
                    if '{' in line_content and not started:
                        started = True
                        brace_count += line_content.count('{')
                        brace_count -= line_content.count('}')
                    elif started:
                        effect_body.append(line_content)
                        brace_count += line_content.count('{')
                        brace_count -= line_content.count('}')
                        if brace_count <= 0:
                            break
                
                effect_text = '\n'.join(effect_body)
                
                # Check for subscriptions without cleanup
                if re.search(r'\.subscribe\(', effect_text) and not re.search(r'return\s+\(\)\s*=>\s*{.*?\.unsubscribe\(\)', effect_text):
                    self.add_issue(CodeIssue(
                        line=i,
                        column=None,
                        severity=Severity.HIGH,
                        type=IssueType.REACT_SPECIFIC,
                        rule_id="REACT003",
                        message="Subscription in useEffect without cleanup",
                        suggestion="Return cleanup function to unsubscribe",
                        fix_example="useEffect(() => { const subscription = observable.subscribe(...); return () => subscription.unsubscribe(); }, [])"
                    ))
    
    def _check_stale_state(self, code: str):
        """Detect stale state references in useEffect"""
        lines = code.split('\n')
        
        # Find useEffect hooks
        for i, line in enumerate(lines, 1):
            if 'useEffect(' in line:
                # Check if state variable is used inside but missing from deps
                state_vars = re.findall(r'\b(\w+State)\b', code[i:min(i+20, len(code.split('\n')))])
                dep_match = re.search(r'\[(.*?)\]', line)
                
                if dep_match and state_vars:
                    deps = dep_match.group(1)
                    for var in state_vars:
                        if var not in deps:
                            self.add_issue(CodeIssue(
                                line=i,
                                column=None,
                                severity=Severity.MEDIUM,
                                type=IssueType.REACT_SPECIFIC,
                                rule_id="REACT004",
                                message=f"Potential stale state: '{var}' used but not in dependencies",
                                suggestion=f"Add '{var}' to dependency array or use functional update",
                                fix_example=f"useEffect(..., [{', '.join(state_vars)}])"
                            ))
                            break
    
    def _check_performance_issues(self, code: str):
        """Detect React performance bottlenecks"""
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Inline function in JSX props
            if re.search(r'<.*?onClick=\{\(\)\s*=>', line):
                self.add_issue(CodeIssue(
                    line=i,
                    column=None,
                    severity=Severity.MEDIUM,
                    type=IssueType.PERFORMANCE,
                    rule_id="REACT005",
                    message="Inline function in JSX prop causes unnecessary re-renders",
                    suggestion="Extract function using useCallback",
                    fix_example="const handleClick = useCallback(() => { ... }, []);"
                ))
            
            # Missing React.memo for expensive components
            if re.search(r'function\s+(\w+)\s*\(.*?\)\s*{', line):
                component_name = re.search(r'function\s+(\w+)', line).group(1)
                # Check if component is exported
                if re.search(r'export\s+default\s+' + component_name, '\n'.join(lines[i:i+10])):
                    self.add_issue(CodeIssue(
                        line=i,
                        column=None,
                        severity=Severity.LOW,
                        type=IssueType.PERFORMANCE,
                        rule_id="REACT006",
                        message=f"Component '{component_name}' might benefit from memoization",
                        suggestion="Wrap with React.memo to prevent unnecessary re-renders",
                        fix_example=f"export default React.memo({component_name});"
                    ))
            
            # Large state object
            if re.search(r'useState\(\{[^}]{50,}\}', line):
                self.add_issue(CodeIssue(
                    line=i,
                    column=None,
                    severity=Severity.MEDIUM,
                    type=IssueType.PERFORMANCE,
                    rule_id="REACT007",
                    message="Large state object may cause performance issues",
                    suggestion="Split state into multiple useState calls or use useReducer",
                    fix_example="const [name, setName] = useState(''); const [email, setEmail] = useState('');"
                ))
    
    def _check_hook_dependencies(self, code: str):
        """Check for missing dependencies in useEffect/useCallback/useMemo"""
        hooks = ['useEffect', 'useCallback', 'useMemo']
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            for hook in hooks:
                if hook in line:
                    # Check if dependencies array is empty but uses variables
                    if re.search(rf'{hook}\((.*?)\)', line) and '[]' in line:
                        match = re.search(rf'{hook}\(([^)]+)\)', line)
                        if match:
                            callback = match.group(1)
                            # Simple check for variable usage
                            if re.search(r'\b\w+\b', callback) and not re.search(r'return\s+\(', callback):
                                self.add_issue(CodeIssue(
                                    line=i,
                                    column=None,
                                    severity=Severity.MEDIUM,
                                    type=IssueType.BEST_PRACTICE,
                                    rule_id="REACT008",
                                    message=f"Missing dependencies in {hook}",
                                    suggestion=f"Add used variables to {hook} dependency array",
                                    fix_example=f"{hook}(() => {{ ... }}, [dep1, dep2])"
                                ))
                                break
    
    def _check_state_anti_patterns(self, code: str):
        """Detect state update anti-patterns"""
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Direct state mutation
            if re.search(r'\w+\.state\.[a-z]+\s*=', line):
                self.add_issue(CodeIssue(
                    line=i,
                    column=None,
                    severity=Severity.HIGH,
                    type=IssueType.BUG,
                    rule_id="REACT009",
                    message="Direct state mutation detected",
                    suggestion="Use setState or state setter function",
                    fix_example="setState({ ...state, newValue: 'updated' })"
                ))
            
            # Using index as key
            if re.search(r'key=\{index\}', line):
                self.add_issue(CodeIssue(
                    line=i,
                    column=None,
                    severity=Severity.MEDIUM,
                    type=IssueType.PERFORMANCE,
                    rule_id="REACT010",
                    message="Using index as key can cause issues with dynamic lists",
                    suggestion="Use unique identifier from data as key",
                    fix_example="items.map(item => <div key={item.id}>{item.name}</div>)"
                ))