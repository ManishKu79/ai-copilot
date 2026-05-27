import { useState, useEffect } from 'react'
import {
  Scissors,
  AlertTriangle,
  TrendingUp,
  Clock,
  FileCode,
  ChevronRight,
  Code,
  Copy,
  Check,
  Zap
} from 'lucide-react'
import useAppStore from '../store/useAppStore'
import { refactorAPI } from '../services/api'

export default function RefactorSuggestions() {
  const { currentAnalysis } = useAppStore()
  const [analysis, setAnalysis] = useState(null)
  const [loading, setLoading] = useState(false)
  const [selectedSuggestion, setSelectedSuggestion] = useState(null)
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    if (currentAnalysis && currentAnalysis.files_preview) {
      analyzeRepository()
    }
  }, [currentAnalysis])

  const analyzeRepository = async () => {
    setLoading(true)
    try {
      const files = currentAnalysis.files_preview || []
      console.log('Analyzing files for refactoring:', files.length)
      const result = await refactorAPI.analyzeRepository(files)
      if (result.success) {
        setAnalysis(result.analysis)
      }
    } catch (error) {
      console.error('Refactor analysis failed:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCopyExample = (example) => {
    if (example) {
      navigator.clipboard.writeText(example)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const getSeverityColor = (severity) => {
    switch(severity) {
      case 'high': return 'border-red-500/20 bg-red-500/10'
      case 'medium': return 'border-yellow-500/20 bg-yellow-500/10'
      case 'low': return 'border-blue-500/20 bg-blue-500/10'
      default: return 'border-gray-500/20 bg-gray-500/10'
    }
  }

  const getSeverityBadge = (severity) => {
    switch(severity) {
      case 'high': return 'bg-red-500/20 text-red-400'
      case 'medium': return 'bg-yellow-500/20 text-yellow-400'
      case 'low': return 'bg-blue-500/20 text-blue-400'
      default: return 'bg-gray-500/20 text-gray-400'
    }
  }

  if (!currentAnalysis) {
    return (
      <div>
        <h1 className="text-2xl font-semibold mb-6">Refactor Suggestions</h1>
        <div className="card text-center py-12">
          <Scissors className="w-16 h-16 text-dark-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium mb-2">No Repository Analyzed</h3>
          <p className="text-dark-300">
            First analyze a repository to get refactoring suggestions
          </p>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div>
        <h1 className="text-2xl font-semibold mb-6">Refactor Suggestions</h1>
        <div className="card text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-dark-300">Analyzing code for refactoring opportunities...</p>
        </div>
      </div>
    )
  }

  return (
    <div>
      <h1 className="text-2xl font-semibold mb-6">Refactor Suggestions</h1>
      
      {analysis && (
        <div className="space-y-6">
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <div className="card bg-dark-800/50">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-dark-300 text-sm">Total Suggestions</p>
                  <p className="text-2xl font-bold">{analysis.total_suggestions}</p>
                </div>
                <Scissors className="w-8 h-8 text-purple-400" />
              </div>
            </div>
            <div className="card bg-dark-800/50">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-dark-300 text-sm">High Severity</p>
                  <p className="text-2xl font-bold text-red-400">{analysis.high_severity}</p>
                </div>
                <AlertTriangle className="w-8 h-8 text-red-400" />
              </div>
            </div>
            <div className="card bg-dark-800/50">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-dark-300 text-sm">Medium Severity</p>
                  <p className="text-2xl font-bold text-yellow-400">{analysis.medium_severity}</p>
                </div>
                <AlertTriangle className="w-8 h-8 text-yellow-400" />
              </div>
            </div>
            <div className="card bg-dark-800/50">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-dark-300 text-sm">Effort Estimate</p>
                  <p className="text-2xl font-bold">{analysis.estimated_effort_hours}h</p>
                </div>
                <Clock className="w-8 h-8 text-blue-400" />
              </div>
            </div>
            <div className="card bg-dark-800/50">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-dark-300 text-sm">Priority</p>
                  <p className={`text-2xl font-bold capitalize ${
                    analysis.refactoring_priority === 'high' ? 'text-red-400' :
                    analysis.refactoring_priority === 'medium' ? 'text-yellow-400' :
                    'text-green-400'
                  }`}>
                    {analysis.refactoring_priority}
                  </p>
                </div>
                <TrendingUp className="w-8 h-8 text-orange-400" />
              </div>
            </div>
          </div>

          {/* Category Breakdown */}
          {analysis.categories && Object.keys(analysis.categories).length > 0 && (
            <div className="card">
              <h3 className="text-lg font-semibold mb-4">Issues by Category</h3>
              <div className="flex flex-wrap gap-3">
                {Object.entries(analysis.categories).map(([category, count]) => (
                  <div key={category} className="flex items-center space-x-2 px-3 py-2 bg-dark-700 rounded-lg">
                    <span className="capitalize text-sm">{category}</span>
                    <span className="text-xs px-2 py-0.5 bg-blue-500/20 text-blue-400 rounded-full">
                      {count}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Suggestions List */}
          <div className="card">
            <h3 className="text-lg font-semibold mb-4">Refactoring Suggestions</h3>
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {analysis.suggestions.length === 0 ? (
                <div className="text-center text-green-400 py-8">
                  <svg className="w-12 h-12 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <p>Great job! No refactoring suggestions found.</p>
                </div>
              ) : (
                analysis.suggestions.map((suggestion, idx) => (
                  <div
                    key={idx}
                    className={`border rounded-lg p-4 cursor-pointer transition-all ${getSeverityColor(suggestion.severity)}`}
                    onClick={() => setSelectedSuggestion(selectedSuggestion === idx ? null : idx)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center mb-2 flex-wrap gap-2">
                          <FileCode className="w-4 h-4 text-dark-300" />
                          <span className="text-xs font-mono text-dark-300">{suggestion.file_name}</span>
                          <span className="text-xs text-dark-400">Line {suggestion.line}</span>
                          <span className={`text-xs px-2 py-0.5 rounded ${getSeverityBadge(suggestion.severity)}`}>
                            {suggestion.severity}
                          </span>
                        </div>
                        <h4 className="font-medium mb-1">{suggestion.title}</h4>
                        <p className="text-sm text-dark-300">{suggestion.message}</p>
                        <p className="text-sm text-blue-400 mt-2">💡 {suggestion.suggestion}</p>
                      </div>
                      <ChevronRight className={`w-4 h-4 text-dark-400 transition-transform flex-shrink-0 ${selectedSuggestion === idx ? 'rotate-90' : ''}`} />
                    </div>

                    {selectedSuggestion === idx && suggestion.code_example && (
                      <div className="mt-4 pt-4 border-t border-dark-600">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center">
                            <Code className="w-4 h-4 text-green-400 mr-2" />
                            <span className="text-sm font-medium">Suggested Fix</span>
                          </div>
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              handleCopyExample(suggestion.code_example)
                            }}
                            className="text-dark-300 hover:text-dark-100"
                          >
                            {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                          </button>
                        </div>
                        <pre className="bg-dark-900 rounded p-3 overflow-x-auto text-sm font-mono whitespace-pre-wrap">
                          <code>{suggestion.code_example}</code>
                        </pre>
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Action Plan */}
          {analysis.total_suggestions > 0 && (
            <div className="card bg-gradient-to-r from-blue-500/10 to-purple-500/10">
              <div className="flex items-start">
                <Zap className="w-6 h-6 text-yellow-400 mr-3 flex-shrink-0 mt-1" />
                <div>
                  <h3 className="text-lg font-semibold mb-2">Suggested Action Plan</h3>
                  <div className="space-y-2 text-sm text-dark-300">
                    <p>1. <span className="text-red-400">High severity issues</span> should be addressed first ({analysis.high_severity} found)</p>
                    <p>2. Focus on files with multiple suggestions to maximize impact</p>
                    <p>3. Estimated total effort: <span className="font-semibold">{analysis.estimated_effort_hours} hours</span></p>
                    <p>4. Start with function extraction and complexity reduction</p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}