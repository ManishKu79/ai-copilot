import { useState } from 'react'
import {
  GitPullRequest,
  AlertCircle,
  CheckCircle,
  AlertTriangle,
  ThumbsUp,
  ThumbsDown,
  Copy,
  Check,
  FileCode,
  Bug,
  Shield,
  Zap,
  FileText
} from 'lucide-react'
import { prAPI } from '../services/api'

export default function PRReviewAssistant() {
  const [diff, setDiff] = useState('')
  const [prTitle, setPrTitle] = useState('')
  const [prDescription, setPrDescription] = useState('')
  const [review, setReview] = useState(null)
  const [loading, setLoading] = useState(false)
  const [copied, setCopied] = useState(false)

  const handleReview = async () => {
    if (!diff.trim()) {
      alert('Please paste your PR diff')
      return
    }

    setLoading(true)
    try {
      const result = await prAPI.reviewPR(diff, prTitle, prDescription)
      setReview(result)
    } catch (error) {
      console.error('PR review failed:', error)
      alert('Failed to review PR')
    } finally {
      setLoading(false)
    }
  }

  const handleCopySummary = () => {
    if (review) {
      navigator.clipboard.writeText(review.summary)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const getGradeColor = (grade) => {
    const colors = {
      'A': 'text-green-400',
      'B': 'text-blue-400',
      'C': 'text-yellow-400',
      'D': 'text-orange-400',
      'F': 'text-red-400'
    }
    return colors[grade] || 'text-gray-400'
  }

  const getScoreColor = (score) => {
    if (score >= 80) return 'bg-green-500'
    if (score >= 60) return 'bg-yellow-500'
    return 'bg-red-500'
  }

  const exampleDiff = `diff --git a/src/auth/login.py b/src/auth/login.py
index abc123..def456 100644
--- a/src/auth/login.py
+++ b/src/auth/login.py
@@ -10,6 +10,10 @@ def authenticate_user(username, password):
     if not username or not password:
         return False
     
+    # TODO: Add rate limiting
+    password = "hardcoded_secret_123"
+    print(f"Login attempt from {username}")
+    
     user = User.query.filter_by(username=username).first()
     if user and user.check_password(password):
         return True

diff --git a/src/api/users.py b/src/api/users.py
index xyz789..uvw456 100644
--- a/src/api/users.py
+++ b/src/api/users.py
@@ -25,6 +25,12 @@ def get_user_data(user_id):
     if not user_id:
         return None
     
+    query = f"SELECT * FROM users WHERE id = {user_id}"
+    result = execute_query(query)
+    
+    if result:
+        return result[0]
+    
     return None`

  return (
    <div>
      <h1 className="text-2xl font-semibold mb-6">PR Review Assistant</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input Panel */}
        <div className="card">
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">Pull Request Title (optional)</label>
            <input
              type="text"
              value={prTitle}
              onChange={(e) => setPrTitle(e.target.value)}
              placeholder="feat: add authentication feature"
              className="w-full bg-dark-700 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">PR Description (optional)</label>
            <textarea
              value={prDescription}
              onChange={(e) => setPrDescription(e.target.value)}
              placeholder="Describe the changes in this PR..."
              rows={3}
              className="w-full bg-dark-700 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            />
          </div>
          
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">Git Diff</label>
            <textarea
              value={diff}
              onChange={(e) => setDiff(e.target.value)}
              placeholder="Paste your git diff here..."
              rows={12}
              className="w-full bg-dark-700 rounded-md p-3 font-mono text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            />
          </div>
          
          <button
            onClick={handleReview}
            disabled={loading}
            className="btn-primary w-full flex items-center justify-center"
          >
            {loading ? (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
            ) : (
              <GitPullRequest className="w-4 h-4 mr-2" />
            )}
            Review Pull Request
          </button>
          
          <div className="mt-3">
            <button
              onClick={() => setDiff(exampleDiff)}
              className="text-sm text-blue-400 hover:text-blue-300"
            >
              Load Example PR
            </button>
          </div>
        </div>

        {/* Output Panel */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Review Results</h2>
            {review && (
              <button
                onClick={handleCopySummary}
                className="btn-secondary flex items-center text-sm"
              >
                {copied ? <Check className="w-4 h-4 mr-1" /> : <Copy className="w-4 h-4 mr-1" />}
                Copy Summary
              </button>
            )}
          </div>

          {!review && !loading && (
            <div className="text-center text-dark-400 py-12">
              <GitPullRequest className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>Paste your PR diff to get an automated review</p>
              <p className="text-sm mt-2">AI will analyze code quality, security, and best practices</p>
            </div>
          )}

          {loading && (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-4"></div>
              <p className="text-dark-300">Analyzing pull request...</p>
            </div>
          )}

          {review && !loading && (
            <div className="space-y-4 overflow-y-auto" style={{ maxHeight: '600px' }}>
              {/* Score Card */}
              <div className="bg-dark-800 rounded-lg p-4 text-center">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-dark-300">PR Quality Score</span>
                  <span className={`text-2xl font-bold ${getGradeColor(review.grade)}`}>
                    Grade: {review.grade}
                  </span>
                </div>
                <div className="bg-dark-700 rounded-full h-3">
                  <div 
                    className={`${getScoreColor(review.pr_score)} rounded-full h-3 transition-all`}
                    style={{ width: `${review.pr_score}%` }}
                  />
                </div>
                <p className="text-sm text-dark-300 mt-2">{review.pr_score}/100</p>
              </div>

              {/* Assessment */}
              <div className="bg-dark-800 rounded-lg p-4">
                <div className="prose prose-invert prose-sm max-w-none">
                  <div dangerouslySetInnerHTML={{ __html: review.assessment.replace(/\n/g, '<br/>') }} />
                </div>
              </div>

              {/* Statistics */}
              <div className="grid grid-cols-4 gap-2">
                <div className="text-center p-2 bg-dark-800 rounded">
                  <FileCode className="w-4 h-4 mx-auto mb-1 text-blue-400" />
                  <p className="text-lg font-bold">{review.statistics.files_changed}</p>
                  <p className="text-xs text-dark-400">Files</p>
                </div>
                <div className="text-center p-2 bg-dark-800 rounded">
                  <div className="text-green-400 text-lg font-bold">+{review.statistics.additions}</div>
                  <p className="text-xs text-dark-400">Additions</p>
                </div>
                <div className="text-center p-2 bg-dark-800 rounded">
                  <div className="text-red-400 text-lg font-bold">-{review.statistics.deletions}</div>
                  <p className="text-xs text-dark-400">Deletions</p>
                </div>
                <div className="text-center p-2 bg-dark-800 rounded">
                  <AlertCircle className="w-4 h-4 mx-auto mb-1 text-yellow-400" />
                  <p className="text-lg font-bold">{review.statistics.issues_found}</p>
                  <p className="text-xs text-dark-400">Issues</p>
                </div>
              </div>

              {/* Issues by Severity */}
              {review.issues_by_severity.critical?.length > 0 && (
                <div className="border-l-4 border-red-500 bg-red-500/10 p-3 rounded">
                  <h3 className="font-semibold text-red-400 mb-2">🔴 Critical Issues ({review.issues_by_severity.critical.length})</h3>
                  {review.issues_by_severity.critical.map((issue, idx) => (
                    <div key={idx} className="mb-2 text-sm">
                      <p className="text-red-300">{issue.message}</p>
                      <p className="text-dark-300 text-xs mt-1">📍 {issue.file}:{issue.line}</p>
                    </div>
                  ))}
                </div>
              )}

              {review.issues_by_severity.high?.length > 0 && (
                <div className="border-l-4 border-orange-500 bg-orange-500/10 p-3 rounded">
                  <h3 className="font-semibold text-orange-400 mb-2">🟠 High Severity ({review.issues_by_severity.high.length})</h3>
                  {review.issues_by_severity.high.map((issue, idx) => (
                    <div key={idx} className="mb-2 text-sm">
                      <p className="text-orange-300">{issue.message}</p>
                      <p className="text-dark-300 text-xs mt-1">📍 {issue.file}:{issue.line}</p>
                    </div>
                  ))}
                </div>
              )}

              {/* Summary Preview */}
              <div className="border-t border-dark-700 pt-3">
                <h3 className="font-semibold mb-2">📋 Full Review Summary</h3>
                <pre className="bg-dark-900 rounded p-3 text-xs font-mono whitespace-pre-wrap overflow-x-auto">
                  {review.summary}
                </pre>
              </div>

              {/* Recommendations */}
              {review.recommendations.length > 0 && (
                <div className="border-t border-dark-700 pt-3">
                  <h3 className="font-semibold mb-2">💡 Recommendations</h3>
                  {review.recommendations.map((rec, idx) => (
                    <div key={idx} className="mb-2 p-2 bg-dark-800 rounded">
                      <div className="flex items-center">
                        <span className={`text-xs px-2 py-0.5 rounded mr-2 ${
                          rec.priority === 'critical' ? 'bg-red-500/20 text-red-400' :
                          rec.priority === 'high' ? 'bg-orange-500/20 text-orange-400' :
                          'bg-yellow-500/20 text-yellow-400'
                        }`}>
                          {rec.priority.toUpperCase()}
                        </span>
                        <span className="font-medium">{rec.title}</span>
                      </div>
                      <p className="text-sm text-dark-300 mt-1">{rec.action}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Info Section */}
      <div className="mt-6 card bg-dark-800/50">
        <div className="flex items-start">
          <Shield className="w-5 h-5 text-blue-400 mr-3 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="text-sm font-medium mb-1">What the PR Review Checks For</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs text-dark-300">
              <span>🐛 Bug risks</span>
              <span>🔒 Security issues</span>
              <span>⚡ Performance problems</span>
              <span>💄 Code style violations</span>
              <span>📝 Missing documentation</span>
              <span>✅ Test coverage</span>
              <span>🔄 Code complexity</span>
              <span>✨ Best practices</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}