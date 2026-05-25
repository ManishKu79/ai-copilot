import { useState } from 'react'
import MonacoEditor from '@monaco-editor/react'
import { AlertCircle, AlertTriangle, Info, Copy, Check } from 'lucide-react'
import { reviewAPI } from '../services/api'

export default function CodeReview() {
  const [code, setCode] = useState(`# Paste your code here for review
# Example:

def calculate_average(numbers):
    total = 0
    for num in numbers:
        total += num
    return total / len(numbers)

def process_user_data(user_data):
    # TODO: Add validation
    password = "hardcoded123"  # This is bad practice
    print(f"Processing user: {user_data['name']}")
    
    if user_data['age'] > 18:
        if user_data['verified'] == True:
            if user_data['active'] is True:
                return "User is active"
    return "User is not active"`)
  
  const [reviewResult, setReviewResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [selectedLanguage, setSelectedLanguage] = useState('python')
  const [copied, setCopied] = useState(false)

  const handleReview = async () => {
    setLoading(true)
    try {
      const result = await reviewAPI.reviewCode(code, selectedLanguage)
      setReviewResult(result)
    } catch (error) {
      console.error('Review failed:', error)
      alert('Failed to review code. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleCopyCode = () => {
    navigator.clipboard.writeText(code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const getSeverityIcon = (severity) => {
    switch(severity) {
      case 'error': return <AlertCircle className="w-4 h-4 text-red-400" />
      case 'warning': return <AlertTriangle className="w-4 h-4 text-yellow-400" />
      default: return <Info className="w-4 h-4 text-blue-400" />
    }
  }

  const getSeverityColor = (severity) => {
    switch(severity) {
      case 'error': return 'border-red-500/20 bg-red-500/10'
      case 'warning': return 'border-yellow-500/20 bg-yellow-500/10'
      default: return 'border-blue-500/20 bg-blue-500/10'
    }
  }

  const getQualityColor = (score) => {
    if (score >= 80) return 'text-green-400'
    if (score >= 60) return 'text-yellow-400'
    return 'text-red-400'
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-semibold">Code Review</h1>
        <div className="flex space-x-3">
          <select
            value={selectedLanguage}
            onChange={(e) => setSelectedLanguage(e.target.value)}
            className="bg-dark-700 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="python">Python</option>
            <option value="javascript">JavaScript</option>
            <option value="typescript">TypeScript</option>
          </select>
          <button
            onClick={handleReview}
            disabled={loading}
            className="btn-primary"
          >
            {loading ? 'Reviewing...' : 'Review Code'}
          </button>
        </div>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Code Editor Section */}
        <div className="card p-0 overflow-hidden">
          <div className="bg-dark-700 px-4 py-2 border-b border-dark-600 flex justify-between items-center">
            <h2 className="text-sm font-medium">Code Editor</h2>
            <button
              onClick={handleCopyCode}
              className="text-dark-300 hover:text-dark-100 transition-colors"
              title="Copy code"
            >
              {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
            </button>
          </div>
          <MonacoEditor
            height="600px"
            language={selectedLanguage}
            value={code}
            onChange={(value) => setCode(value || '')}
            theme="vs-dark"
            options={{
              minimap: { enabled: false },
              fontSize: 14,
              lineNumbers: 'on',
              automaticLayout: true,
            }}
          />
        </div>

        {/* Review Results Section */}
        <div className="card">
          <h2 className="text-lg font-semibold mb-4">Review Suggestions</h2>
          
          {!reviewResult && !loading && (
            <div className="text-center text-dark-400 py-8">
              Click "Review Code" to get AI-powered suggestions
            </div>
          )}
          
          {loading && (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-4"></div>
              <p className="text-dark-300">Analyzing code...</p>
            </div>
          )}
          
          {reviewResult && !loading && (
            <div className="space-y-4">
              {/* Quality Score */}
              <div className="bg-dark-700 rounded-lg p-4">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm text-dark-300">Code Quality Score</span>
                  <span className={`text-2xl font-bold ${getQualityColor(reviewResult.quality_score)}`}>
                    {reviewResult.quality_score}/100
                  </span>
                </div>
                <div className="bg-dark-600 rounded-full h-2">
                  <div 
                    className={`rounded-full h-2 transition-all ${
                      reviewResult.quality_score >= 80 ? 'bg-green-500' :
                      reviewResult.quality_score >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                    }`}
                    style={{ width: `${reviewResult.quality_score}%` }}
                  />
                </div>
              </div>
              
              {/* Severity Breakdown */}
              <div className="grid grid-cols-3 gap-3">
                <div className="text-center p-3 bg-red-500/10 rounded-lg">
                  <div className="text-red-400 text-xl font-bold">{reviewResult.severity_breakdown.error}</div>
                  <div className="text-xs text-dark-300">Errors</div>
                </div>
                <div className="text-center p-3 bg-yellow-500/10 rounded-lg">
                  <div className="text-yellow-400 text-xl font-bold">{reviewResult.severity_breakdown.warning}</div>
                  <div className="text-xs text-dark-300">Warnings</div>
                </div>
                <div className="text-center p-3 bg-blue-500/10 rounded-lg">
                  <div className="text-blue-400 text-xl font-bold">{reviewResult.severity_breakdown.info}</div>
                  <div className="text-xs text-dark-300">Info</div>
                </div>
              </div>
              
              {/* Issues List */}
              <div className="space-y-3 max-h-96 overflow-y-auto">
                <h3 className="text-sm font-medium text-dark-300">Issues Found ({reviewResult.total_issues})</h3>
                {reviewResult.issues.length === 0 ? (
                  <div className="text-center text-green-400 py-4">
                    ✅ No issues found! Great code!
                  </div>
                ) : (
                  reviewResult.issues.map((issue, index) => (
                    <div 
                      key={index}
                      className={`border rounded-lg p-3 ${getSeverityColor(issue.severity)}`}
                    >
                      <div className="flex items-start space-x-2">
                        {getSeverityIcon(issue.severity)}
                        <div className="flex-1">
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-sm font-medium">
                              Line {issue.line || 'N/A'}: {issue.category?.replace(/_/g, ' ').toUpperCase() || 'ISSUE'}
                            </span>
                            <span className="text-xs px-2 py-0.5 rounded bg-dark-700">
                              {issue.severity}
                            </span>
                          </div>
                          <p className="text-sm mb-2">{issue.message}</p>
                          {issue.suggestion && (
                            <div className="text-xs text-blue-400 mt-1">
                              💡 {issue.suggestion}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}