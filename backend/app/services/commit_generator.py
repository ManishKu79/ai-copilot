import re
from typing import Dict, List, Optional, Any
from datetime import datetime
from collections import Counter

class CommitMessageGenerator:
    def __init__(self):
        self.commit_types = {
            'feat': {
                'emoji': '✨',
                'description': 'New feature',
                'examples': ['add', 'implement', 'create', 'introduce']
            },
            'fix': {
                'emoji': '🐛',
                'description': 'Bug fix',
                'examples': ['fix', 'repair', 'correct', 'resolve']
            },
            'docs': {
                'emoji': '📝',
                'description': 'Documentation',
                'examples': ['update readme', 'add docs', 'document']
            },
            'style': {
                'emoji': '💄',
                'description': 'Code style/formatting',
                'examples': ['format', 'lint', 'whitespace', 'prettier']
            },
            'refactor': {
                'emoji': '♻️',
                'description': 'Code refactoring',
                'examples': ['refactor', 'restructure', 'rename', 'clean']
            },
            'perf': {
                'emoji': '⚡',
                'description': 'Performance improvement',
                'examples': ['optimize', 'improve performance', 'speed up']
            },
            'test': {
                'emoji': '✅',
                'description': 'Testing',
                'examples': ['add test', 'update test', 'fix test']
            },
            'chore': {
                'emoji': '🔧',
                'description': 'Maintenance tasks',
                'examples': ['update deps', 'config', 'build']
            },
            'ci': {
                'emoji': '👷',
                'description': 'CI/CD changes',
                'examples': ['github actions', 'pipeline', 'deploy']
            },
            'auth': {
                'emoji': '🔐',
                'description': 'Authentication',
                'examples': ['login', 'register', 'logout', 'session']
            },
            'security': {
                'emoji': '🔒',
                'description': 'Security fixes',
                'examples': ['security', 'vulnerability', 'patch']
            }
        }
        
        self.scope_detection = {
            'auth': ['auth', 'login', 'logout', 'register', 'session', 'token', 'jwt'],
            'api': ['api', 'endpoint', 'route', 'rest'],
            'ui': ['ui', 'component', 'page', 'view', 'frontend'],
            'db': ['database', 'db', 'sql', 'migration', 'query'],
            'config': ['config', 'setting', 'env', 'configuration'],
            'test': ['test', 'spec', 'unit', 'integration']
        }
    
    def generate_from_diff(self, diff: str, files_changed: List[str] = None) -> Dict[str, Any]:
        """Generate commit message from git diff"""
        
        # Analyze changes
        changes = self._analyze_changes(diff, files_changed)
        
        # Determine commit type and scope
        commit_type, scope = self._determine_commit_type_and_scope(changes)
        
        # Generate subject line
        subject = self._generate_subject(changes, commit_type, scope)
        
        # Generate body
        body = self._generate_body(changes)
        
        # Generate footer
        footer = self._generate_footer()
        
        # Full message
        full_message = self._format_message(commit_type, scope, subject, body, footer)
        
        # Get emoji
        emoji = self.commit_types.get(commit_type, self.commit_types['chore'])['emoji']
        
        return {
            'success': True,
            'commit_type': commit_type,
            'scope': scope,
            'emoji': emoji,
            'subject': subject,
            'body': body,
            'footer': footer,
            'full_message': full_message,
            'conventional_format': f"{commit_type}{f'({scope})' if scope else ''}: {subject}",
            'changes_summary': changes
        }
    
    def generate_simple_message(self, description: str, commit_type: str = 'feat') -> Dict:
        """Generate a simple commit message from a description"""
        type_info = self.commit_types.get(commit_type, self.commit_types['chore'])
        
        # Capitalize description
        description = description[0].upper() + description[1:] if description else description
        
        # Generate bullet points based on description keywords
        bullet_points = self._generate_bullet_points_from_description(description, commit_type)
        body = '\n'.join(bullet_points)
        
        conventional = f"{commit_type}: {description}"
        header = f"{type_info['emoji']} {conventional}"
        
        footer = self._generate_footer()
        
        return {
            'success': True,
            'commit_type': commit_type,
            'scope': None,
            'emoji': type_info['emoji'],
            'subject': description,
            'body': body,
            'footer': footer,
            'full_message': f"{header}\n\n{body}\n\n{footer}",
            'conventional_format': conventional,
            'changes_summary': None
        }
    
    def generate_with_scope(self, description: str, commit_type: str = 'feat', scope: str = None) -> Dict:
        """Generate commit message with scope from description"""
        type_info = self.commit_types.get(commit_type, self.commit_types['chore'])
        
        # Capitalize description
        description = description[0].upper() + description[1:] if description else description
        
        # Generate bullet points
        bullet_points = self._generate_bullet_points_from_description(description, commit_type, scope)
        body = '\n'.join(bullet_points)
        
        # Format with scope
        if scope:
            conventional = f"{commit_type}({scope}): {description}"
            header = f"{type_info['emoji']} {conventional}"
        else:
            conventional = f"{commit_type}: {description}"
            header = f"{type_info['emoji']} {conventional}"
        
        footer = self._generate_footer()
        
        return {
            'success': True,
            'commit_type': commit_type,
            'scope': scope,
            'emoji': type_info['emoji'],
            'subject': description,
            'body': body,
            'footer': footer,
            'full_message': f"{header}\n\n{body}\n\n{footer}",
            'conventional_format': conventional,
            'changes_summary': None
        }
    
    def _generate_bullet_points_from_description(self, description: str, commit_type: str, scope: str = None) -> List[str]:
        """Generate relevant bullet points from description"""
        desc_lower = description.lower()
        bullet_points = []
        
        # Auth-related changes
        if 'login' in desc_lower or 'auth' in desc_lower or scope == 'auth':
            bullet_points = [
                "- Added backend login validation",
                "- Added frontend login UI handling",
                "- Improved authentication flow"
            ]
        # API changes
        elif 'api' in desc_lower or 'endpoint' in desc_lower or scope == 'api':
            bullet_points = [
                "- Added new API endpoint",
                "- Updated API documentation",
                "- Added request/response validation"
            ]
        # Database changes
        elif 'database' in desc_lower or 'db' in desc_lower or 'migration' in desc_lower or scope == 'db':
            bullet_points = [
                "- Updated database schema",
                "- Added new migrations",
                "- Optimized database queries"
            ]
        # UI/Frontend changes
        elif 'ui' in desc_lower or 'component' in desc_lower or 'frontend' in desc_lower or scope == 'ui':
            bullet_points = [
                "- Added new UI components",
                "- Improved user interface",
                "- Enhanced responsive design"
            ]
        # Performance changes
        elif 'performance' in desc_lower or 'optimize' in desc_lower or 'speed' in desc_lower:
            bullet_points = [
                "- Optimized code performance",
                "- Reduced load times",
                "- Improved caching strategy"
            ]
        # Bug fixes
        elif commit_type == 'fix' or 'fix' in desc_lower or 'bug' in desc_lower:
            bullet_points = [
                "- Fixed identified issues",
                "- Improved error handling",
                "- Added edge case validation"
            ]
        # New features
        elif commit_type == 'feat' or 'add' in desc_lower or 'new' in desc_lower:
            bullet_points = [
                f"- Implemented {description.lower()}",
                "- Added comprehensive documentation",
                "- Included unit tests"
            ]
        # Documentation
        elif commit_type == 'docs' or 'documentation' in desc_lower:
            bullet_points = [
                "- Updated documentation",
                "- Added code comments",
                "- Improved README"
            ]
        # Tests
        elif commit_type == 'test':
            bullet_points = [
                "- Added unit tests",
                "- Improved test coverage",
                "- Added edge case tests"
            ]
        # Default
        else:
            bullet_points = [
                f"- Implemented {description.lower()}",
                "- Made necessary code changes",
                "- Updated relevant documentation"
            ]
        
        return bullet_points
    
    def _analyze_changes(self, diff: str, files_changed: List[str] = None) -> Dict:
        """Analyze the changes in the diff"""
        changes = {
            'files': files_changed or [],
            'additions': 0,
            'deletions': 0,
            'modified_functions': [],
            'new_files': [],
            'deleted_files': [],
            'modified_files': [],
            'keywords': [],
            'impact': 'LOW'
        }
        
        if not diff:
            return changes
        
        lines = diff.split('\n')
        current_file = None
        
        for line in lines:
            # Track file names
            if line.startswith('+++ b/'):
                current_file = line[6:]
                if current_file not in changes['modified_files']:
                    changes['modified_files'].append(current_file)
            
            # Count additions and deletions
            elif line.startswith('+') and not line.startswith('+++'):
                changes['additions'] += 1
                words = re.findall(r'\b[a-z]{3,}\b', line.lower())
                changes['keywords'].extend(words)
                
                # Detect function definitions
                func_match = re.search(r'def\s+(\w+)\s*\(', line)
                if func_match:
                    changes['modified_functions'].append(func_match.group(1))
                
                class_match = re.search(r'class\s+(\w+)', line)
                if class_match:
                    changes['modified_functions'].append(class_match.group(1))
                
                js_func_match = re.search(r'function\s+(\w+)\s*\(', line)
                if js_func_match:
                    changes['modified_functions'].append(js_func_match.group(1))
                
                react_match = re.search(r'const\s+(\w+)\s*=\s*\(?\)?\s*=>', line)
                if react_match:
                    changes['modified_functions'].append(react_match.group(1))
            
            elif line.startswith('-') and not line.startswith('---'):
                changes['deletions'] += 1
            
            # Detect new/deleted files
            elif line.startswith('new file mode'):
                if current_file:
                    changes['new_files'].append(current_file)
            elif line.startswith('deleted file mode'):
                if current_file:
                    changes['deleted_files'].append(current_file)
        
        # Remove duplicates
        changes['modified_functions'] = list(dict.fromkeys(changes['modified_functions']))
        
        # Determine impact
        total_changes = changes['additions'] + changes['deletions']
        if total_changes > 200:
            changes['impact'] = 'HIGH'
        elif total_changes > 50:
            changes['impact'] = 'MEDIUM'
        else:
            changes['impact'] = 'LOW'
        
        return changes
    
    def _determine_commit_type_and_scope(self, changes: Dict) -> tuple:
        """Determine commit type and scope based on changes"""
        
        keywords = [k.lower() for k in changes.get('keywords', [])]
        files = [f.lower() for f in changes.get('modified_files', [])]
        
        # Check for authentication related changes
        auth_keywords = ['login', 'logout', 'register', 'auth', 'password', 'token', 'jwt', 'session']
        if any(kw in keywords for kw in auth_keywords) or any('auth' in f for f in files):
            return 'auth', 'auth'
        
        # Check for security changes
        security_keywords = ['security', 'vulnerability', 'cve', 'encrypt', 'decrypt']
        if any(kw in keywords for kw in security_keywords):
            return 'security', None
        
        # Check for performance changes
        perf_keywords = ['performance', 'optimize', 'speed', 'fast', 'cache']
        if any(kw in keywords for kw in perf_keywords):
            return 'perf', None
        
        # Check for refactoring
        refactor_keywords = ['refactor', 'clean', 'restructure', 'rename']
        if any(kw in keywords for kw in refactor_keywords):
            return 'refactor', None
        
        # Check for bug fixes
        fix_keywords = ['fix', 'bug', 'error', 'issue', 'crash']
        if any(kw in keywords for kw in fix_keywords):
            return 'fix', None
        
        # Check for new features
        feat_keywords = ['add', 'implement', 'create', 'feature', 'new']
        if any(kw in keywords for kw in feat_keywords):
            return 'feat', None
        
        # Check for documentation
        if any('readme' in f for f in files):
            return 'docs', None
        
        # Check for tests
        if any('test' in f for f in files):
            return 'test', None
        
        return 'chore', None
    
    def _generate_subject(self, changes: Dict, commit_type: str, scope: str = None) -> str:
        """Generate a clean, professional subject line"""
        
        if changes.get('new_files'):
            file_names = [f.split('/')[-1] for f in changes['new_files'][:2]]
            file_str = ', '.join(file_names)
            return f"add {file_str}"
        
        if changes.get('deleted_files'):
            file_names = [f.split('/')[-1] for f in changes['deleted_files'][:2]]
            file_str = ', '.join(file_names)
            return f"remove {file_str}"
        
        if changes.get('modified_functions'):
            funcs = changes['modified_functions'][:3]
            if len(funcs) == 1:
                return f"update {funcs[0]} functionality"
            else:
                func_str = ', '.join(funcs)
                return f"update {func_str}"
        
        keywords = changes.get('keywords', [])
        
        if 'login' in keywords or 'auth' in keywords:
            return "improve login authentication workflow"
        
        if 'api' in keywords:
            return "add new API endpoint"
        
        if 'database' in keywords or 'db' in keywords:
            return "update database schema and queries"
        
        if 'component' in keywords:
            return "add new UI component"
        
        type_messages = {
            'feat': "add new feature",
            'fix': "fix bug and improve stability",
            'docs': "update documentation",
            'refactor': "refactor code for better maintainability",
            'perf': "improve performance",
            'test': "add and update tests",
            'auth': "improve authentication and security",
            'security': "fix security vulnerabilities",
            'chore': "update configuration and dependencies"
        }
        
        return type_messages.get(commit_type, "update codebase")
    
    def _generate_body(self, changes: Dict) -> str:
        """Generate clean bullet-point body"""
        body_parts = []
        
        if changes.get('modified_functions'):
            unique_funcs = list(dict.fromkeys(changes['modified_functions']))
            for func in unique_funcs[:5]:
                body_parts.append(f"- Added backend {func} validation")
        
        if changes.get('modified_files'):
            for file in changes['modified_files'][:3]:
                if 'frontend' in file or 'ui' in file:
                    body_parts.append(f"- Added frontend UI handling for {file.split('/')[-1]}")
                elif 'api' in file or 'route' in file:
                    body_parts.append(f"- Improved API endpoint in {file.split('/')[-1]}")
                elif 'test' in file:
                    body_parts.append(f"- Updated test coverage in {file.split('/')[-1]}")
        
        if not body_parts:
            if changes['additions'] > 0:
                body_parts.append(f"- Added {changes['additions']} lines of new code")
            if changes['deletions'] > 0:
                body_parts.append(f"- Removed {changes['deletions']} lines of deprecated code")
            if changes['modified_functions']:
                body_parts.append(f"- Enhanced {', '.join(changes['modified_functions'][:3])} functions")
        
        body_parts = list(dict.fromkeys(body_parts))
        
        return '\n'.join(body_parts) if body_parts else "- Made general improvements to codebase"
    
    def _generate_footer(self) -> str:
        """Generate the commit footer"""
        return f"""Generated by AI Code Copilot
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
    
    def _format_message(self, commit_type: str, scope: str, subject: str, body: str, footer: str) -> str:
        """Format the complete commit message"""
        emoji = self.commit_types.get(commit_type, self.commit_types['chore'])['emoji']
        
        if scope:
            header = f"{emoji} {commit_type}({scope}): {subject}"
        else:
            header = f"{emoji} {commit_type}: {subject}"
        
        header = header[0].upper() + header[1:]
        
        return f"{header}\n\n{body}\n\n{footer}"
    
    def parse_conventional_commit(self, message: str) -> Dict:
        """Parse a conventional commit message"""
        pattern = r'^(?:[^\s]+\s+)?(feat|fix|docs|style|refactor|perf|test|chore|ci|auth|security)(?:\((\w+)\))?!?: (.+)$'
        match = re.match(pattern, message)
        
        if match:
            return {
                'type': match.group(1),
                'scope': match.group(2),
                'description': match.group(3),
                'is_breaking': '!' in message
            }
        
        return None