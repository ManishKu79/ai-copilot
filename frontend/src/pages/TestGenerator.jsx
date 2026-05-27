import { useState } from 'react'
import {
  TestTube,
  Code,
  Copy,
  Check,
  Download,
  Sparkles,
  AlertCircle,
  ChevronRight,
  FileText
} from 'lucide-react'
import { testAPI } from '../services/api'

export default function TestGenerator() {
  const [code, setCode] = useState('')
  const [language, setLanguage] = useState('python')
  const [functionName, setFunctionName] = useState('')
  const [generatedTests, setGeneratedTests] = useState(null)
  const [edgeCases, setEdgeCases] = useState(null)
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState('tests')
  const [copied, setCopied] = useState(false)

  const handleGenerateTests = async () => {
    if (!code.trim()) {
      alert('Please enter code to test')
      return
    }

    setLoading(true)
    try {
      const result = await testAPI.generateTests(code, language, functionName)
      setGeneratedTests(result)
    } catch (error) {
      console.error('Test generation failed:', error)
      alert('Failed to generate tests')
    } finally {
      setLoading(false)
    }
  }

  const handleGenerateEdgeCases = async () => {
    if (!code.trim()) {
      alert('Please enter code to analyze')
      return
    }

    setLoading(true)
    try {
      const result = await testAPI.generateEdgeCases(code, language)
      setEdgeCases(result)
    } catch (error) {
      console.error('Edge case generation failed:', error)
      alert('Failed to generate edge cases')
    } finally {
      setLoading(false)
    }
  }

  const handleCopy = () => {
    if (generatedTests) {
      navigator.clipboard.writeText(generatedTests.test_code)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const handleDownload = () => {
    if (generatedTests) {
      const extension = language === 'python' ? 'py' : 'js'
      const blob = new Blob([generatedTests.test_code], { type: 'text/plain' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `test_${Date.now()}.${extension}`
      a.click()
      URL.revokeObjectURL(url)
    }
  }

  const exampleCode = `def calculate_discount(price, discount_percent, customer_type="regular"):
    """Calculate discounted price based on customer type"""
    if price <= 0:
        raise ValueError("Price must be positive")
    
    if discount_percent < 0 or discount_percent > 100:
        raise ValueError("Discount must be between 0 and 100")
    
    discount = price * (discount_percent / 100)
    
    if customer_type == "premium":
        discount = discount * 1.2  # 20% extra discount for premium
    
    final_price = price - discount
    return round(final_price, 2)`

  return (
    <div>
      <h1 className="text-2xl font-semibold mb-6">AI Test Case Generator</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input Panel */}
        <div className="card">
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">Language</label>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="w-full bg-dark-700 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="python">Python (pytest)</option>
              <option value="javascript">JavaScript (Jest)</option>
              <option value="typescript">TypeScript (Jest)</option>
            </select>
          </div>
          
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">Function Name (optional)</label>
            <input
              type="text"
              value={functionName}
              onChange={(e) => setFunctionName(e.target.value)}
              placeholder="e.g., calculate_discount"
              className="w-full bg-dark-700 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">Code to Test</label>
            <textarea
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder="Paste your function/class code here..."
              rows={10}
              className="w-full bg-dark-700 rounded-md p-3 font-mono text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            />
          </div>
          
          <div className="flex space-x-3">
            <button
              onClick={handleGenerateTests}
              disabled={loading}
              className="flex-1 btn-primary flex items-center justify-center"
            >
              {loading ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              ) : (
                <TestTube className="w-4 h-4 mr-2" />
              )}
              Generate Unit Tests
            </button>
            <button
              onClick={handleGenerateEdgeCases}
              disabled={loading}
              className="flex-1 btn-secondary flex items-center justify-center"
            >
              <AlertCircle className="w-4 h-4 mr-2" />
              Edge Cases
            </button>
          </div>
          
          <div className="mt-3">
            <button
              onClick={() => setCode(exampleCode)}
              className="text-sm text-blue-400 hover:text-blue-300"
            >
              Load Example Code
            </button>
          </div>
        </div>

        {/* Output Panel */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <div className="flex space-x-2">
              <button
                onClick={() => setActiveTab('tests')}
                className={`px-3 py-1 rounded-md text-sm transition-colors ${
                  activeTab === 'tests' 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-dark-700 text-dark-300 hover:text-dark-100'
                }`}
              >
                Unit Tests
              </button>
              <button
                onClick={() => setActiveTab('edge-cases')}
                className={`px-3 py-1 rounded-md text-sm transition-colors ${
                  activeTab === 'edge-cases' 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-dark-700 text-dark-300 hover:text-dark-100'
                }`}
              >
                Edge Cases
              </button>
            </div>
            {activeTab === 'tests' && generatedTests && (
              <div className="flex space-x-2">
                <button
                  onClick={handleCopy}
                  className="btn-secondary flex items-center text-sm"
                >
                  {copied ? <Check className="w-4 h-4 mr-1" /> : <Copy className="w-4 h-4 mr-1" />}
                  Copy
                </button>
                <button
                  onClick={handleDownload}
                  className="btn-secondary flex items-center text-sm"
                >
                  <Download className="w-4 h-4 mr-1" />
                  Download
                </button>
              </div>
            )}
          </div>

          {activeTab === 'tests' && (
            <>
              {!generatedTests && !loading && (
                <div className="text-center text-dark-400 py-12">
                  <TestTube className="w-12 h-12 mx-auto mb-3 opacity-50" />
                  <p>Paste your code to generate unit tests</p>
                  <p className="text-sm mt-2">AI will create pytest/Jest test cases</p>
                </div>
              )}

              {loading && (
                <div className="text-center py-12">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-4"></div>
                  <p className="text-dark-300">Generating test cases...</p>
                </div>
              )}

              {generatedTests && !loading && (
                <div>
                  {/* Stats */}
                  <div className="grid grid-cols-3 gap-3 mb-4">
                    <div className="text-center p-2 bg-dark-800 rounded">
                      <p className="text-2xl font-bold text-blue-400">{generatedTests.test_count}</p>
                      <p className="text-xs text-dark-400">Test Cases</p>
                    </div>
                    <div className="text-center p-2 bg-dark-800 rounded">
                      <p className="text-2xl font-bold text-green-400">{generatedTests.coverage_estimate}%</p>
                      <p className="text-xs text-dark-400">Est. Coverage</p>
                    </div>
                    <div className="text-center p-2 bg-dark-800 rounded">
                      <p className="text-sm font-bold text-purple-400 capitalize">{generatedTests.framework}</p>
                      <p className="text-xs text-dark-400">Framework</p>
                    </div>
                  </div>

                  {/* Test Code */}
                  <pre className="bg-dark-900 rounded-lg p-4 overflow-x-auto text-sm font-mono whitespace-pre-wrap">
                    <code>{generatedTests.test_code}</code>
                  </pre>
                </div>
              )}
            </>
          )}

          {activeTab === 'edge-cases' && (
            <>
              {!edgeCases && !loading && (
                <div className="text-center text-dark-400 py-12">
                  <AlertCircle className="w-12 h-12 mx-auto mb-3 opacity-50" />
                  <p>Click "Edge Cases" to generate test scenarios</p>
                  <p className="text-sm mt-2">AI will identify boundary conditions</p>
                </div>
              )}

              {edgeCases && !loading && (
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  <div className="mb-3 p-2 bg-blue-500/10 rounded">
                    <p className="text-sm text-blue-400">
                      Found {edgeCases.total_cases} edge cases to test
                    </p>
                  </div>
                  {edgeCases.edge_cases.map((edge, idx) => (
                    <div key={idx} className="border border-dark-700 rounded-lg p-3">
                      <div className="flex items-start">
                        <AlertCircle className="w-4 h-4 text-yellow-400 mr-2 mt-0.5" />
                        <div>
                          <h4 className="font-medium text-sm">{edge.name}</h4>
                          <p className="text-xs text-dark-300 mt-1">{edge.description}</p>
                          <div className="mt-2 text-xs">
                            <span className="text-blue-400">Input: </span>
                            <code className="bg-dark-800 px-1 rounded">{edge.input}</code>
                          </div>
                          <div className="mt-1 text-xs">
                            <span className="text-green-400">Expected: </span>
                            <span className="text-dark-300">{edge.expected}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* Info Section */}
      <div className="mt-6 card bg-dark-800/50">
        <div className="flex items-start">
          <TestTube className="w-5 h-5 text-blue-400 mr-3 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="text-sm font-medium mb-1">Test Generation Features</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs text-dark-300">
              <span>✓ Unit test generation</span>
              <span>✓ Edge case detection</span>
              <span>✓ Mock/stub creation</span>
              <span>✓ Assertion suggestions</span>
              <span>✓ Exception testing</span>
              <span>✓ Parameterized tests</span>
              <span>✓ Coverage estimation</span>
              <span>✓ Framework-specific code</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}