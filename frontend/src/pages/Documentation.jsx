import { useState } from 'react'
import { 
  FileText, 
  Download, 
  Copy, 
  Check,
  Eye,
  Code,
  BookOpen,
  FileCode,
  RefreshCw
} from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import useAppStore from '../store/useAppStore'
import { docsAPI } from '../services/api'

// Simple code block component without external dependencies
const CodeBlock = ({ children, language }) => {
  return (
    <div className="relative">
      <div className="absolute top-2 right-2 text-xs text-dark-400 bg-dark-800 px-2 py-1 rounded">
        {language || 'code'}
      </div>
      <pre className="bg-dark-900 rounded-lg p-4 overflow-x-auto">
        <code className="text-sm text-dark-100 font-mono">
          {children}
        </code>
      </pre>
    </div>
  )
}

export default function Documentation() {
  const { currentAnalysis } = useAppStore()
  const [generatedReadme, setGeneratedReadme] = useState(null)
  const [generatedApiDocs, setGeneratedApiDocs] = useState(null)
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState('readme')
  const [copied, setCopied] = useState(false)
  const [apiCode, setApiCode] = useState('')
  const [apiLanguage, setApiLanguage] = useState('python')

  const generateReadme = async () => {
    if (!currentAnalysis) {
      alert('Please analyze a repository first')
      return
    }
    
    setLoading(true)
    try {
      const result = await docsAPI.generateReadme(currentAnalysis)
      if (result.success) {
        setGeneratedReadme(result.readme)
      }
    } catch (error) {
      console.error('README generation failed:', error)
      alert('Failed to generate README')
    } finally {
      setLoading(false)
    }
  }

  const generateApiDocs = async () => {
    if (!apiCode.trim()) {
      alert('Please enter code to generate API documentation')
      return
    }
    
    setLoading(true)
    try {
      const result = await docsAPI.generateApiDocs(apiCode, apiLanguage)
      if (result.success) {
        setGeneratedApiDocs(result.documentation)
      }
    } catch (error) {
      console.error('API docs generation failed:', error)
      alert('Failed to generate API documentation')
    } finally {
      setLoading(false)
    }
  }

  const handleCopy = async (text) => {
    await navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleDownload = (content, filename) => {
    const blob = new Blob([content], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.click()
    URL.revokeObjectURL(url)
  }

  // Custom markdown components
  const markdownComponents = {
    code({ node, inline, className, children, ...props }) {
      const match = /language-(\w+)/.exec(className || '')
      const language = match ? match[1] : ''
      return !inline ? (
        <CodeBlock language={language}>
          {String(children).replace(/\n$/, '')}
        </CodeBlock>
      ) : (
        <code className="bg-dark-700 px-1 py-0.5 rounded text-sm font-mono" {...props}>
          {children}
        </code>
      )
    },
    h1: ({ children }) => <h1 className="text-2xl font-bold mt-6 mb-4 pb-2 border-b border-dark-700">{children}</h1>,
    h2: ({ children }) => <h2 className="text-xl font-semibold mt-5 mb-3">{children}</h2>,
    h3: ({ children }) => <h3 className="text-lg font-medium mt-4 mb-2">{children}</h3>,
    p: ({ children }) => <p className="mb-4 leading-relaxed">{children}</p>,
    ul: ({ children }) => <ul className="list-disc list-inside mb-4 space-y-1">{children}</ul>,
    ol: ({ children }) => <ol className="list-decimal list-inside mb-4 space-y-1">{children}</ol>,
    li: ({ children }) => <li className="text-dark-200">{children}</li>,
    a: ({ href, children }) => (
      <a href={href} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300 underline">
        {children}
      </a>
    ),
    blockquote: ({ children }) => (
      <blockquote className="border-l-4 border-blue-500 pl-4 italic my-4 text-dark-300">
        {children}
      </blockquote>
    ),
    table: ({ children }) => (
      <div className="overflow-x-auto my-4">
        <table className="min-w-full border border-dark-700 rounded-lg">
          {children}
        </table>
      </div>
    ),
    th: ({ children }) => (
      <th className="border border-dark-700 px-4 py-2 bg-dark-800 text-left">{children}</th>
    ),
    td: ({ children }) => (
      <td className="border border-dark-700 px-4 py-2">{children}</td>
    ),
    hr: () => <hr className="my-6 border-dark-700" />
  }

  return (
    <div>
      <h1 className="text-2xl font-semibold mb-6">Documentation Generator</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Panel - Controls */}
        <div className="space-y-6">
          {/* README Generator Card */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center">
                <FileText className="w-5 h-5 text-blue-400 mr-2" />
                <h2 className="text-lg font-semibold">README Generator</h2>
              </div>
              <button
                onClick={generateReadme}
                disabled={loading || !currentAnalysis}
                className="btn-primary flex items-center text-sm"
              >
                <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                Generate README
              </button>
            </div>
            
            {!currentAnalysis && (
              <div className="text-center text-dark-400 py-4 text-sm">
                ⚠️ No repository analyzed. Please analyze a repository first.
              </div>
            )}
            
            {generatedReadme && (
              <div className="mt-4 flex space-x-2">
                <button
                  onClick={() => handleCopy(generatedReadme)}
                  className="flex-1 btn-secondary flex items-center justify-center text-sm"
                >
                  {copied ? <Check className="w-4 h-4 mr-2" /> : <Copy className="w-4 h-4 mr-2" />}
                  Copy
                </button>
                <button
                  onClick={() => handleDownload(generatedReadme, 'README.md')}
                  className="flex-1 btn-secondary flex items-center justify-center text-sm"
                >
                  <Download className="w-4 h-4 mr-2" />
                  Download
                </button>
              </div>
            )}
          </div>
          
          {/* API Documentation Generator Card */}
          <div className="card">
            <div className="flex items-center mb-4">
              <Code className="w-5 h-5 text-green-400 mr-2" />
              <h2 className="text-lg font-semibold">API Documentation</h2>
            </div>
            
            <div className="mb-3">
              <label className="block text-sm font-medium mb-2">Language</label>
              <select
                value={apiLanguage}
                onChange={(e) => setApiLanguage(e.target.value)}
                className="w-full bg-dark-700 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="python">Python</option>
                <option value="javascript">JavaScript</option>
                <option value="typescript">TypeScript</option>
              </select>
            </div>
            
            <div className="mb-3">
              <label className="block text-sm font-medium mb-2">Code</label>
              <textarea
                value={apiCode}
                onChange={(e) => setApiCode(e.target.value)}
                placeholder={`# Paste your code here
# Example:
def get_user(user_id):
    """Get user by ID"""
    return {"id": user_id, "name": "John"}

def create_user(name, email):
    """Create a new user"""
    return {"id": 123, "name": name, "email": email}`}
                rows={8}
                className="w-full bg-dark-700 rounded-md p-3 font-mono text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
              />
            </div>
            
            <button
              onClick={generateApiDocs}
              disabled={loading}
              className="btn-primary w-full flex items-center justify-center"
            >
              <BookOpen className="w-4 h-4 mr-2" />
              Generate API Docs
            </button>
            
            {generatedApiDocs && (
              <div className="mt-4 flex space-x-2">
                <button
                  onClick={() => handleCopy(generatedApiDocs)}
                  className="flex-1 btn-secondary flex items-center justify-center text-sm"
                >
                  {copied ? <Check className="w-4 h-4 mr-2" /> : <Copy className="w-4 h-4 mr-2" />}
                  Copy
                </button>
                <button
                  onClick={() => handleDownload(generatedApiDocs, 'API_DOCS.md')}
                  className="flex-1 btn-secondary flex items-center justify-center text-sm"
                >
                  <Download className="w-4 h-4 mr-2" />
                  Download
                </button>
              </div>
            )}
          </div>
        </div>
        
        {/* Right Panel - Preview */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              <Eye className="w-5 h-5 text-purple-400 mr-2" />
              <h2 className="text-lg font-semibold">Preview</h2>
            </div>
            <div className="flex space-x-2">
              <button
                onClick={() => setActiveTab('readme')}
                className={`px-3 py-1 rounded-md text-sm transition-colors ${
                  activeTab === 'readme' 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-dark-700 text-dark-300 hover:text-dark-100'
                }`}
              >
                README
              </button>
              <button
                onClick={() => setActiveTab('api')}
                className={`px-3 py-1 rounded-md text-sm transition-colors ${
                  activeTab === 'api' 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-dark-700 text-dark-300 hover:text-dark-100'
                }`}
              >
                API Docs
              </button>
            </div>
          </div>
          
          <div className="prose prose-invert max-w-none overflow-y-auto" style={{ maxHeight: '600px' }}>
            {activeTab === 'readme' && (
              generatedReadme ? (
                <ReactMarkdown components={markdownComponents}>
                  {generatedReadme}
                </ReactMarkdown>
              ) : (
                <div className="text-center text-dark-400 py-12">
                  <FileCode className="w-12 h-12 mx-auto mb-3 opacity-50" />
                  <p>Click "Generate README" to create documentation</p>
                  <p className="text-sm mt-2">Based on your repository analysis</p>
                </div>
              )
            )}
            
            {activeTab === 'api' && (
              generatedApiDocs ? (
                <ReactMarkdown components={markdownComponents}>
                  {generatedApiDocs}
                </ReactMarkdown>
              ) : (
                <div className="text-center text-dark-400 py-12">
                  <BookOpen className="w-12 h-12 mx-auto mb-3 opacity-50" />
                  <p>Paste code and click "Generate API Docs"</p>
                  <p className="text-sm mt-2">Creates documentation from function signatures</p>
                </div>
              )
            )}
          </div>
        </div>
      </div>
    </div>
  )
}