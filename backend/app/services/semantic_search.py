import numpy as np
from typing import List, Dict, Any, Optional
from collections import defaultdict
import re
from pathlib import Path

class SemanticSearch:
    def __init__(self):
        self.index = {}  # file_path -> content index
        self.embeddings = {}  # file_path -> vector embedding
        self.keywords_index = defaultdict(list)  # keyword -> list of file paths
        
    def index_repository(self, repository_data: Dict) -> Dict:
        """Index all files in a repository for searching"""
        files = repository_data.get('files_preview', [])
        structure = repository_data.get('structure', {})
        
        indexed_count = 0
        for file in files:
            if file.get('error'):
                continue
            
            file_path = file.get('path', '')
            file_name = file.get('name', '')
            
            # Index file content if available
            if 'content' in file:
                self._index_file(file_path, file['content'])
                indexed_count += 1
            else:
                # Simulate indexing with available metadata
                self._index_file_metadata(file_path, file)
                indexed_count += 1
        
        return {
            'success': True,
            'indexed_files': indexed_count,
            'repository': repository_data.get('name', 'unknown')
        }
    
    def _index_file(self, file_path: str, content: str):
        """Index file content for searching"""
        # Store content
        self.index[file_path] = {
            'content': content,
            'tokens': self._tokenize(content)
        }
        
        # Build keyword index
        tokens = set(self._tokenize(content))
        for token in tokens:
            if len(token) > 2:  # Ignore very short tokens
                self.keywords_index[token].append(file_path)
    
    def _index_file_metadata(self, file_path: str, file_metadata: Dict):
        """Index file based on metadata when content isn't available"""
        file_name = file_metadata.get('name', '')
        content_preview = f"{file_name} {file_metadata.get('extension', '')} {file_metadata.get('path', '')}"
        
        self.index[file_path] = {
            'content': content_preview,
            'tokens': self._tokenize(content_preview),
            'metadata': file_metadata
        }
        
        tokens = set(self._tokenize(content_preview))
        for token in tokens:
            if len(token) > 2:
                self.keywords_index[token].append(file_path)
    
    def _tokenize(self, text: str) -> List[str]:
        """Convert text into searchable tokens"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep underscores and dots
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
        """Search for code matching natural language query"""
        query_tokens = self._tokenize(query)
        
        if not query_tokens:
            return []
        
        # Score each file based on keyword matches
        scores = defaultdict(float)
        
        for token in query_tokens:
            if token in self.keywords_index:
                for file_path in self.keywords_index[token]:
                    # Simple TF scoring - more occurrences = higher score
                    token_count = self.index[file_path]['tokens'].count(token)
                    scores[file_path] += token_count * (1.0 / len(query_tokens))
        
        # Get top results
        sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        results = []
        for file_path, score in sorted_results[:max_results]:
            file_data = self.index.get(file_path, {})
            content = file_data.get('content', '')
            metadata = file_data.get('metadata', {})
            
            # Extract relevant snippet
            snippet = self._extract_snippet(content, query_tokens)
            
            results.append({
                'file_path': file_path,
                'file_name': Path(file_path).name,
                'score': round(score * 100, 2),  # Convert to percentage
                'snippet': snippet,
                'matches': self._get_match_count(file_data.get('tokens', []), query_tokens),
                'metadata': metadata
            })
        
        return results
    
    def _extract_snippet(self, content: str, query_tokens: List[str], context_lines: int = 2) -> str:
        """Extract relevant code snippet around matches"""
        if not content:
            return "No content preview available"
        
        lines = content.split('\n')
        
        # Find line numbers containing query tokens
        matching_lines = []
        for i, line in enumerate(lines):
            line_lower = line.lower()
            for token in query_tokens:
                if token in line_lower:
                    matching_lines.append(i)
                    break
        
        if not matching_lines:
            # Return first few lines as preview
            return '\n'.join(lines[:5])
        
        # Get context around first match
        first_match = matching_lines[0]
        start = max(0, first_match - context_lines)
        end = min(len(lines), first_match + context_lines + 1)
        
        snippet_lines = []
        for i in range(start, end):
            line = lines[i]
            # Highlight matching tokens
            for token in query_tokens:
                if token.lower() in line.lower():
                    line = re.sub(f'({token})', r'**\1**', line, flags=re.IGNORECASE)
            snippet_lines.append(line)
        
        return '\n'.join(snippet_lines)
    
    def _get_match_count(self, file_tokens: List[str], query_tokens: List[str]) -> int:
        """Count how many query tokens appear in the file"""
        file_tokens_set = set(file_tokens)
        return sum(1 for token in query_tokens if token in file_tokens_set)
    
    def clear_index(self):
        """Clear the search index"""
        self.index = {}
        self.keywords_index = defaultdict(list)
        self.embeddings = {}


class AdvancedSemanticSearch(SemanticSearch):
    """Extended search with semantic understanding using sentence transformers"""
    
    def __init__(self):
        super().__init__()
        self.use_embeddings = False
        
        # Try to load sentence transformers if available
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.use_embeddings = True
            print("Semantic search with embeddings enabled")
        except ImportError:
            print("sentence-transformers not available. Using keyword search only.")
    
    def _create_embedding(self, text: str) -> Optional[np.ndarray]:
        """Create vector embedding for text"""
        if not self.use_embeddings:
            return None
        
        try:
            # Truncate long text for performance
            if len(text) > 5000:
                text = text[:5000]
            return self.model.encode(text)
        except Exception as e:
            print(f"Embedding creation failed: {e}")
            return None
    
    def _index_file(self, file_path: str, content: str):
        """Index file with embeddings for semantic search"""
        super()._index_file(file_path, content)
        
        # Create and store embedding
        if self.use_embeddings:
            embedding = self._create_embedding(content)
            if embedding is not None:
                self.embeddings[file_path] = embedding
    
    def semantic_search(self, query: str, max_results: int = 20) -> List[Dict]:
        """Search using semantic understanding"""
        # First try keyword search
        keyword_results = self.search(query, max_results * 2)
        
        # If embeddings are available, re-rank using semantic similarity
        if self.use_embeddings and self.embeddings:
            query_embedding = self._create_embedding(query)
            
            if query_embedding is not None:
                # Calculate cosine similarity with all indexed files
                similarities = {}
                for file_path, embedding in self.embeddings.items():
                    similarity = np.dot(query_embedding, embedding) / (
                        np.linalg.norm(query_embedding) * np.linalg.norm(embedding)
                    )
                    similarities[file_path] = float(similarity)
                
                # Sort by similarity
                semantic_results = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
                
                # Combine with keyword results (weighted average)
                combined_scores = defaultdict(float)
                
                for file_path, score in keyword_results:
                    combined_scores[file_path] += score * 0.4
                
                for file_path, similarity in semantic_results[:max_results]:
                    combined_scores[file_path] += similarity * 100 * 0.6
                
                # Re-sort combined results
                sorted_combined = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
                
                # Build results
                results = []
                for file_path, score in sorted_combined[:max_results]:
                    file_data = self.index.get(file_path, {})
                    content = file_data.get('content', '')
                    
                    snippet = self._extract_snippet(content, self._tokenize(query))
                    
                    results.append({
                        'file_path': file_path,
                        'file_name': Path(file_path).name,
                        'score': round(score, 2),
                        'snippet': snippet,
                        'semantic_score': round(similarities.get(file_path, 0) * 100, 2),
                        'metadata': file_data.get('metadata', {})
                    })
                
                return results
        
        # Fallback to keyword search
        return keyword_results