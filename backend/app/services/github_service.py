import requests
from typing import Dict, List, Optional
import base64

class GitHubService:
    def __init__(self):
        self.api_base = "https://api.github.com"
    
    def get_repo_info(self, owner: str, repo: str) -> Optional[Dict]:
        """Fetch repository information from GitHub API"""
        try:
            url = f"{self.api_base}/repos/{owner}/{repo}"
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except:
            return None
    
    def get_repo_contents(self, owner: str, repo: str, path: str = "") -> List[Dict]:
        """Fetch repository contents"""
        try:
            url = f"{self.api_base}/repos/{owner}/{repo}/contents/{path}"
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except:
            return []
    
    def parse_github_url(self, url: str) -> tuple:
        """Parse GitHub URL to get owner and repo name"""
        # Remove trailing slash and .git if present
        url = url.rstrip('/')
        if url.endswith('.git'):
            url = url[:-4]
        
        parts = url.split('/')
        if 'github.com' in url:
            try:
                owner = parts[-2]
                repo = parts[-1]
                return owner, repo
            except:
                pass
        
        return None, None