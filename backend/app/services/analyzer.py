import os
import zipfile
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
import ast
from collections import Counter

class RepositoryAnalyzer:
    def __init__(self):
        self.language_extensions = {
            'python': ['.py'],
            'javascript': ['.js', '.jsx'],
            'typescript': ['.ts', '.tsx'],
            'html': ['.html', '.htm'],
            'css': ['.css', '.scss', '.sass'],
            'json': ['.json'],
            'markdown': ['.md'],
            'java': ['.java'],
            'go': ['.go'],
            'rust': ['.rs'],
        }
        
    def analyze_zip(self, zip_path: str) -> Dict:
        """Extract and analyze ZIP file"""
        extract_dir = tempfile.mkdtemp()
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            # Find the root directory (if files are in a subfolder)
            items = os.listdir(extract_dir)
            if len(items) == 1 and os.path.isdir(os.path.join(extract_dir, items[0])):
                extract_dir = os.path.join(extract_dir, items[0])
            
            return self.analyze_directory(extract_dir)
        except Exception as e:
            return {
                "error": f"Failed to analyze ZIP: {str(e)}",
                "name": os.path.basename(zip_path),
                "files_count": 0,
                "languages": {},
                "total_lines": 0,
                "complexity_score": 0,
                "structure": {"name": "empty", "type": "directory", "children": []},
                "technologies": [],
                "files_preview": []
            }
        finally:
            # Clean up temp directory
            if os.path.exists(extract_dir):
                shutil.rmtree(extract_dir, ignore_errors=True)
    
    def analyze_github_repo(self, repo_url: str) -> Dict:
        """Analyze GitHub repository from URL"""
        # Extract repo name from URL
        repo_name = repo_url.split('/')[-1]
        if repo_name.endswith('.git'):
            repo_name = repo_name[:-4]
        
        # For now, return a basic structure without fake files
        # In production, this would fetch from GitHub API
        return {
            "name": repo_name,
            "files_count": 0,
            "languages": {},
            "total_lines": 0,
            "complexity_score": 5.0,
            "structure": {
                "name": repo_name,
                "type": "directory",
                "children": []
            },
            "technologies": [],
            "files_preview": [],
            "github_info": {
                "stars": 0,
                "forks": 0,
                "description": "GitHub repository - upload ZIP file for full analysis",
                "default_branch": "main"
            },
            "message": "For complete analysis, please download and upload the repository as a ZIP file"
        }
    
    def analyze_directory(self, dir_path: str) -> Dict:
        """Analyze local directory structure"""
        files = []
        languages = Counter()
        total_lines = 0
        total_complexity = 0
        
        try:
            for root, _, filenames in os.walk(dir_path):
                for filename in filenames:
                    # Skip hidden files and common ignored directories
                    if filename.startswith('.') or any(ignored in root for ignored in ['node_modules', '__pycache__', '.git', 'venv', 'env', 'dist', 'build']):
                        continue
                    
                    file_path = os.path.join(root, filename)
                    ext = Path(filename).suffix.lower()
                    
                    # Detect language
                    detected = False
                    for lang, exts in self.language_extensions.items():
                        if ext in exts:
                            languages[lang] += 1
                            detected = True
                            break
                    
                    if not detected and ext:
                        languages['other'] = languages.get('other', 0) + 1
                    
                    # Analyze file
                    file_info = self.analyze_file(file_path)
                    if file_info:
                        files.append(file_info)
                        total_lines += file_info.get('lines', 0)
                        total_complexity += file_info.get('complexity', 0)
        except Exception as e:
            print(f"Error analyzing directory: {e}")
        
        # Build structure for visualization
        structure = self.build_structure(dir_path)
        
        # Calculate average complexity
        avg_complexity = total_complexity / max(1, len(files))
        complexity_score = min(10, avg_complexity * 2)
        
        # Detect technologies
        technologies = self.detect_technologies(files, structure)
        
        return {
            "name": os.path.basename(dir_path),
            "files_count": len(files),
            "languages": dict(languages.most_common(5)),
            "total_lines": total_lines,
            "complexity_score": round(complexity_score, 2),
            "structure": structure,
            "technologies": technologies,
            "files_preview": files[:100]  # Send up to 100 files
        }
    
    def analyze_file(self, file_path: str) -> Optional[Dict]:
        """Analyze individual file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = len(content.splitlines())
                
                if lines == 0:
                    return None
                
                complexity = self.calculate_complexity(content, file_path)
                
                # Determine file type
                file_name = os.path.basename(file_path).lower()
                is_test = (
                    'test' in file_name or 
                    'spec' in file_name or 
                    file_name.startswith('test_') or 
                    file_name.endswith('_test.py') or
                    '/test/' in file_path or
                    '/tests/' in file_path
                )
                
                is_documentation = file_path.endswith(('.md', '.txt', '.rst', '.adoc')) or 'readme' in file_name
                
                return {
                    "path": file_path,
                    "name": os.path.basename(file_path),
                    "extension": Path(file_path).suffix,
                    "lines": lines,
                    "complexity": min(10, round(complexity, 2)),
                    "size": os.path.getsize(file_path),
                    "is_test": is_test,
                    "is_documentation": is_documentation,
                    "is_source": not is_test and not is_documentation and file_path.endswith(('.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.rs'))
                }
        except Exception as e:
            return None
    
    def calculate_complexity(self, content: str, file_path: str) -> float:
        """Calculate file complexity"""
        complexity = 1.0
        lines = content.splitlines()
        
        if not lines:
            return 0
        
        lines_count = len(lines)
        complexity += lines_count / 100  # Base complexity from size
        
        # Python AST analysis
        if file_path.endswith('.py'):
            try:
                tree = ast.parse(content)
                complex_nodes = 0
                for node in ast.walk(tree):
                    if isinstance(node, (ast.If, ast.While, ast.For)):
                        complex_nodes += 1
                    elif isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                        complex_nodes += 2
                    elif isinstance(node, ast.Try):
                        complex_nodes += 1
                complexity += complex_nodes / 10
            except:
                pass
        
        # JavaScript/TypeScript analysis
        elif file_path.endswith(('.js', '.jsx', '.ts', '.tsx')):
            complexity += (content.count('if') + content.count('for') + content.count('while')) / 20
            complexity += content.count('=>') / 50
            complexity += content.count('function') / 30
        
        return min(10, complexity)
    
    def build_structure(self, dir_path: str, max_depth: int = 3) -> Dict:
        """Build folder structure tree"""
        structure = {"name": os.path.basename(dir_path), "type": "directory", "children": []}
        
        def build_tree(path, current_depth):
            if current_depth > max_depth:
                return []
            
            items = []
            try:
                for item in sorted(os.listdir(path)):
                    if item.startswith('.') or item in ['node_modules', '__pycache__', 'venv', 'env', '.git', 'dist', 'build']:
                        continue
                    
                    item_path = os.path.join(path, item)
                    if os.path.isdir(item_path):
                        items.append({
                            "name": item,
                            "type": "directory",
                            "children": build_tree(item_path, current_depth + 1)
                        })
                    else:
                        items.append({
                            "name": item,
                            "type": "file",
                            "extension": Path(item).suffix
                        })
            except:
                pass
            
            return items
        
        structure["children"] = build_tree(dir_path, 1)
        return structure
    
    def detect_technologies(self, files: List[Dict], structure: Dict) -> List[str]:
        """Detect technologies used"""
        technologies = set()
        
        for file in files:
            name = file.get('name', '').lower()
            if name == 'requirements.txt':
                technologies.add('Python')
            elif name == 'package.json':
                technologies.add('Node.js')
                technologies.add('npm')
            elif name == 'yarn.lock':
                technologies.add('Yarn')
            elif name == 'dockerfile':
                technologies.add('Docker')
            elif 'docker-compose' in name:
                technologies.add('Docker Compose')
            elif name.endswith('.py'):
                technologies.add('Python')
            elif name.endswith(('.js', '.jsx')):
                technologies.add('JavaScript')
                if 'react' in name or file.get('content', '').find('React') != -1:
                    technologies.add('React')
            elif name.endswith(('.ts', '.tsx')):
                technologies.add('TypeScript')
            elif name == 'pom.xml':
                technologies.add('Java')
                technologies.add('Maven')
        
        return sorted(list(technologies))[:8]