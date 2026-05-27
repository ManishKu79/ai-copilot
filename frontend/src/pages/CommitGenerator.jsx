import { useState } from 'react'
import {
  GitBranch,
  Send,
  Copy,
  Check,
  Sparkles,
  Code,
  FileText,
  AlertCircle,
  ChevronDown
} from 'lucide-react'
import { commitAPI } from '../services/api'

export default function CommitGenerator() {
  const [diff, setDiff] = useState('')
  const [description, setDescription] = useState('')
  const [commitType, setCommitType] = useState('feat')
  const [scope, setScope] = useState('')
  const [generatedMessage, setGeneratedMessage] = useState(null)
  const [loading, setLoading] = useState(false)
  const [copied, setCopied] = useState(false)
  const [activeMethod, setActiveMethod] = useState('diff')

  const commitTypes = [
    { value: 'feat', label: '✨ feat', description: 'New feature' },
    { value: 'fix', label: '🐛 fix', description: 'Bug fix' },
    { value: 'docs', label: '📝 docs', description: 'Documentation' },
    { value: 'style', label: '💄 style', description: 'Code style' },
    { value: 'refactor', label: '♻️ refactor', description: 'Code refactoring' },
    { value: 'perf', label: '⚡ perf', description: 'Performance' },
    { value: 'test', label: '✅ test', description: 'Testing' },
    { value: 'chore', label: '🔧 chore', description: 'Maintenance' },
    { value: 'ci', label: '👷 ci', description: 'CI/CD' },
    { value: 'auth', label: '🔐 auth', description: 'Authentication' },
    { value: 'security', label: '🔒 security', description: 'Security fixes' }
  ]

  const handleGenerateFromDiff = async () => {
    if (!diff.trim()) {
      alert('Please paste your git diff')
      return
    }

    setLoading(true)
    try {
      const result = await commitAPI.generateCommitMessage(diff)
      setGeneratedMessage(result)
    } catch (error) {
      console.error('Generation failed:', error)
      alert('Failed to generate commit message')
    } finally {
      setLoading(false)
    }
  }

  const handleGenerateFromDescription = async () => {
    if (!description.trim()) {
      alert('Please enter a description')
      return
    }

    setLoading(true)
    try {
      let result
      if (scope.trim()) {
        result = await commitAPI.generateCommitWithScope(description, commitType, scope)
      } else {
        result = await commitAPI.generateConventionalCommit(description, commitType)
      }
      setGeneratedMessage(result)
    } catch (error) {
      console.error('Generation failed:', error)
      alert('Failed to generate commit message')
    } finally {
      setLoading(false)
    }
  }

  const handleCopy = () => {
    if (generatedMessage) {
      const text = generatedMessage.full_message
      navigator.clipboard.writeText(text)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const handleCopyFormat = () => {
    if (generatedMessage) {
      navigator.clipboard.writeText(generatedMessage.conventional_format)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const exampleDiff = `diff --git a/src/auth/login.py b/src/auth/login.py
index abc123..def456 100644
--- a/src/auth/login.py
+++ b/src/auth/login.py
@@ -10,6 +10,10 @@ def authenticate_user(username, password):
     if not username or not password:
         return False
     
+    # Add rate limiting
+    if check_rate_limit(username):
+        return False
+    
     user = User.query.filter_by(username=username).first()
     if user and user.check_password(password):
         return True

diff --git a/src/ui/LoginComponent.js b/src/ui/LoginComponent.js
index xyz789..uvw456 100644
--- a/src/ui/LoginComponent.js
+++ b/src/ui/LoginComponent.js
@@ -25,6 +25,12 @@ function LoginComponent() {
       setError('Please enter credentials');
       return;
     }
+    
+    // Add loading state
+    setLoading(true);
+    const result = await api.login(credentials);
+    setLoading(false);
+    
     if (response.success) {
       navigate('/dashboard');
     }`

  return (
    <div>
      <h1 className="text-2xl font-semibold mb-6">AI Commit Message Generator</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input Panel */}
        <div className="card">
          <div className="flex items-center space-x-4 mb-4">
            <button
              onClick={() => setActiveMethod('diff')}
              className={`flex-1 py-2 rounded-md transition-colors ${
                activeMethod === 'diff' 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-dark-700 text-dark-300 hover:text-dark-100'
              }`}
            >
              <Code className="w-4 h-4 inline mr-2" />
              From Git Diff
            </button>
            <button
              onClick={() => setActiveMethod('description')}
              className={`flex-1 py-2 rounded-md transition-colors ${
                activeMethod === 'description' 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-dark-700 text-dark-300 hover:text-dark-100'
              }`}
            >
              <FileText className="w-4 h-4 inline mr-2" />
              From Description
            </button>
          </div>

          {activeMethod === 'diff' ? (
            <>
              <div className="mb-3">
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
                onClick={handleGenerateFromDiff}
                disabled={loading}
                className="btn-primary w-full flex items-center justify-center"
              >
                {loading ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                ) : (
                  <Sparkles className="w-4 h-4 mr-2" />
                )}
                Generate Commit Message
              </button>
              <div className="mt-3">
                <button
                  onClick={() => setDiff(exampleDiff)}
                  className="text-sm text-blue-400 hover:text-blue-300"
                >
                  Load Example Diff
                </button>
              </div>
            </>
          ) : (
            <>
              <div className="mb-3">
                <label className="block text-sm font-medium mb-2">Commit Type</label>
                <select
                  value={commitType}
                  onChange={(e) => setCommitType(e.target.value)}
                  className="w-full bg-dark-700 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {commitTypes.map(type => (
                    <option key={type.value} value={type.value}>
                      {type.label} - {type.description}
                    </option>
                  ))}
                </select>
              </div>
              <div className="mb-3">
                <label className="block text-sm font-medium mb-2">Scope (optional)</label>
                <input
                  type="text"
                  value={scope}
                  onChange={(e) => setScope(e.target.value)}
                  placeholder="e.g., auth, api, ui, db"
                  className="w-full bg-dark-700 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div className="mb-3">
                <label className="block text-sm font-medium mb-2">Description</label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Describe your changes..."
                  rows={6}
                  className="w-full bg-dark-700 rounded-md p-3 font-mono text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                />
              </div>
              <button
                onClick={handleGenerateFromDescription}
                disabled={loading}
                className="btn-primary w-full flex items-center justify-center"
              >
                {loading ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                ) : (
                  <Sparkles className="w-4 h-4 mr-2" />
                )}
                Generate Commit Message
              </button>
            </>
          )}
        </div>

        {/* Output Panel */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Generated Commit Message</h2>
            {generatedMessage && (
              <div className="flex space-x-2">
                <button
                  onClick={handleCopyFormat}
                  className="btn-secondary flex items-center text-sm"
                >
                  <Copy className="w-4 h-4 mr-1" />
                  Format
                </button>
                <button
                  onClick={handleCopy}
                  className="btn-primary flex items-center text-sm"
                >
                  {copied ? <Check className="w-4 h-4 mr-1" /> : <Copy className="w-4 h-4 mr-1" />}
                  Copy All
                </button>
              </div>
            )}
          </div>

          {!generatedMessage && !loading && (
            <div className="text-center text-dark-400 py-12">
              <GitBranch className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>Enter your changes above to generate a commit message</p>
              <p className="text-sm mt-2">AI will analyze and create a conventional commit</p>
            </div>
          )}

          {loading && (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-4"></div>
              <p className="text-dark-300">Analyzing changes...</p>
            </div>
          )}

          {generatedMessage && !loading && (
            <div className="space-y-4">
              {/* Preview */}
              <pre className="bg-dark-900 rounded-lg p-4 overflow-x-auto text-sm font-mono whitespace-pre-wrap">
                {generatedMessage.full_message}
              </pre>

              {/* Changes Summary */}
              {generatedMessage.changes_summary && (
                <div className="border-t border-dark-700 pt-3 mt-2">
                  <p className="text-xs text-dark-400 mb-2">Changes Analyzed</p>
                  <div className="flex space-x-4 text-sm">
                    <span className="text-green-400">+{generatedMessage.changes_summary.additions}</span>
                    <span className="text-red-400">-{generatedMessage.changes_summary.deletions}</span>
                    {generatedMessage.changes_summary.impact && (
                      <span className={`${
                        generatedMessage.changes_summary.impact === 'HIGH' ? 'text-red-400' :
                        generatedMessage.changes_summary.impact === 'MEDIUM' ? 'text-yellow-400' :
                        'text-green-400'
                      }`}>
                        {generatedMessage.changes_summary.impact} IMPACT
                      </span>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Info Section */}
      <div className="mt-6 card bg-dark-800/50">
        <div className="flex items-start">
          <AlertCircle className="w-5 h-5 text-blue-400 mr-3 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="text-sm font-medium mb-1">About Conventional Commits</h3>
            <p className="text-xs text-dark-300">
              Conventional Commits provide a lightweight convention for commit messages. 
              Format: <code className="text-green-400">&lt;type&gt;(&lt;scope&gt;): &lt;description&gt;</code>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}