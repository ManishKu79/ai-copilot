import { useState, useEffect } from 'react'
import { 
  Search, 
  FileCode, 
  X, 
  ChevronRight,
  Database,
  RefreshCw,
  Sparkles,
  AlertCircle
} from 'lucide-react'
import useAppStore from '../store/useAppStore'
import { searchAPI } from '../services/api'

export default function CodeSearch() {
  const { currentAnalysis } = useAppStore()
  const [query, setQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [indexed, setIndexed] = useState(false)
  const [indexing, setIndexing] = useState(false)
  const [selectedFile, setSelectedFile] = useState(null)
  const [recentSearches, setRecentSearches] = useState([])

  // Load recent searches from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('recentCodeSearches')
    if (saved) {
      setRecentSearches(JSON.parse(saved))
    }
  }, [])

  const saveRecentSearch = (searchQuery) => {
    const updated = [searchQuery, ...recentSearches.filter(s => s !== searchQuery)].slice(0, 5)
    setRecentSearches(updated)
    localStorage.setItem('recentCodeSearches', JSON.stringify(updated))
  }

  const indexRepository = async () => {
    if (!currentAnalysis) {
      alert('Please analyze a repository first')
      return
    }

    setIndexing(true)
    try {
      const result = await searchAPI.indexRepository(currentAnalysis)
      if (result.success) {
        setIndexed(true)
        alert(`Successfully indexed ${result.indexed_files} files`)
      }
    } catch (error) {
      console.error('Indexing failed:', error)
      alert('Failed to index repository')
    } finally {
      setIndexing(false)
    }
  }

  const handleSearch = async () => {
    if (!query.trim()) return
    
    if (!indexed && !currentAnalysis) {
      alert('Please index a repository first')
      return
    }

    setLoading(true)
    try {
      const result = await searchAPI.semanticSearch(query)
      if (result.success) {
        setSearchResults(result.results)
        saveRecentSearch(query)
      }
    } catch (error) {
      console.error('Search failed:', error)
      alert('Search failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch()
    }
  }

  const clearSearch = () => {
    setQuery('')
    setSearchResults([])
  }

  const getScoreColor = (score) => {
    if (score >= 70) return 'text-green-400'
    if (score >= 40) return 'text-yellow-400'
    return 'text-gray-400'
  }

  const highlightMatches = (text, query) => {
    if (!text || !query) return text
    
    const words = query.toLowerCase().split(' ')
    let highlighted = text
    
    words.forEach(word => {
      const regex = new RegExp(`(${word})`, 'gi')
      highlighted = highlighted.replace(regex, '<mark class="bg-yellow-500/30 text-yellow-200 px-0.5 rounded">$1</mark>')
    })
    
    return highlighted
  }

  return (
    <div>
      <h1 className="text-2xl font-semibold mb-6">Smart Code Search</h1>
      
      {/* Search Header */}
      <div className="card mb-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center">
            <Sparkles className="w-5 h-5 text-purple-400 mr-2" />
            <h2 className="text-lg font-semibold">Semantic Code Search</h2>
          </div>
          
          <button
            onClick={indexRepository}
            disabled={indexing || !currentAnalysis}
            className="btn-secondary flex items-center text-sm"
          >
            <Database className="w-4 h-4 mr-2" />
            {indexing ? 'Indexing...' : (indexed ? 'Re-index' : 'Index Repository')}
          </button>
        </div>
        
        {/* Search Input */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-dark-400" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Search your codebase naturally... e.g., 'find all API endpoint handlers' or 'where do we handle authentication'"
            className="w-full bg-dark-700 rounded-md pl-10 pr-10 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          {query && (
            <button
              onClick={clearSearch}
              className="absolute right-3 top-1/2 transform -translate-y-1/2"
            >
              <X className="w-4 h-4 text-dark-400 hover:text-dark-200" />
            </button>
          )}
        </div>
        
        {/* Search Button */}
        <button
          onClick={handleSearch}
          disabled={loading || !query}
          className="mt-4 btn-primary w-full flex items-center justify-center"
        >
          {loading ? (
            <>
              <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
              Searching...
            </>
          ) : (
            <>
              <Search className="w-4 h-4 mr-2" />
              Search Code
            </>
          )}
        </button>
        
        {/* Recent Searches */}
        {recentSearches.length > 0 && !searchResults.length && (
          <div className="mt-4">
            <p className="text-xs text-dark-400 mb-2">Recent searches:</p>
            <div className="flex flex-wrap gap-2">
              {recentSearches.map((s, idx) => (
                <button
                  key={idx}
                  onClick={() => setQuery(s)}
                  className="text-xs px-2 py-1 bg-dark-700 rounded-md hover:bg-dark-600 transition-colors"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}
        
        {/* Index Status */}
        {!indexed && currentAnalysis && (
          <div className="mt-4 p-3 bg-yellow-500/10 border border-yellow-500/20 rounded-md flex items-center text-sm">
            <AlertCircle className="w-4 h-4 text-yellow-400 mr-2" />
            <span className="text-yellow-300">Repository not indexed. Click "Index Repository" to enable search.</span>
          </div>
        )}
      </div>
      
      {/* Search Results */}
      {searchResults.length > 0 && (
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">
              Results ({searchResults.length})
            </h2>
            <p className="text-sm text-dark-400">
              Relevance score: higher = better match
            </p>
          </div>
          
          <div className="space-y-3">
            {searchResults.map((result, idx) => (
              <div
                key={idx}
                className="border border-dark-700 rounded-lg hover:border-dark-600 transition-colors"
              >
                <div
                  className="p-4 cursor-pointer"
                  onClick={() => setSelectedFile(selectedFile === result.file_path ? null : result.file_path)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center mb-2">
                        <FileCode className="w-4 h-4 text-blue-400 mr-2" />
                        <span className="font-mono text-sm font-medium">{result.file_name}</span>
                        <span className="ml-3 text-xs text-dark-400">{result.file_path}</span>
                      </div>
                      
                      <div className="text-sm text-dark-300 mb-2">
                        <div 
                          className="font-mono text-xs"
                          dangerouslySetInnerHTML={{ 
                            __html: highlightMatches(result.snippet, query) 
                          }}
                        />
                      </div>
                      
                      <div className="flex items-center space-x-4 text-xs">
                        <span className={`font-medium ${getScoreColor(result.score)}`}>
                          Relevance: {result.score}%
                        </span>
                        {result.semantic_score && (
                          <span className="text-purple-400">
                            Semantic: {result.semantic_score}%
                          </span>
                        )}
                        <span className="text-dark-400">
                          Matches: {result.matches || 'N/A'}
                        </span>
                      </div>
                    </div>
                    <ChevronRight className={`w-4 h-4 text-dark-400 transition-transform ${selectedFile === result.file_path ? 'rotate-90' : ''}`} />
                  </div>
                </div>
                
                {selectedFile === result.file_path && (
                  <div className="border-t border-dark-700 p-4 bg-dark-800/50">
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="text-sm font-medium">Full Context</h4>
                      <button className="text-xs text-blue-400 hover:text-blue-300">
                        View Full File
                      </button>
                    </div>
                    <pre className="bg-dark-900 rounded p-3 overflow-x-auto text-xs font-mono">
                      <code>{result.snippet}</code>
                    </pre>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* No Results State */}
      {searchResults.length === 0 && query && !loading && (
        <div className="card text-center py-12">
          <Search className="w-12 h-12 text-dark-400 mx-auto mb-3" />
          <h3 className="text-lg font-medium mb-2">No results found</h3>
          <p className="text-dark-300">
            Try different keywords or check if the repository is indexed
          </p>
        </div>
      )}
      
      {/* Example Queries */}
      {!searchResults.length && !query && currentAnalysis && indexed && (
        <div className="card">
          <h3 className="text-sm font-medium mb-3">Example queries you can try:</h3>
          <div className="flex flex-wrap gap-2">
            {[
              'authentication handler',
              'database connection',
              'error handling middleware',
              'API endpoint definitions',
              'utility functions for string processing',
              'configuration settings'
            ].map((example, idx) => (
              <button
                key={idx}
                onClick={() => setQuery(example)}
                className="text-xs px-3 py-1 bg-dark-700 rounded-full hover:bg-dark-600 transition-colors"
              >
                {example}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}