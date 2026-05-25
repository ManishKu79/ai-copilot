import os
import zipfile
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Set, Optional
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
        }
        
    def analyze_zip(self, zip_path: str) -> Dict:
        """Extract and analyze ZIP file"""
        extract_dir = tempfile.mkdtemp()
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            return self.analyze_directory(extract_dir)
        finally:
            shutil.rmtree(extract_dir)
    
    def analyze_github_repo(self, repo_url: str) -> Dict:
        """Clone and analyze GitHub repository"""
        # For Phase 2, we'll simulate analysis
        # In production, you would use git clone
        return {
            "name": repo_url.split('/')[-1],
            "files_count": 42,
            "languages": {"python": 70, "javascript": 30},
            "complexity_score": 7.3,
            "structure": self.get_mock_structure(),
            "technologies": ["React", "FastAPI", "PostgreSQL"]
        }
    
    def analyze_directory(self, dir_path: str) -> Dict:
        """Analyze local directory structure"""
        files = []
        languages = Counter()
        total_lines = 0
        total_complexity = 0
        
        for root, _, filenames in os.walk(dir_path):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                ext = Path(filename).suffix
                
                # Detect language
                for lang, exts in self.language_extensions.items():
                    if ext in exts:
                        languages[lang] += 1
                        break
                
                # Analyze file
                file_info = self.analyze_file(file_path)
                files.append(file_info)
                total_lines += file_info.get('lines', 0)
                total_complexity += file_info.get('complexity', 0)
        
        structure = self.build_structure(dir_path)
        complexity_score = min(10, total_complexity / max(1, len(files)))
        
        return {
            "name": os.path.basename(dir_path),
            "files_count": len(files),
            "languages": dict(languages),
            "total_lines": total_lines,
            "complexity_score": round(complexity_score, 2),
            "structure": structure,
            "technologies": self.detect_technologies(files, structure),
            "files": files[:20]  # Return first 20 files for preview
        }
    
    def analyze_file(self, file_path: str) -> Dict:
        """Analyze individual file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = len(content.splitlines())
                
                # Basic complexity metrics
                complexity = self.calculate_complexity(content, file_path)
                
                return {
                    "path": file_path,
                    "name": os.path.basename(file_path),
                    "extension": Path(file_path).suffix,
                    "lines": lines,
                    "complexity": complexity,
                    "size": os.path.getsize(file_path)
                }
        except Exception as e:
            return {
                "path": file_path,
                "name": os.path.basename(file_path),
                "error": str(e)
            }
    
    def calculate_complexity(self, content: str, file_path: str) -> float:
        """Calculate file complexity"""
        complexity = 0
        
        # Python files get AST analysis
        if file_path.endswith('.py'):
            try:
                tree = ast.parse(content)
                # Count complex structures
                for node in ast.walk(tree):
                    if isinstance(node, (ast.If, ast.While, ast.For)):
                        complexity += 1
                    elif isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                        complexity += 2
                    elif isinstance(node, ast.Try):
                        complexity += 1
            except:
                complexity = len(content.splitlines()) / 100
        
        # JavaScript/TypeScript files
        elif file_path.endswith(('.js', '.jsx', '.ts', '.tsx')):
            complexity = content.count('if') + content.count('for') + content.count('while')
            complexity = complexity / 10
        
        else:
            complexity = len(content.splitlines()) / 100
        
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
                    item_path = os.path.join(path, item)
                    if os.path.isdir(item_path) and not item.startswith('.'):
                        items.append({
                            "name": item,
                            "type": "directory",
                            "children": build_tree(item_path, current_depth + 1)
                        })
                    elif not item.startswith('.'):
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
        """Detect technologies used in the repository"""
        technologies = set()
        
        # Check package files
        for file in files:
            if file['name'] == 'package.json':
                technologies.add('Node.js')
                technologies.add('npm')
            elif file['name'] == 'requirements.txt':
                technologies.add('Python')
                technologies.add('pip')
            elif file['name'] == 'Dockerfile':
                technologies.add('Docker')
            elif file['name'] == '.github/workflows':
                technologies.add('GitHub Actions')
        
        # Check for frameworks
        all_content = ''
        for file in files[:50]:
            if file.get('error'):
                continue
        
        return sorted(list(technologies))[:10]
    
    def get_mock_structure(self):
        """Mock structure for GitHub repos (simplified for Phase 2)"""
        return {
            "name": "repository",
            "type": "directory",
            "children": [
                {"name": "src", "type": "directory", "children": [
                    {"name": "index.js", "type": "file", "extension": ".js"},
                    {"name": "app.js", "type": "file", "extension": ".js"}
                ]},
                {"name": "tests", "type": "directory", "children": [
                    {"name": "test.js", "type": "file", "extension": ".js"}
                ]},
                {"name": "README.md", "type": "file", "extension": ".md"}
            ]
        }