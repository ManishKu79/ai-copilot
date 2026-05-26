import { useState, useEffect } from 'react'
import { 
  TrendingUp, 
  AlertTriangle, 
  Shield, 
  Activity,
  FileCode,
  ChevronRight,
  Download,
  BarChart3,
  GitBranch
} from 'lucide-react'
import useAppStore from '../store/useAppStore'
import { bugPredictionAPI } from '../services/api'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

export default function BugPrediction() {
  const { currentAnalysis } = useAppStore()
  const [riskAnalysis, setRiskAnalysis] = useState(null)
  const [loading, setLoading] = useState(false)
  const [selectedFile, setSelectedFile] = useState(null)
  const [activeTab, setActiveTab] = useState('overview')

  useEffect(() => {
    if (currentAnalysis && currentAnalysis.files) {
      analyzeRisks()
    }
  }, [currentAnalysis])

  const analyzeRisks = async () => {
    setLoading(true)
    try {
      const filesData = currentAnalysis.files_preview || currentAnalysis.files || []
      const result = await bugPredictionAPI.predictRisks('current_repo', filesData)
      if (result.success) {
        setRiskAnalysis(result.analysis)
      }
    } catch (error) {
      console.error('Risk analysis failed:', error)
    } finally {
      setLoading(false)
    }
  }

  const getRiskColor = (level) => {
    switch(level) {
      case 'high': return 'text-red-400 bg-red-500/10 border-red-500/20'
      case 'medium': return 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20'
      case 'low': return 'text-green-400 bg-green-500/10 border-green-500/20'
      default: return 'text-gray-400 bg-gray-500/10 border-gray-500/20'
    }
  }

  const getRiskIcon = (level) => {
    switch(level) {
      case 'high': return <AlertTriangle className="w-4 h-4" />
      case 'medium': return <Activity className="w-4 h-4" />
      case 'low': return <Shield className="w-4 h-4" />
      default: return <FileCode className="w-4 h-4" />
    }
  }

  const pieData = riskAnalysis ? [
    { name: 'High Risk', value: riskAnalysis.risk_distribution.high, color: '#ef4444' },
    { name: 'Medium Risk', value: riskAnalysis.risk_distribution.medium, color: '#eab308' },
    { name: 'Low Risk', value: riskAnalysis.risk_distribution.low, color: '#22c55e' }
  ] : []

  const barData = riskAnalysis?.high_risk_files?.slice(0, 5).map(file => ({
    name: file.file_name.length > 30 ? file.file_name.substring(0, 27) + '...' : file.file_name,
    score: file.risk_score * 100
  })) || []

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-semibold">Bug Prediction Engine</h1>
        {riskAnalysis && (
          <button className="btn-secondary flex items-center">
            <Download className="w-4 h-4 mr-2" />
            Export Report
          </button>
        )}
      </div>

      {!currentAnalysis && (
        <div className="card text-center py-12">
          <TrendingUp className="w-16 h-16 text-dark-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium mb-2">No Repository Analyzed</h3>
          <p className="text-dark-300">
            First analyze a repository to see bug predictions and risk analysis
          </p>
        </div>
      )}

      {loading && (
        <div className="card text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-dark-300">Analyzing codebase for potential bugs...</p>
        </div>
      )}

      {riskAnalysis && !loading && (
        <div className="space-y-6">
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-dark-300 text-sm">Overall Risk Score</p>
                  <p className="text-2xl font-bold mt-1">{riskAnalysis.overall_risk_score}/100</p>
                </div>
                <TrendingUp className="w-8 h-8 text-blue-400" />
              </div>
              <div className="mt-2">
                <span className={`text-xs px-2 py-1 rounded ${getRiskColor(riskAnalysis.risk_level)}`}>
                  {riskAnalysis.risk_level.toUpperCase()} RISK
                </span>
              </div>
            </div>

            <div className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-dark-300 text-sm">Maintainability Score</p>
                  <p className="text-2xl font-bold mt-1">{riskAnalysis.maintainability_score}/100</p>
                </div>
                <Activity className="w-8 h-8 text-green-400" />
              </div>
              <div className="mt-2 bg-dark-600 rounded-full h-2">
                <div 
                  className="bg-green-500 rounded-full h-2 transition-all"
                  style={{ width: `${riskAnalysis.maintainability_score}%` }}
                />
              </div>
            </div>

            <div className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-dark-300 text-sm">High Risk Files</p>
                  <p className="text-2xl font-bold mt-1">{riskAnalysis.high_risk_files_count}</p>
                </div>
                <AlertTriangle className="w-8 h-8 text-red-400" />
              </div>
              <p className="text-xs text-dark-300 mt-2">
                {riskAnalysis.medium_risk_files_count} medium risk files
              </p>
            </div>

            <div className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-dark-300 text-sm">Confidence</p>
                  <p className="text-2xl font-bold mt-1">{riskAnalysis.prediction_confidence}%</p>
                </div>
                <BarChart3 className="w-8 h-8 text-purple-400" />
              </div>
              <p className="text-xs text-dark-300 mt-2">
                Based on {riskAnalysis.total_files_analyzed} files
              </p>
            </div>
          </div>

          {/* Tabs */}
          <div className="border-b border-dark-700">
            <div className="flex space-x-6">
              {['overview', 'high-risk-files', 'recommendations', 'patterns'].map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`pb-2 px-1 capitalize transition-colors ${
                    activeTab === tab 
                      ? 'text-blue-400 border-b-2 border-blue-400' 
                      : 'text-dark-300 hover:text-dark-100'
                  }`}
                >
                  {tab.replace('-', ' ')}
                </button>
              ))}
            </div>
          </div>

          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="card">
                <h3 className="text-lg font-semibold mb-4">Risk Distribution</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={pieData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={5}
                      dataKey="value"
                      label={({ name, value }) => `${name}: ${value}%`}
                    >
                      {pieData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>

              <div className="card">
                <h3 className="text-lg font-semibold mb-4">Top Risk Files</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={barData} layout="vertical">
                    <XAxis type="number" domain={[0, 100]} />
                    <YAxis type="category" dataKey="name" width={200} />
                    <Tooltip />
                    <Bar dataKey="score" fill="#ef4444" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {/* High Risk Files Tab */}
          {activeTab === 'high-risk-files' && (
            <div className="card">
              <h3 className="text-lg font-semibold mb-4">High Risk Files Details</h3>
              <div className="space-y-3">
                {riskAnalysis.high_risk_files.map((file, idx) => (
                  <div 
                    key={idx}
                    className={`border rounded-lg p-4 cursor-pointer transition-all ${getRiskColor(file.risk_level)}`}
                    onClick={() => setSelectedFile(selectedFile === file.file_path ? null : file.file_path)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center">
                          <FileCode className="w-4 h-4 mr-2" />
                          <span className="font-mono text-sm">{file.file_name}</span>
                          <span className={`ml-3 text-xs px-2 py-0.5 rounded ${getRiskColor(file.risk_level)}`}>
                            Risk: {file.risk_score * 100}%
                          </span>
                          {file.ml_bug_probability && (
                            <span className="ml-2 text-xs text-dark-300">
                              ML Predict: {file.ml_bug_probability}%
                            </span>
                          )}
                        </div>
                        <div className="mt-2 grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
                          <div>Complexity: {file.complexity}</div>
                          <div>Lines: {file.lines_of_code}</div>
                          <div>Complexity Risk: {file.complexity_risk * 100}%</div>
                          <div>Size Risk: {file.size_risk * 100}%</div>
                        </div>
                      </div>
                      <ChevronRight className={`w-4 h-4 transition-transform ${selectedFile === file.file_path ? 'rotate-90' : ''}`} />
                    </div>
                    
                    {selectedFile === file.file_path && (
                      <div className="mt-4 pt-4 border-t border-dark-600">
                        <div className="mb-3">
                          <p className="text-sm font-medium mb-2">📊 Predictions:</p>
                          <ul className="space-y-1">
                            {file.predictions.map((pred, i) => (
                              <li key={i} className="text-sm text-dark-300">• {pred}</li>
                            ))}
                          </ul>
                        </div>
                        <div>
                          <p className="text-sm font-medium mb-2">🎯 Suggested Actions:</p>
                          <ul className="space-y-1">
                            {file.suggested_actions.map((action, i) => (
                              <li key={i} className="text-sm text-dark-300">• {action}</li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recommendations Tab */}
          {activeTab === 'recommendations' && (
            <div className="card">
              <h3 className="text-lg font-semibold mb-4">Actionable Recommendations</h3>
              <div className="space-y-4">
                {riskAnalysis.recommendations.map((rec, idx) => (
                  <div key={idx} className="border-l-4 border-blue-500 bg-dark-700 p-4 rounded">
                    <div className="flex items-center mb-2">
                      <span className={`text-xs px-2 py-0.5 rounded mr-2 ${
                        rec.priority === 'critical' ? 'bg-red-500/20 text-red-400' :
                        rec.priority === 'high' ? 'bg-orange-500/20 text-orange-400' :
                        'bg-yellow-500/20 text-yellow-400'
                      }`}>
                        {rec.priority.toUpperCase()}
                      </span>
                      <h4 className="font-medium">{rec.title}</h4>
                    </div>
                    <p className="text-sm text-dark-300 mb-2">{rec.description}</p>
                    <p className="text-sm text-blue-400">💡 {rec.action}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Patterns Tab */}
          {activeTab === 'patterns' && riskAnalysis.risk_patterns && (
            <div className="card">
              <h3 className="text-lg font-semibold mb-4">Detected Risk Patterns</h3>
              <div className="space-y-4">
                {riskAnalysis.risk_patterns.map((pattern, idx) => (
                  <div key={idx} className="bg-dark-700 rounded-lg p-4">
                    <h4 className="font-medium mb-2">{pattern.pattern}</h4>
                    <p className="text-sm text-dark-300 mb-2">Impact: {pattern.impact}</p>
                    <p className="text-sm text-green-400">✓ {pattern.suggestion}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}