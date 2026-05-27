import { useState, useEffect } from 'react'
import {
  Package,
  AlertTriangle,
  Shield,
  Lock,
  ExternalLink,
  CheckCircle,
  XCircle,
  AlertCircle,
  RefreshCw
} from 'lucide-react'
import useAppStore from '../store/useAppStore'
import { dependencyAPI } from '../services/api'

export default function DependencyScanner() {
  const { currentAnalysis } = useAppStore()
  const [scanResult, setScanResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState('vulnerabilities')

  useEffect(() => {
    if (currentAnalysis) {
      scanDependencies()
    }
  }, [currentAnalysis])

  const scanDependencies = async () => {
    setLoading(true)
    try {
      const result = await dependencyAPI.scanDependencies(currentAnalysis)
      setScanResult(result)
    } catch (error) {
      console.error('Dependency scan failed:', error)
    } finally {
      setLoading(false)
    }
  }

  const getSeverityColor = (severity) => {
    switch(severity?.toLowerCase()) {
      case 'critical': return 'bg-red-500/20 text-red-400 border-red-500/20'
      case 'high': return 'bg-orange-500/20 text-orange-400 border-orange-500/20'
      case 'medium': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/20'
      case 'low': return 'bg-blue-500/20 text-blue-400 border-blue-500/20'
      default: return 'bg-gray-500/20 text-gray-400 border-gray-500/20'
    }
  }

  const getSecurityScoreColor = (score) => {
    if (score >= 80) return 'text-green-400'
    if (score >= 60) return 'text-yellow-400'
    return 'text-red-400'
  }

  if (!currentAnalysis) {
    return (
      <div>
        <h1 className="text-2xl font-semibold mb-6">Dependency & Security Scanner</h1>
        <div className="card text-center py-12">
          <Package className="w-16 h-16 text-dark-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium mb-2">No Repository Analyzed</h3>
          <p className="text-dark-300">First analyze a repository to scan dependencies</p>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div>
        <h1 className="text-2xl font-semibold mb-6">Dependency & Security Scanner</h1>
        <div className="card text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-dark-300">Scanning dependencies for vulnerabilities...</p>
        </div>
      </div>
    )
  }

  return (
    <div>
      <h1 className="text-2xl font-semibold mb-6">Dependency & Security Scanner</h1>
      
      {scanResult && (
        <div className="space-y-6">
          {/* Security Score Card */}
          <div className="card bg-gradient-to-r from-blue-500/10 to-purple-500/10">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-dark-300 text-sm">Security Score</p>
                <p className={`text-4xl font-bold ${getSecurityScoreColor(scanResult.security_score)}`}>
                  {scanResult.security_score}/100
                </p>
              </div>
              <Shield className="w-12 h-12 text-blue-400 opacity-50" />
            </div>
            <div className="mt-3 bg-dark-700 rounded-full h-2">
              <div 
                className={`rounded-full h-2 transition-all ${
                  scanResult.security_score >= 80 ? 'bg-green-500' :
                  scanResult.security_score >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                }`}
                style={{ width: `${scanResult.security_score}%` }}
              />
            </div>
          </div>

          {/* Summary Stats */}
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <div className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-dark-300 text-sm">Total Dependencies</p>
                  <p className="text-2xl font-bold">{scanResult.total_dependencies}</p>
                </div>
                <Package className="w-8 h-8 text-blue-400" />
              </div>
            </div>
            <div className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-dark-300 text-sm">Vulnerabilities</p>
                  <p className="text-2xl font-bold text-red-400">{scanResult.vulnerability_count}</p>
                </div>
                <AlertTriangle className="w-8 h-8 text-red-400" />
              </div>
            </div>
            <div className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-dark-300 text-sm">Critical</p>
                  <p className="text-2xl font-bold text-red-500">{scanResult.critical_vulnerabilities}</p>
                </div>
                <XCircle className="w-8 h-8 text-red-500" />
              </div>
            </div>
            <div className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-dark-300 text-sm">Secrets Found</p>
                  <p className="text-2xl font-bold text-yellow-400">{scanResult.secrets_found?.length || 0}</p>
                </div>
                <Lock className="w-8 h-8 text-yellow-400" />
              </div>
            </div>
            <div className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-dark-300 text-sm">Outdated</p>
                  <p className="text-2xl font-bold text-orange-400">{scanResult.outdated_packages?.length || 0}</p>
                </div>
                <RefreshCw className="w-8 h-8 text-orange-400" />
              </div>
            </div>
          </div>

          {/* Tabs */}
          <div className="border-b border-dark-700">
            <div className="flex space-x-6">
              {['vulnerabilities', 'dependencies', 'secrets', 'unsafe-imports', 'recommendations'].map((tab) => (
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

          {/* Vulnerabilities Tab */}
          {activeTab === 'vulnerabilities' && (
            <div className="card">
              <h3 className="text-lg font-semibold mb-4">Security Vulnerabilities</h3>
              {scanResult.vulnerabilities.length === 0 ? (
                <div className="text-center text-green-400 py-8">
                  <CheckCircle className="w-12 h-12 mx-auto mb-3" />
                  <p>No vulnerabilities detected!</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {scanResult.vulnerabilities.map((vuln, idx) => (
                    <div key={idx} className={`border rounded-lg p-4 ${getSeverityColor(vuln.severity)}`}>
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center mb-2">
                            <AlertTriangle className="w-4 h-4 mr-2" />
                            <span className="font-mono text-sm font-medium">{vuln.name}@{vuln.version}</span>
                            <span className={`ml-3 text-xs px-2 py-0.5 rounded ${getSeverityColor(vuln.severity)}`}>
                              {vuln.severity?.toUpperCase()}
                            </span>
                            {vuln.cve && (
                              <span className="ml-2 text-xs text-dark-400">{vuln.cve}</span>
                            )}
                          </div>
                          <p className="text-sm text-dark-300 mb-2">{vuln.description}</p>
                          <div className="flex items-center text-sm">
                            <span className="text-yellow-400">Fix version: {vuln.fix_version}</span>
                            <button className="ml-4 text-blue-400 hover:text-blue-300 flex items-center">
                              <ExternalLink className="w-3 h-3 mr-1" />
                              Details
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Dependencies Tab */}
          {activeTab === 'dependencies' && (
            <div className="card">
              <h3 className="text-lg font-semibold mb-4">Dependencies</h3>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="border-b border-dark-700">
                    <tr className="text-left text-sm text-dark-300">
                      <th className="pb-2">Package</th>
                      <th className="pb-2">Version</th>
                      <th className="pb-2">Type</th>
                      <th className="pb-2">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {scanResult.dependencies.map((dep, idx) => {
                      const isOutdated = scanResult.outdated_packages?.some(o => o.name === dep.name)
                      return (
                        <tr key={idx} className="border-b border-dark-700/50">
                          <td className="py-3 font-mono text-sm">{dep.name}</td>
                          <td className="py-3 text-sm">{dep.version}</td>
                          <td className="py-3 text-sm capitalize">{dep.type}</td>
                          <td className="py-3">
                            {isOutdated ? (
                              <span className="text-xs text-yellow-400 flex items-center">
                                <AlertCircle className="w-3 h-3 mr-1" />
                                Outdated
                              </span>
                            ) : (
                              <span className="text-xs text-green-400 flex items-center">
                                <CheckCircle className="w-3 h-3 mr-1" />
                                Up to date
                              </span>
                            )}
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Secrets Tab */}
          {activeTab === 'secrets' && (
            <div className="card">
              <h3 className="text-lg font-semibold mb-4">Hardcoded Secrets</h3>
              {scanResult.secrets_found?.length === 0 ? (
                <div className="text-center text-green-400 py-8">
                  <Shield className="w-12 h-12 mx-auto mb-3" />
                  <p>No hardcoded secrets detected!</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {scanResult.secrets_found?.map((secret, idx) => (
                    <div key={idx} className="border border-red-500/20 bg-red-500/10 rounded-lg p-4">
                      <div className="flex items-start">
                        <Lock className="w-4 h-4 text-red-400 mr-2 mt-0.5" />
                        <div>
                          <div className="flex items-center mb-1">
                            <span className="font-medium">{secret.type}</span>
                            <span className="ml-2 text-xs text-red-400">CRITICAL</span>
                          </div>
                          <p className="text-sm text-dark-300">File: {secret.file}</p>
                          <p className="text-sm text-yellow-400 mt-2">💡 {secret.suggestion}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Unsafe Imports Tab */}
          {activeTab === 'unsafe-imports' && (
            <div className="card">
              <h3 className="text-lg font-semibold mb-4">Unsafe Imports/Functions</h3>
              {scanResult.unsafe_imports?.length === 0 ? (
                <div className="text-center text-green-400 py-8">
                  <CheckCircle className="w-12 h-12 mx-auto mb-3" />
                  <p>No unsafe imports detected!</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {scanResult.unsafe_imports?.map((imp, idx) => (
                    <div key={idx} className="border border-orange-500/20 bg-orange-500/10 rounded-lg p-4">
                      <div className="flex items-start">
                        <AlertCircle className="w-4 h-4 text-orange-400 mr-2 mt-0.5" />
                        <div>
                          <div className="flex items-center mb-1">
                            <span className="font-mono text-sm">{imp.function}</span>
                            <span className="ml-2 text-xs text-orange-400">HIGH</span>
                          </div>
                          <p className="text-sm text-dark-300">File: {imp.file}</p>
                          <p className="text-sm text-yellow-400 mt-2">💡 {imp.suggestion}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Recommendations Tab */}
          {activeTab === 'recommendations' && (
            <div className="card">
              <h3 className="text-lg font-semibold mb-4">Recommendations</h3>
              <div className="space-y-3">
                {scanResult.recommendations?.map((rec, idx) => (
                  <div key={idx} className="border-l-4 border-blue-500 bg-dark-700 p-4 rounded">
                    <div className="flex items-center mb-2">
                      <span className={`text-xs px-2 py-0.5 rounded mr-2 ${
                        rec.priority === 'critical' ? 'bg-red-500/20 text-red-400' :
                        rec.priority === 'high' ? 'bg-orange-500/20 text-orange-400' :
                        rec.priority === 'medium' ? 'bg-yellow-500/20 text-yellow-400' :
                        'bg-green-500/20 text-green-400'
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
        </div>
      )}
    </div>
  )
}