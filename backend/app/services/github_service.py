import requests
from typing import Dict, List, Optional, Tuple
import base64
import re

class GitHubService:
    def __init__(self):
        self.api_base = "https://api.github.com"
    
    def get_repo_info(self, owner: str, repo: str) -> Optional[Dict]:
        """Fetch repository information from GitHub API"""
        try:
            url = f"{self.api_base}/repos/{owner}/{repo}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error fetching repo info: {e}")
            return None
    
    def get_repo_contents(self, owner: str, repo: str, path: str = "") -> List[Dict]:
        """Fetch repository contents"""
        try:
            url = f"{self.api_base}/repos/{owner}/{repo}/contents/{path}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            print(f"Error fetching repo contents: {e}")
            return []
    
    def parse_github_url(self, url: str) -> Tuple[Optional[str], Optional[str]]:
        """Parse GitHub URL to get owner and repo name"""
        url = url.rstrip('/')
        if url.endswith('.git'):
            url = url[:-4]
        
        # Match GitHub URLs
        patterns = [
            r'github\.com/([^/]+)/([^/]+)',
            r'github\.com[:/]([^/]+)/([^/]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                owner = match.group(1)
                repo = match.group(2)
                # Remove any trailing .git
                repo = repo.replace('.git', '')
                return owner, repo
        
        return None, None
    
    def scan_repository(self, owner: str, repo: str) -> Dict:
        """Scan entire repository structure"""
        files = []
        
        def scan_directory(path=""):
            contents = self.get_repo_contents(owner, repo, path)
            if not contents:
                return
            
            for item in contents:
                if item.get('type') == 'file':
                    # Skip large files
                    if item.get('size', 0) < 100000:
                        files.append({
                            'name': item.get('name', ''),
                            'path': item.get('path', ''),
                            'size': item.get('size', 0),
                            'type': 'file',
                            'download_url': item.get('download_url')
                        })
                elif item.get('type') == 'dir':
                    scan_directory(item.get('path', ''))
        
        try:
            scan_directory()
        except Exception as e:
            print(f"Error scanning repository: {e}")
        
        return {
            'files': files,
            'total_files': len(files)
        }