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
    { value: 'security', label: '🔒 security', description: 'Security' }
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
      const result = await commitAPI.generateConventionalCommit(description, commitType)
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
      const text = generatedMessage.full_message || generatedMessage.conventional_format
      navigator.clipboard.writeText(text)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const handleUseAsTemplate = () => {
    if (generatedMessage) {
      const text = generatedMessage.conventional_format
      navigator.clipboard.writeText(text)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const exampleDiff = `diff --git a/src/app.py b/src/app.py
index abc123..def456 100644
--- a/src/app.py
+++ b/src/app.py
@@ -10,6 +10,10 @@ def authenticate_user(username, password):
     if not username or not password:
         return False
     
+    # Add rate limiting
+    if check_rate_limit(username):
+        return False
+    
     user = User.query.filter_by(username=username).first()
     if user and user.check_password(password):
         return True`

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
                <label className="block text-sm font-medium mb-2">Description</label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Describe your changes..."
                  rows={8}
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
                  onClick={handleCopy}
                  className="btn-secondary flex items-center text-sm"
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
              <p className="text-sm mt-2">AI will analyze the diff and create a conventional commit</p>
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
              {/* Commit Type Badge */}
              <div className="flex items-center space-x-2">
                <span className="text-2xl">{generatedMessage.emoji}</span>
                <span className="px-2 py-1 bg-blue-500/20 text-blue-400 rounded-md text-sm">
                  {generatedMessage.commit_type}
                </span>
                {generatedMessage.changes_summary?.impact && (
                  <span className={`px-2 py-1 rounded-md text-sm ${
                    generatedMessage.changes_summary.impact === 'high' ? 'bg-red-500/20 text-red-400' :
                    generatedMessage.changes_summary.impact === 'medium' ? 'bg-yellow-500/20 text-yellow-400' :
                    'bg-green-500/20 text-green-400'
                  }`}>
                    {generatedMessage.changes_summary.impact.toUpperCase()} Impact
                  </span>
                )}
              </div>

              {/* Conventional Format */}
              <div className="bg-dark-700 rounded-lg p-3">
                <p className="text-xs text-dark-400 mb-1">Conventional Commit Format</p>
                <code className="text-sm font-mono text-green-400">
                  {generatedMessage.conventional_format}
                </code>
              </div>

              {/* Full Message */}
              <div>
                <p className="text-xs text-dark-400 mb-1">Full Commit Message</p>
                <pre className="bg-dark-900 rounded-lg p-3 overflow-x-auto text-sm font-mono whitespace-pre-wrap">
                  {generatedMessage.full_message}
                </pre>
              </div>

              {/* Changes Summary */}
              {generatedMessage.changes_summary && (
                <div className="border-t border-dark-700 pt-3 mt-2">
                  <p className="text-xs text-dark-400 mb-2">Changes Analyzed</p>
                  <div className="flex space-x-4 text-sm">
                    <span className="text-green-400">+{generatedMessage.changes_summary.additions}</span>
                    <span className="text-red-400">-{generatedMessage.changes_summary.deletions}</span>
                    {generatedMessage.changes_summary.modified_functions?.length > 0 && (
                      <span className="text-blue-400">
                        {generatedMessage.changes_summary.modified_functions.length} functions
                      </span>
                    )}
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex space-x-2 pt-2">
                <button
                  onClick={handleCopy}
                  className="flex-1 btn-primary flex items-center justify-center"
                >
                  <GitBranch className="w-4 h-4 mr-2" />
                  Copy & Use
                </button>
                <button
                  onClick={handleUseAsTemplate}
                  className="flex-1 btn-secondary flex items-center justify-center"
                >
                  <Copy className="w-4 h-4 mr-2" />
                  Copy Format Only
                </button>
              </div>
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
              This makes it easier to automate releases, generate changelogs, and understand 
              the history of changes. Format: <code className="text-green-400">&lt;type&gt;: &lt;description&gt;</code>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}