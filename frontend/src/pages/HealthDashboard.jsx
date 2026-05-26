import { useState, useEffect } from 'react'
import {
  Activity,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  Clock,
  DollarSign,
  FileText,
  Shield,
  Zap,
  Code,
  TestTube,
  BookOpen
} from 'lucide-react'
import {
  AreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, PieChart, Pie, Cell
} from 'recharts'
import useAppStore from '../store/useAppStore'

export default function HealthDashboard() {
  const { currentAnalysis } = useAppStore()
  const [healthData, setHealthData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (currentAnalysis) {
      analyzeHealth()
    }
  }, [currentAnalysis])

  const analyzeHealth = async () => {
    setLoading(true)
    setError(null)
    
    try {
      console.log('Analyzing health for:', currentAnalysis?.name)
      console.log('Files count:', currentAnalysis?.files_preview?.length)
      
      const response = await fetch('http://localhost:8000/api/health/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          repository_data: currentAnalysis
        })
      })
      
      const data = await response.json()
      console.log('Health API Response:', data)
      
      if (data.success) {
        setHealthData(data.health)
      } else {
        setError('Failed to analyze health')
      }
    } catch (err) {
      console.error('Health analysis failed:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const getGradeColor = (grade) => {
    const colors = {
      'A+': 'text-green-400',
      'A': 'text-green-300',
      'B': 'text-blue-400',
      'C': 'text-yellow-400',
      'C+': 'text-yellow-400',
      'D': 'text-orange-400',
      'F': 'text-red-400'
    }
    return colors[grade] || 'text-gray-400'
  }

  const pieData = healthData ? [
    { name: 'Maintainability', value: healthData.metrics.maintainability, color: '#3b82f6' },
    { name: 'Test Coverage', value: healthData.metrics.test_coverage, color: '#22c55e' },
    { name: 'Documentation', value: healthData.metrics.documentation_score, color: '#a855f7' }
  ] : []

  if (!currentAnalysis) {
    return (
      <div>
        <h1 className="text-2xl font-semibold mb-6">Project Health Dashboard</h1>
        <div className="card text-center py-12">
          <Activity className="w-16 h-16 text-dark-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium mb-2">No Repository Analyzed</h3>
          <p className="text-dark-300">
            First analyze a repository to see health metrics
          </p>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div>
        <h1 className="text-2xl font-semibold mb-6">Project Health Dashboard</h1>
        <div className="card text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-dark-300">Analyzing repository health...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div>
        <h1 className="text-2xl font-semibold mb-6">Project Health Dashboard</h1>
        <div className="card text-center py-12">
          <AlertTriangle className="w-16 h-16 text-red-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium mb-2">Analysis Failed</h3>
          <p className="text-dark-300">{error}</p>
          <button onClick={analyzeHealth} className="mt-4 btn-primary">
            Try Again
          </button>
        </div>
      </div>
    )
  }

  return (
    <div>
      <h1 className="text-2xl font-semibold mb-6">Project Health Dashboard</h1>
      
      {healthData && (
        <div className="space-y-6">
          {/* Summary Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="card bg-dark-800/50">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-dark-300 text-sm">Total Files</p>
                  <p className="text-2xl font-bold">{healthData.summary?.total_files || 0}</p>
                </div>
                <FileText className="w-8 h-8 text-blue-400" />
              </div>
            </div>
            <div className="card bg-dark-800/50">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-dark-300 text-sm">Source Files</p>
                  <p className="text-2xl font-bold">{healthData.summary?.source_files || 0}</p>
                </div>
                <Code className="w-8 h-8 text-green-400" />
              </div>
            </div>
            <div className="card bg-dark-800/50">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-dark-300 text-sm">Test Files</p>
                  <p className="text-2xl font-bold">{healthData.summary?.test_files || 0}</p>
                </div>
                <TestTube className="w-8 h-8 text-purple-400" />
              </div>
            </div>
            <div className="card bg-dark-800/50">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-dark-300 text-sm">Has README</p>
                  <p className="text-2xl font-bold">{healthData.summary?.has_readme ? 'Yes' : 'No'}</p>
                </div>
                <BookOpen className="w-8 h-8 text-yellow-400" />
              </div>
            </div>
          </div>

          {/* Overall Health Score */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">Overall Health Score</h2>
              <div className="flex items-center space-x-4">
                <span className="text-sm text-dark-300">Industry Average: 68</span>
                <span className={`text-2xl font-bold ${getGradeColor(healthData.grade)}`}>
                  Grade: {healthData.grade}
                </span>
              </div>
            </div>
            
            <div className="relative pt-4">
              <div className="flex justify-between mb-2">
                <span className="text-sm text-dark-400">0</span>
                <span className="text-sm text-dark-400">25</span>
                <span className="text-sm text-dark-400">50</span>
                <span className="text-sm text-dark-400">75</span>
                <span className="text-sm text-dark-400">100</span>
              </div>
              <div className="bg-dark-700 rounded-full h-4">
                <div 
                  className="bg-gradient-to-r from-red-500 via-yellow-500 to-green-500 rounded-full h-4 transition-all"
                  style={{ width: `${healthData.overall_health_score}%` }}
                />
              </div>
              <div className="text-center mt-4">
                <span className="text-3xl font-bold">{healthData.overall_health_score}</span>
                <span className="text-dark-400 ml-2">/ 100</span>
              </div>
            </div>
          </div>

          {/* Metrics Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            <div className="card">
              <div className="flex items-center justify-between mb-2">
                <Shield className="w-5 h-5 text-blue-400" />
                <span className={`text-sm font-medium ${healthData.metrics.maintainability >= 70 ? 'text-green-400' : 'text-yellow-400'}`}>
                  {healthData.metrics.maintainability}%
                </span>
              </div>
              <p className="text-sm text-dark-300">Maintainability</p>
              <div className="mt-2 bg-dark-700 rounded-full h-1.5">
                <div 
                  className="bg-blue-500 rounded-full h-1.5 transition-all"
                  style={{ width: `${healthData.metrics.maintainability}%` }}
                />
              </div>
            </div>

            <div className="card">
              <div className="flex items-center justify-between mb-2">
                <CheckCircle className="w-5 h-5 text-green-400" />
                <span className={`text-sm font-medium ${healthData.metrics.test_coverage >= 70 ? 'text-green-400' : 'text-yellow-400'}`}>
                  {healthData.metrics.test_coverage}%
                </span>
              </div>
              <p className="text-sm text-dark-300">Test Coverage</p>
              <div className="mt-2 bg-dark-700 rounded-full h-1.5">
                <div 
                  className="bg-green-500 rounded-full h-1.5 transition-all"
                  style={{ width: `${healthData.metrics.test_coverage}%` }}
                />
              </div>
            </div>

            <div className="card">
              <div className="flex items-center justify-between mb-2">
                <Zap className="w-5 h-5 text-yellow-400" />
                <span className={`text-sm font-medium ${healthData.metrics.complexity_score <= 5 ? 'text-green-400' : 'text-yellow-400'}`}>
                  {healthData.metrics.complexity_score}/10
                </span>
              </div>
              <p className="text-sm text-dark-300">Complexity</p>
              <div className="mt-2 bg-dark-700 rounded-full h-1.5">
                <div 
                  className="bg-yellow-500 rounded-full h-1.5 transition-all"
                  style={{ width: `${(healthData.metrics.complexity_score / 10) * 100}%` }}
                />
              </div>
            </div>

            <div className="card">
              <div className="flex items-center justify-between mb-2">
                <FileText className="w-5 h-5 text-purple-400" />
                <span className="text-sm font-medium text-purple-400">
                  {healthData.metrics.duplication_rate}%
                </span>
              </div>
              <p className="text-sm text-dark-300">Duplication Rate</p>
              <div className="mt-2 bg-dark-700 rounded-full h-1.5">
                <div 
                  className="bg-purple-500 rounded-full h-1.5 transition-all"
                  style={{ width: `${healthData.metrics.duplication_rate}%` }}
                />
              </div>
            </div>

            <div className="card">
              <div className="flex items-center justify-between mb-2">
                <Activity className="w-5 h-5 text-orange-400" />
                <span className="text-sm font-medium text-orange-400">
                  {healthData.metrics.documentation_score}%
                </span>
              </div>
              <p className="text-sm text-dark-300">Documentation</p>
              <div className="mt-2 bg-dark-700 rounded-full h-1.5">
                <div 
                  className="bg-orange-500 rounded-full h-1.5 transition-all"
                  style={{ width: `${healthData.metrics.documentation_score}%` }}
                />
              </div>
            </div>
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="card">
              <h3 className="text-lg font-semibold mb-4">Quality Trends</h3>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={healthData.trends.monthly.labels.map((label, i) => ({
                  month: label,
                  score: healthData.trends.monthly.values[i]
                }))}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                  <XAxis dataKey="month" stroke="#888" />
                  <YAxis stroke="#888" />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#1e1e1e', border: '1px solid #333' }}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="score" 
                    stroke="#3b82f6" 
                    fill="#3b82f6" 
                    fillOpacity={0.2}
                  />
                </AreaChart>
              </ResponsiveContainer>
              <div className="mt-2 text-center">
                <span className="text-sm text-green-400">
                  ↑ {healthData.trends.improvement_rate}% improvement over 6 months
                </span>
              </div>
            </div>

            <div className="card">
              <h3 className="text-lg font-semibold mb-4">Quality Distribution</h3>
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
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Technical Debt */}
          {healthData.technical_debt.debt_items && healthData.technical_debt.debt_items.length > 0 && (
            <div className="card">
              <h3 className="text-lg font-semibold mb-4">Technical Debt Analysis</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="text-center p-3 bg-red-500/10 rounded-lg">
                  <Clock className="w-6 h-6 text-red-400 mx-auto mb-2" />
                  <p className="text-2xl font-bold">{healthData.technical_debt.total_hours}h</p>
                  <p className="text-xs text-dark-300">Estimated Refactoring Time</p>
                </div>
                <div className="text-center p-3 bg-yellow-500/10 rounded-lg">
                  <DollarSign className="w-6 h-6 text-yellow-400 mx-auto mb-2" />
                  <p className="text-2xl font-bold">${healthData.technical_debt.estimated_cost}</p>
                  <p className="text-xs text-dark-300">Estimated Cost to Fix</p>
                </div>
                <div className="text-center p-3 bg-blue-500/10 rounded-lg">
                  <AlertTriangle className="w-6 h-6 text-blue-400 mx-auto mb-2" />
                  <p className="text-2xl font-bold capitalize">{healthData.technical_debt.severity}</p>
                  <p className="text-xs text-dark-300">Debt Severity</p>
                </div>
              </div>
              
              <div>
                <h4 className="text-sm font-medium mb-2">Files Needing Attention</h4>
                <div className="space-y-2">
                  {healthData.technical_debt.debt_items.map((item, idx) => (
                    <div key={idx} className="flex items-center justify-between p-2 bg-dark-700 rounded">
                      <div>
                        <span className="text-sm font-mono">{item.file}</span>
                        <span className="ml-2 text-xs text-dark-400">Complexity: {item.complexity}</span>
                      </div>
                      <div className="flex items-center">
                        <span className="text-sm text-yellow-400">{item.estimated_hours}h</span>
                        <span className={`ml-2 text-xs px-2 py-0.5 rounded ${
                          item.priority === 'high' ? 'bg-red-500/20 text-red-400' : 'bg-yellow-500/20 text-yellow-400'
                        }`}>
                          {item.priority}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Recommendations */}
          <div className="card">
            <h3 className="text-lg font-semibold mb-4">Recommendations</h3>
            <div className="space-y-3">
              {healthData.recommendations.map((rec, idx) => (
                <div key={idx} className="border-l-4 border-blue-500 bg-dark-700 p-3 rounded">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center">
                      <span className={`text-xs px-2 py-0.5 rounded mr-2 ${
                        rec.priority === 'high' ? 'bg-red-500/20 text-red-400' : 
                        rec.priority === 'medium' ? 'bg-yellow-500/20 text-yellow-400' :
                        'bg-green-500/20 text-green-400'
                      }`}>
                        {rec.priority.toUpperCase()}
                      </span>
                      <h4 className="font-medium">{rec.title}</h4>
                    </div>
                    {rec.priority === 'high' ? (
                      <TrendingUp className="w-4 h-4 text-red-400" />
                    ) : (
                      <Activity className="w-4 h-4 text-yellow-400" />
                    )}
                  </div>
                  <p className="text-sm text-dark-300 mb-2">{rec.description}</p>
                  <p className="text-sm text-blue-400">💡 {rec.action}</p>
                  <p className="text-xs text-green-400 mt-1">✓ Expected impact: {rec.impact}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}