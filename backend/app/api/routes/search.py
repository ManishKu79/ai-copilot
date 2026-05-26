from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from pathlib import Path
import re
from collections import defaultdict

router = APIRouter()

# Simple in-memory search index
class SearchIndex:
    def __init__(self):
        self.index = {}  # file_path -> content
        self.keywords_index = defaultdict(list)  # keyword -> list of file paths
    
    def clear(self):
        self.index = {}
        self.keywords_index = defaultdict(list)
    
    def index_repository(self, repository_data: Dict) -> int:
        """Index all files in repository"""
        files = repository_data.get('files_preview', [])
        structure = repository_data.get('structure', {})
        
        indexed_count = 0
        
        # Index files from files_preview
        for file in files:
            file_path = file.get('path', file.get('name', ''))
            file_name = file.get('name', '')
            
            # Create searchable content from available metadata
            content = f"{file_name} {file.get('extension', '')} {file.get('path', '')}"
            
            # Add file to index
            self.index[file_path] = {
                'content': content,
                'name': file_name,
                'path': file_path,
                'extension': file.get('extension', ''),
                'lines': file.get('lines', 0)
            }
            
            # Index keywords
            tokens = self._tokenize(content)
            for token in tokens:
                if len(token) > 2:
                    self.keywords_index[token].append(file_path)
            
            indexed_count += 1
        
        # Also index structure if available
        if structure:
            self._index_structure(structure)
        
        return indexed_count
    
    def _index_structure(self, node, path=""):
        """Recursively index folder structure"""
        node_name = node.get('name', '')
        node_type = node.get('type', 'file')
        
        current_path = f"{path}/{node_name}" if path else node_name
        
        if node_type == 'directory':
            content = f"directory {node_name} folder"
            tokens = self._tokenize(content)
            for token in tokens:
                if len(token) > 2:
                    self.keywords_index[token].append(current_path)
            
            # Index children
            for child in node.get('children', []):
                self._index_structure(child, current_path)
        else:
            # Index file
            content = f"file {node_name} {node.get('extension', '')}"
            tokens = self._tokenize(content)
            for token in tokens:
                if len(token) > 2:
                    self.keywords_index[token].append(current_path)
    
    def _tokenize(self, text: str) -> List[str]:
        """Convert text into searchable tokens"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters
        text = re.sub(r'[^\w\s\.\_\-]', ' ', text)
        
        # Split into words
        tokens = text.split()
        
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                      'of', 'with', 'by', 'from', 'up', 'down', 'is', 'it', 'be', 'are',
                      'was', 'were', 'been', 'being', 'have', 'has', 'had', 'having',
                      'do', 'does', 'did', 'doing', 'get', 'gets', 'got', 'getting',
                      'this', 'that', 'these', 'those', 'there', 'their', 'they'}
        
        tokens = [t for t in tokens if t not in stop_words]
        
        return tokens
    
    def search(self, query: str, max_results: int = 20) -> List[Dict]:
        """Search for files matching query"""
        query_tokens = self._tokenize(query)
        
        if not query_tokens:
            return []
        
        # Score each file based on keyword matches
        scores = defaultdict(float)
        match_counts = defaultdict(int)
        
        for token in query_tokens:
            if token in self.keywords_index:
                for file_path in self.keywords_index[token]:
                    # Calculate token frequency in file
                    if file_path in self.index:
                        file_content = self.index[file_path].get('content', '')
                        token_count = file_content.lower().count(token)
                    else:
                        token_count = 1
                    
                    scores[file_path] += token_count * (1.0 / len(query_tokens))
                    match_counts[file_path] += 1
        
        # Sort by score
        sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        results = []
        for file_path, score in sorted_results[:max_results]:
            if file_path in self.index:
                file_data = self.index[file_path]
                
                # Extract snippet
                snippet = self._extract_snippet(file_data.get('content', ''), query_tokens)
                
                results.append({
                    'file_path': file_path,
                    'file_name': file_data.get('name', Path(file_path).name),
                    'score': round(min(100, score * 100), 2),
                    'snippet': snippet,
                    'matches': match_counts[file_path],
                    'metadata': {
                        'extension': file_data.get('extension', ''),
                        'lines': file_data.get('lines', 0)
                    }
                })
            else:
                # For structure items without full file data
                results.append({
                    'file_path': file_path,
                    'file_name': Path(file_path).name if '/' in file_path else file_path,
                    'score': round(min(100, score * 100), 2),
                    'snippet': f"Found in: {file_path}",
                    'matches': match_counts[file_path],
                    'metadata': {}
                })
        
        return results
    
    def _extract_snippet(self, content: str, query_tokens: List[str], context_chars: int = 150) -> str:
        """Extract relevant snippet around matches"""
        if not content:
            return "No content preview available"
        
        content_lower = content.lower()
        
        # Find position of first match
        first_match_pos = -1
        for token in query_tokens:
            pos = content_lower.find(token)
            if pos != -1 and (first_match_pos == -1 or pos < first_match_pos):
                first_match_pos = pos
        
        if first_match_pos == -1:
            # Return beginning of content
            return content[:context_chars] + ('...' if len(content) > context_chars else '')
        
        # Extract context around match
        start = max(0, first_match_pos - context_chars // 2)
        end = min(len(content), first_match_pos + context_chars // 2)
        
        snippet = content[start:end]
        
        # Add ellipsis
        if start > 0:
            snippet = '...' + snippet
        if end < len(content):
            snippet = snippet + '...'
        
        return snippet


# Create global search index instance
search_index = SearchIndex()


class IndexRequest(BaseModel):
    repository_data: Dict[str, Any]


class SearchRequest(BaseModel):
    query: str
    max_results: Optional[int] = 20


@router.post("/index")
async def index_repository(request: IndexRequest):
    """Index a repository for searching"""
    if not request.repository_data:
        raise HTTPException(status_code=400, detail="Repository data required")
    
    try:
        indexed_count = search_index.index_repository(request.repository_data)
        return {
            "success": True,
            "indexed_files": indexed_count,
            "message": f"Successfully indexed {indexed_count} files"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Indexing failed: {str(e)}")


@router.post("/search")
async def search_code(request: SearchRequest):
    """Search for code using natural language query"""
    if not request.query or len(request.query.strip()) == 0:
        raise HTTPException(status_code=400, detail="Search query required")
    
    try:
        results = search_index.search(request.query, request.max_results)
        
        return {
            "success": True,
            "query": request.query,
            "total_results": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.post("/clear-index")
async def clear_index():
    """Clear the search index"""
    search_index.clear()
    return {
        "success": True,
        "message": "Search index cleared successfully"
    }


@router.get("/status")
async def get_index_status():
    """Get current index status"""
    return {
        "success": True,
        "indexed_files": len(search_index.index),
        "keywords_count": len(search_index.keywords_index)
    }