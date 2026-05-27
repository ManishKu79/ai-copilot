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
        
        # Generate subject line (clean and professional)
        subject = self._generate_subject(changes, commit_type, scope)
        
        # Generate body (bullet points)
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
            'impact': 'low'
        }
        
        if not diff:
            return changes
        
        lines = diff.split('\n')
        
        # Track current file
        current_file = None
        
        for line in lines:
            # Track file names
            if line.startswith('+++ b/'):
                current_file = line[6:]  # Remove '+++ b/'
                if current_file not in changes['modified_files']:
                    changes['modified_files'].append(current_file)
            elif line.startswith('--- a/'):
                pass
            
            # Count additions and deletions
            elif line.startswith('+') and not line.startswith('+++'):
                changes['additions'] += 1
                # Extract keywords from added lines
                words = re.findall(r'\b[a-z]{3,}\b', line.lower())
                changes['keywords'].extend(words)
                
                # Detect function definitions
                func_match = re.search(r'def\s+(\w+)\s*\(', line)
                if func_match:
                    changes['modified_functions'].append(func_match.group(1))
                
                # Detect class/component definitions
                class_match = re.search(r'class\s+(\w+)', line)
                if class_match:
                    changes['modified_functions'].append(class_match.group(1))
                
                # Detect JavaScript functions
                js_func_match = re.search(r'function\s+(\w+)\s*\(', line)
                if js_func_match:
                    changes['modified_functions'].append(js_func_match.group(1))
                
                # Detect React components
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
        
        # Remove duplicates from modified_functions
        changes['modified_functions'] = list(dict.fromkeys(changes['modified_functions']))
        
        # Determine impact based on changes
        total_changes = changes['additions'] + changes['deletions']
        if total_changes > 200:
            changes['impact'] = 'HIGH'
        elif total_changes > 50:
            changes['impact'] = 'MEDIUM'
        else:
            changes['impact'] = 'LOW'
        
        # Get top keywords
        if changes['keywords']:
            # Filter out common words
            stop_words = {'the', 'and', 'for', 'with', 'this', 'that', 'from', 'are', 'was', 'were'}
            filtered = [w for w in changes['keywords'] if w not in stop_words and len(w) > 2]
            if filtered:
                common = Counter(filtered).most_common(5)
                changes['top_keywords'] = [word for word, count in common]
        
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
        security_keywords = ['security', 'vulnerability', 'cve', 'encrypt', 'decrypt', 'cors', 'csrf']
        if any(kw in keywords for kw in security_keywords):
            return 'security', None
        
        # Check for performance changes
        perf_keywords = ['performance', 'optimize', 'speed', 'fast', 'cache', 'lazy']
        if any(kw in keywords for kw in perf_keywords):
            return 'perf', None
        
        # Check for refactoring
        refactor_keywords = ['refactor', 'clean', 'restructure', 'rename', 'move']
        if any(kw in keywords for kw in refactor_keywords):
            return 'refactor', None
        
        # Check for bug fixes
        fix_keywords = ['fix', 'bug', 'error', 'issue', 'crash', 'exception']
        if any(kw in keywords for kw in fix_keywords):
            return 'fix', None
        
        # Check for new features
        feat_keywords = ['add', 'implement', 'create', 'feature', 'new']
        if any(kw in keywords for kw in feat_keywords):
            return 'feat', None
        
        # Check for documentation
        if any('readme' in f for f in files) or any(kw in ['doc', 'readme'] for kw in keywords):
            return 'docs', None
        
        # Check for tests
        if any('test' in f for f in files):
            return 'test', None
        
        # Default
        return 'chore', None
    
    def _generate_subject(self, changes: Dict, commit_type: str, scope: str = None) -> str:
        """Generate a clean, professional subject line"""
        
        # New files added
        if changes.get('new_files'):
            file_names = [f.split('/')[-1] for f in changes['new_files'][:2]]
            file_str = ', '.join(file_names)
            return f"add {file_str}"
        
        # Deleted files
        if changes.get('deleted_files'):
            file_names = [f.split('/')[-1] for f in changes['deleted_files'][:2]]
            file_str = ', '.join(file_names)
            return f"remove {file_str}"
        
        # Modified functions
        if changes.get('modified_functions'):
            funcs = changes['modified_functions'][:3]
            if len(funcs) == 1:
                return f"update {funcs[0]} functionality"
            else:
                func_str = ', '.join(funcs)
                return f"update {func_str}"
        
        # Specific keywords detection
        keywords = changes.get('top_keywords', [])
        
        if 'login' in keywords or 'auth' in keywords:
            return "improve login authentication workflow"
        
        if 'api' in keywords:
            return "add new API endpoint"
        
        if 'database' in keywords or 'db' in keywords:
            return "update database schema and queries"
        
        if 'component' in keywords:
            return "add new UI component"
        
        # General based on additions/deletions
        if changes['additions'] > changes['deletions'] * 2:
            return "add new features and improvements"
        elif changes['deletions'] > changes['additions'] * 2:
            return "remove deprecated code and clean up"
        
        # Default based on commit type
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
        
        # Add bullet points for key changes
        if changes['modified_functions']:
            unique_funcs = list(dict.fromkeys(changes['modified_functions']))
            for func in unique_funcs[:5]:
                body_parts.append(f"- Added backend {func} validation")
        
        # Add file change summaries
        if changes['modified_files']:
            for file in changes['modified_files'][:3]:
                if 'frontend' in file or 'ui' in file or 'component' in file:
                    body_parts.append(f"- Added frontend UI handling for {file.split('/')[-1]}")
                elif 'api' in file or 'route' in file:
                    body_parts.append(f"- Improved API endpoint in {file.split('/')[-1]}")
                elif 'test' in file:
                    body_parts.append(f"- Updated test coverage in {file.split('/')[-1]}")
        
        # Add generic improvements if no specific items
        if not body_parts:
            if changes['additions'] > 0:
                body_parts.append(f"- Added {changes['additions']} lines of new code")
            if changes['deletions'] > 0:
                body_parts.append(f"- Removed {changes['deletions']} lines of deprecated code")
            if changes['modified_functions']:
                body_parts.append(f"- Enhanced {', '.join(changes['modified_functions'][:3])} functions")
        
        # Remove duplicates
        body_parts = list(dict.fromkeys(body_parts))
        
        # Join with newlines
        return '\n'.join(body_parts) if body_parts else "- Made general improvements to codebase"
    
    def _generate_footer(self) -> str:
        """Generate the commit footer"""
        return f"""Generated by AI Code Copilot
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
    
    def _format_message(self, commit_type: str, scope: str, subject: str, body: str, footer: str) -> str:
        """Format the complete commit message"""
        emoji = self.commit_types.get(commit_type, self.commit_types['chore'])['emoji']
        
        # Format header with scope
        if scope:
            header = f"{emoji} {commit_type}({scope}): {subject}"
        else:
            header = f"{emoji} {commit_type}: {subject}"
        
        # Add changes summary
        header = header[0].upper() + header[1:]  # Capitalize first letter
        
        # Combine all parts
        message_parts = [header, "", body, "", footer]
        
        return '\n'.join(message_parts)
    
    def generate_simple_message(self, description: str, commit_type: str = 'feat') -> Dict:
        """Generate a simple commit message from a description"""
        type_info = self.commit_types.get(commit_type, self.commit_types['chore'])
        
        # Capitalize description
        description = description[0].upper() + description[1:] if description else description
        
        conventional = f"{commit_type}: {description}"
        
        return {
            'success': True,
            'commit_type': commit_type,
            'scope': None,
            'emoji': type_info['emoji'],
            'subject': description,
            'body': "- Made requested changes",
            'footer': self._generate_footer(),
            'full_message': f"{type_info['emoji']} {conventional}\n\n- Made requested changes\n\n{self._generate_footer()}",
            'conventional_format': conventional
        }
    
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