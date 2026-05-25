import { useState } from 'react'
import { 
  AlertCircle, 
  Lightbulb, 
  BookOpen, 
  Copy, 
  Check,
  ChevronDown,
  ChevronRight,
  FileText,
  Terminal
} from 'lucide-react'
import { errorAPI } from '../services/api'

export default function ErrorExplainer() {
  const [errorInput, setErrorInput] = useState('')
  const [explanation, setExplanation] = useState(null)
  const [loading, setLoading] = useState(false)
  const [copied, setCopied] = useState(false)
  const [expandedSections, setExpandedSections] = useState({
    causes: true,
    fixes: true,
    example: false,
    docs: true
  })

  const handleExplain = async () => {
    if (!errorInput.trim()) {
      alert('Please paste an error message')
      return
    }

    setLoading(true)
    try {
      const result = await errorAPI.explainError(errorInput)
      if (result.success) {
        setExplanation(result.explanation)
      }
    } catch (error) {
      console.error('Error explanation failed:', error)
      alert('Failed to explain error. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleCopyError = () => {
    navigator.clipboard.writeText(errorInput)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }))
  }

  const getCategoryColor = (category) => {
    const colors = {
      'syntax_error': 'text-purple-400 border-purple-500',
      'runtime_error': 'text-red-400 border-red-500',
      'import_error': 'text-yellow-400 border-yellow-500',
      'type_error': 'text-orange-400 border-orange-500',
      'value_error': 'text-pink-400 border-pink-500',
      'attribute_error': 'text-indigo-400 border-indigo-500'
    }
    return colors[category] || 'text-blue-400 border-blue-500'
  }

  const getCategoryIcon = (category) => {
    const icons = {
      'syntax_error': '🔧',
      'runtime_error': '🚨',
      'import_error': '📦',
      'type_error': '🔤',
      'value_error': '📊',
      'attribute_error': '🏷️'
    }
    return icons[category] || '⚠️'
  }

  return (
    <div>
      <h1 className="text-2xl font-semibold mb-6">AI Error Explainer</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Error Input Section */}
        <div className="card">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold">Error Message</h2>
            <button
              onClick={handleCopyError}
              className="text-dark-300 hover:text-dark-100 transition-colors"
              title="Copy error"
            >
              {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
            </button>
          </div>
          
          <textarea
            value={errorInput}
            onChange={(e) => setErrorInput(e.target.value)}
            placeholder={`Paste your error message or stack trace here...

Examples:
- "SyntaxError: invalid syntax at line 5"
- "ModuleNotFoundError: No module named 'requests'"
- "TypeError: can only concatenate str (not 'int') to str"
- React error: "Cannot read property 'map' of undefined"`}
            rows={12}
            className="w-full bg-dark-700 rounded-md p-3 font-mono text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
          />
          
          <button
            onClick={handleExplain}
            disabled={loading}
            className="mt-4 btn-primary w-full flex items-center justify-center"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Analyzing Error...
              </>
            ) : (
              <>
                <AlertCircle className="w-4 h-4 mr-2" />
                Explain Error
              </>
            )}
          </button>
          
          <div className="mt-4 p-3 bg-dark-700 rounded-md">
            <div className="flex items-center text-xs text-dark-300">
              <Terminal className="w-3 h-3 mr-1" />
              <span>Pro tip: Include the full stack trace for better explanations</span>
            </div>
          </div>
        </div>

        {/* Explanation Section */}
        <div className="card overflow-y-auto max-h-[calc(100vh-200px)]">
          <h2 className="text-lg font-semibold mb-4">Explanation</h2>
          
          {!explanation && !loading && (
            <div className="text-center text-dark-400 py-12">
              <AlertCircle className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>Paste an error message to get an intelligent explanation</p>
              <p className="text-sm mt-2">Get fixes, examples, and best practices</p>
            </div>
          )}
          
          {loading && (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-4"></div>
              <p className="text-dark-300">Parsing error and generating explanation...</p>
            </div>
          )}
          
          {explanation && !loading && (
            <div className="space-y-4">
              {/* Error Type Badge */}
              <div className={`border-l-4 ${getCategoryColor(explanation.category)} bg-dark-700 p-3 rounded`}>
                <div className="flex items-center">
                  <span className="text-2xl mr-2">{getCategoryIcon(explanation.category)}</span>
                  <div>
                    <div className="text-xs text-dark-300">Error Type</div>
                    <div className="font-mono text-sm">{explanation.error_type}</div>
                  </div>
                </div>
              </div>
              
              {/* Explanation */}
              <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
                <div className="flex items-start">
                  <FileText className="w-4 h-4 text-blue-400 mr-2 mt-0.5" />
                  <p className="text-sm leading-relaxed">{explanation.explanation}</p>
                </div>
              </div>
              
              {/* Probable Causes */}
              <div className="border border-dark-700 rounded-lg overflow-hidden">
                <button
                  onClick={() => toggleSection('causes')}
                  className="w-full flex items-center justify-between p-3 bg-dark-800 hover:bg-dark-700 transition-colors"
                >
                  <div className="flex items-center">
                    <AlertCircle className="w-4 h-4 text-yellow-400 mr-2" />
                    <span className="font-medium">Probable Causes</span>
                  </div>
                  {expandedSections.causes ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                </button>
                {expandedSections.causes && (
                  <div className="p-3 space-y-2">
                    {explanation.probable_causes.map((cause, idx) => (
                      <div key={idx} className="flex items-start text-sm">
                        <span className="text-red-400 mr-2">•</span>
                        <span className="text-dark-200">{cause}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
              
              {/* Fix Suggestions */}
              <div className="border border-dark-700 rounded-lg overflow-hidden">
                <button
                  onClick={() => toggleSection('fixes')}
                  className="w-full flex items-center justify-between p-3 bg-dark-800 hover:bg-dark-700 transition-colors"
                >
                  <div className="flex items-center">
                    <Lightbulb className="w-4 h-4 text-green-400 mr-2" />
                    <span className="font-medium">How to Fix</span>
                  </div>
                  {expandedSections.fixes ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                </button>
                {expandedSections.fixes && (
                  <div className="p-3 space-y-3">
                    {explanation.fix_suggestions.map((fix, idx) => (
                      <div key={idx} className="flex items-start">
                        <span className="text-green-400 mr-2">→</span>
                        <span className="text-sm text-dark-200">{fix}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
              
              {/* Code Example */}
              {explanation.code_example && (
                <div className="border border-dark-700 rounded-lg overflow-hidden">
                  <button
                    onClick={() => toggleSection('example')}
                    className="w-full flex items-center justify-between p-3 bg-dark-800 hover:bg-dark-700 transition-colors"
                  >
                    <div className="flex items-center">
                      <span className="text-xl mr-2">💻</span>
                      <span className="font-medium">Code Example</span>
                    </div>
                    {expandedSections.example ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                  </button>
                  {expandedSections.example && (
                    <div className="p-3">
                      <pre className="bg-dark-900 rounded p-3 overflow-x-auto text-sm">
                        <code>{explanation.code_example}</code>
                      </pre>
                    </div>
                  )}
                </div>
              )}
              
              {/* Stack Trace Analysis */}
              {explanation.stack_trace_analysis && (
                <div className="border border-dark-700 rounded-lg p-3">
                  <div className="flex items-center mb-2">
                    <Terminal className="w-4 h-4 text-dark-300 mr-2" />
                    <span className="text-sm font-medium">Stack Trace Analysis</span>
                  </div>
                  <div className="space-y-1 text-sm">
                    {explanation.stack_trace_analysis.frames.map((frame, idx) => (
                      <div key={idx} className="font-mono text-xs text-dark-300">
                        {frame.file}:{frame.line}
                      </div>
                    ))}
                    <div className="mt-2 text-green-400 text-xs">
                      {explanation.stack_trace_analysis.suggestion}
                    </div>
                  </div>
                </div>
              )}
              
              {/* Related Documentation */}
              {explanation.related_docs && explanation.related_docs.length > 0 && (
                <div className="border border-dark-700 rounded-lg overflow-hidden">
                  <button
                    onClick={() => toggleSection('docs')}
                    className="w-full flex items-center justify-between p-3 bg-dark-800 hover:bg-dark-700 transition-colors"
                  >
                    <div className="flex items-center">
                      <BookOpen className="w-4 h-4 text-blue-400 mr-2" />
                      <span className="font-medium">Related Documentation</span>
                    </div>
                    {expandedSections.docs ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                  </button>
                  {expandedSections.docs && (
                    <div className="p-3 space-y-2">
                      {explanation.related_docs.map((doc, idx) => (
                        <a
                          key={idx}
                          href={doc}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center text-sm text-blue-400 hover:text-blue-300 transition-colors"
                        >
                          <BookOpen className="w-3 h-3 mr-2" />
                          {doc}
                        </a>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}