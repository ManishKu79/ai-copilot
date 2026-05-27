import { useState, useRef } from 'react'
import { Upload, FolderTree, Code, BarChart3, AlertCircle, Star, GitFork, Eye, AlertOctagon } from 'lucide-react'
import { analysisAPI } from '../services/api'
import useAppStore from '../store/useAppStore'

// Simple GitHub SVG icon component
const GitHubIcon = ({ className = "w-4 h-4 mr-2" }) => (
  <svg className={className} fill="currentColor" viewBox="0 0 24 24">
    <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026.8-.223 1.65-.334 2.5-.334.85 0 1.7.111 2.5.334 1.91-1.295 2.75-1.026 2.75-1.026.544 1.378.201 2.397.099 2.65.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
  </svg>
)

export default function RepositoryAnalysis() {
  const [repoUrl, setRepoUrl] = useState('')
  const [uploadedFile, setUploadedFile] = useState(null)
  const [analyzing, setAnalyzing] = useState(false)
  const [error, setError] = useState(null)
  const fileInputRef = useRef(null)
  const { currentAnalysis, setCurrentAnalysis } = useAppStore()

  const handleFileUpload = async (e) => {
    const file = e.target.files[0]
    if (file && file.name.endsWith('.zip')) {
      setUploadedFile(file)
      await analyzeZip(file)
    } else {
      setError('Please upload a valid ZIP file')
    }
  }

  const analyzeZip = async (file) => {
    setAnalyzing(true)
    setError(null)
    try {
      const result = await analysisAPI.uploadZip(file)
      if (result.success) {
        setCurrentAnalysis(result.analysis)
      } else {
        setError('Analysis failed')
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Analysis failed')
    } finally {
      setAnalyzing(false)
    }
  }

  const analyzeGithub = async () => {
    if (!repoUrl) {
      setError('Please enter a GitHub repository URL')
      return
    }
    
    setAnalyzing(true)
    setError(null)
    try {
      const result = await analysisAPI.analyzeGithub(repoUrl)
      if (result.success) {
        setCurrentAnalysis(result.analysis)
      } else {
        setError(result.message || 'Analysis failed')
      }
    } catch (err) {
      setError(err.message || 'GitHub analysis failed. Please check the URL and try again.')
    } finally {
      setAnalyzing(false)
    }
  }

  const FileTree = ({ structure, level = 0 }) => {
    if (!structure || !structure.children) return null
    
    return (
      <div className="space-y-1">
        {structure.children.map((item, idx) => (
          <div key={idx}>
            <div className="flex items-center text-sm py-0.5 hover:bg-dark-700 rounded px-2">
              {item.type === 'directory' ? (
                <FolderTree className="w-4 h-4 text-blue-400 mr-2 flex-shrink-0" />
              ) : (
                <Code className="w-4 h-4 text-gray-400 mr-2 flex-shrink-0" />
              )}
              <span className={item.type === 'directory' ? 'font-medium text-blue-300' : 'text-gray-300'}>
                {item.name}
              </span>
            </div>
            {item.children && item.children.length > 0 && (
              <div className="ml-4">
                <FileTree structure={item} level={level + 1} />
              </div>
            )}
          </div>
        ))}
      </div>
    )
  }

  return (
    <div>
      <h1 className="text-2xl font-semibold mb-6">Repository Analysis</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Panel - Input */}
        <div className="space-y-6">
          {/* Upload Section */}
          <div className="card">
            <h2 className="text-lg font-semibold mb-4">Upload Repository</h2>
            
            <div className="space-y-4">
              <div 
                className="border-2 border-dashed border-dark-600 rounded-lg p-8 text-center cursor-pointer hover:border-dark-500 transition-colors"
                onClick={() => fileInputRef.current?.click()}
              >
                <Upload className="w-12 h-12 text-dark-400 mx-auto mb-3" />
                <p className="text-dark-300 mb-2">
                  {uploadedFile ? uploadedFile.name : 'Drag & drop ZIP file here'}
                </p>
                <p className="text-dark-400 text-sm">or click to browse</p>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".zip"
                  onChange={handleFileUpload}
                  className="hidden"
                />
              </div>

              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-dark-700"></div>
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-2 bg-dark-800 text-dark-400">OR</span>
                </div>
              </div>

              {/* GitHub URL Input */}
              <div>
                <label className="block text-sm font-medium mb-2">GitHub Repository URL</label>
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={repoUrl}
                    onChange={(e) => setRepoUrl(e.target.value)}
                    placeholder="https://github.com/username/repo"
                    className="flex-1 bg-dark-700 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <button
                    onClick={analyzeGithub}
                    disabled={analyzing}
                    className="btn-primary flex items-center"
                  >
                    <GitHubIcon />
                    {analyzing ? 'Analyzing...' : 'Analyze'}
                  </button>
                </div>
                <p className="text-xs text-dark-400 mt-1">
                  Example: https://github.com/facebook/react
                </p>
              </div>
            </div>
          </div>

          {/* Error Display */}
          {error && (
            <div className="card bg-red-500/10 border-red-500/20">
              <div className="flex items-center">
                <AlertCircle className="w-5 h-5 text-red-400 mr-2" />
                <p className="text-red-400 text-sm">{error}</p>
              </div>
            </div>
          )}

          {/* Loading State */}
          {analyzing && (
            <div className="card text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-3"></div>
              <p className="text-dark-300">Analyzing repository structure...</p>
            </div>
          )}
        </div>

        {/* Right Panel - Results */}
        <div className="card">
          <h2 className="text-lg font-semibold mb-4">Analysis Results</h2>
          
          {!currentAnalysis && !analyzing && (
            <div className="text-center text-dark-400 py-8">
              <FolderTree className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>Upload a repository or enter a GitHub URL to begin analysis</p>
            </div>
          )}
          
          {currentAnalysis && !analyzing && (
            <div className="space-y-4 max-h-[600px] overflow-y-auto pr-2">
              {/* Repository Info */}
              <div>
                <h3 className="text-sm font-medium text-dark-300 mb-2">Repository Info</h3>
                <div className="bg-dark-700 rounded-lg p-3">
                  <p className="font-semibold text-lg">{currentAnalysis.name}</p>
                  <div className="flex flex-wrap gap-3 mt-2 text-sm">
                    <span className="text-dark-300">📄 {currentAnalysis.files_count} files</span>
                    <span className="text-dark-300">📝 {currentAnalysis.total_lines?.toLocaleString() || 0} lines</span>
                  </div>
                </div>
              </div>
              
              {/* GitHub Stats */}
              {currentAnalysis.github_info && (
                <div>
                  <h3 className="text-sm font-medium text-dark-300 mb-2">GitHub Stats</h3>
                  <div className="grid grid-cols-2 gap-2">
                    <div className="bg-dark-700 rounded-lg p-2 text-center">
                      <Star className="w-4 h-4 text-yellow-400 mx-auto mb-1" />
                      <p className="text-lg font-bold text-yellow-400">{currentAnalysis.github_info.stars?.toLocaleString() || 0}</p>
                      <p className="text-xs text-dark-400">Stars</p>
                    </div>
                    <div className="bg-dark-700 rounded-lg p-2 text-center">
                      <GitFork className="w-4 h-4 text-green-400 mx-auto mb-1" />
                      <p className="text-lg font-bold text-green-400">{currentAnalysis.github_info.forks?.toLocaleString() || 0}</p>
                      <p className="text-xs text-dark-400">Forks</p>
                    </div>
                    <div className="bg-dark-700 rounded-lg p-2 text-center">
                      <Eye className="w-4 h-4 text-blue-400 mx-auto mb-1" />
                      <p className="text-lg font-bold text-blue-400">{currentAnalysis.github_info.watchers?.toLocaleString() || 0}</p>
                      <p className="text-xs text-dark-400">Watchers</p>
                    </div>
                    <div className="bg-dark-700 rounded-lg p-2 text-center">
                      <AlertOctagon className="w-4 h-4 text-red-400 mx-auto mb-1" />
                      <p className="text-lg font-bold text-red-400">{currentAnalysis.github_info.open_issues?.toLocaleString() || 0}</p>
                      <p className="text-xs text-dark-400">Issues</p>
                    </div>
                  </div>
                  {currentAnalysis.github_info.description && (
                    <p className="mt-2 text-sm text-dark-300 line-clamp-2">
                      {currentAnalysis.github_info.description}
                    </p>
                  )}
                  {currentAnalysis.github_info.language && (
                    <div className="mt-2 flex items-center">
                      <span className="text-xs text-dark-400">Main Language:</span>
                      <span className="ml-2 text-xs px-2 py-0.5 bg-dark-600 rounded">{currentAnalysis.github_info.language}</span>
                    </div>
                  )}
                </div>
              )}
              
              {/* Complexity Score */}
              <div>
                <h3 className="text-sm font-medium text-dark-300 mb-2">Complexity Score</h3>
                <div className="bg-dark-700 rounded-lg p-3">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-2xl font-bold">{currentAnalysis.complexity_score}/10</span>
                    <BarChart3 className="w-5 h-5 text-blue-400" />
                  </div>
                  <div className="bg-dark-600 rounded-full h-2">
                    <div 
                      className={`rounded-full h-2 transition-all ${
                        currentAnalysis.complexity_score <= 3 ? 'bg-green-500' :
                        currentAnalysis.complexity_score <= 6 ? 'bg-yellow-500' : 'bg-red-500'
                      }`}
                      style={{ width: `${(currentAnalysis.complexity_score / 10) * 100}%` }}
                    />
                  </div>
                  <p className="text-xs text-dark-400 mt-2">
                    {currentAnalysis.complexity_score <= 3 ? 'Low complexity - Well structured' :
                     currentAnalysis.complexity_score <= 6 ? 'Moderate complexity - Monitor closely' :
                     'High complexity - Needs refactoring'}
                  </p>
                </div>
              </div>
              
              {/* Languages */}
              {currentAnalysis.languages && Object.keys(currentAnalysis.languages).length > 0 && (
                <div>
                  <h3 className="text-sm font-medium text-dark-300 mb-2">Languages</h3>
                  <div className="flex flex-wrap gap-2">
                    {Object.entries(currentAnalysis.languages).map(([lang, count]) => (
                      <span key={lang} className="px-2 py-1 bg-dark-700 rounded-md text-sm">
                        {lang}: {count} files
                      </span>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Technologies */}
              {currentAnalysis.technologies && currentAnalysis.technologies.length > 0 && (
                <div>
                  <h3 className="text-sm font-medium text-dark-300 mb-2">Technologies</h3>
                  <div className="flex flex-wrap gap-2">
                    {currentAnalysis.technologies.map((tech) => (
                      <span key={tech} className="px-2 py-1 bg-blue-900/30 text-blue-300 rounded-md text-sm">
                        {tech}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Folder Structure */}
              {currentAnalysis.structure && (
                <div>
                  <h3 className="text-sm font-medium text-dark-300 mb-2">Folder Structure</h3>
                  <div className="bg-dark-700 rounded-lg p-3 max-h-64 overflow-y-auto">
                    <FileTree structure={currentAnalysis.structure} />
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}