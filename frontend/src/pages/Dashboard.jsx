import { useState, useEffect } from 'react'
import { 
  Activity, 
  GitBranch, 
  AlertCircle, 
  CheckCircle, 
  TrendingUp, 
  Code, 
  Bug, 
  FileText, 
  Shield, 
  GitPullRequest,
  FolderGit2
} from 'lucide-react'
import useAppStore from '../store/useAppStore'
import { Link } from 'react-router-dom'

export default function Dashboard() {
  const { currentAnalysis, analysesHistory } = useAppStore()
  const [stats, setStats] = useState({
    projectsAnalyzed: 0,
    codeReviews: 0,
    issuesFound: 0,
    qualityScore: 0,
    vulnerabilitiesFound: 0,
    testCasesGenerated: 0
  })
  const [recentActivity, setRecentActivity] = useState([])

  useEffect(() => {
    // Load stats from localStorage or store
    const savedHistory = localStorage.getItem('analysisHistory')
    const history = savedHistory ? JSON.parse(savedHistory) : []
    
    const savedReviews = localStorage.getItem('codeReviews')
    const reviews = savedReviews ? JSON.parse(savedReviews) : []
    
    const savedIssues = localStorage.getItem('issuesFound')
    const issues = savedIssues ? JSON.parse(savedIssues) : []
    
    // Calculate stats
    const projectsCount = history.length + (currentAnalysis ? 1 : 0)
    const reviewsCount = reviews.length
    const totalIssues = issues.length
    
    // Calculate average quality score
    let avgQuality = 65
    if (currentAnalysis) {
      const complexity = currentAnalysis.complexity_score || 5
      avgQuality = Math.round(100 - (complexity * 8))
    }
    
    setStats({
      projectsAnalyzed: projectsCount,
      codeReviews: reviewsCount,
      issuesFound: totalIssues,
      qualityScore: avgQuality,
      vulnerabilitiesFound: Math.floor(totalIssues * 0.3),
      testCasesGenerated: 0
    })
    
    // Build recent activity
    const activities = []
    
    if (currentAnalysis) {
      activities.push({
        id: Date.now(),
        type: 'analysis',
        title: 'Repository Analyzed',
        description: `${currentAnalysis.name} - ${currentAnalysis.files_count} files analyzed`,
        time: 'Just now',
        icon: GitBranch,
        color: 'blue'
      })
    }
    
    if (reviews.length > 0) {
      const lastReview = reviews[reviews.length - 1]
      activities.push({
        id: lastReview.id || Date.now(),
        type: 'review',
        title: 'Code Review Completed',
        description: `Found ${lastReview.issuesCount || 0} issues`,
        time: lastReview.time || 'Recently',
        icon: Code,
        color: 'green'
      })
    }
    
    if (issues.length > 0) {
      const criticalIssues = issues.filter(i => i.severity === 'high').length
      activities.push({
        id: Date.now() + 1,
        type: 'issues',
        title: 'Issues Detected',
        description: `${criticalIssues} critical issues found`,
        time: 'Recent',
        icon: Bug,
        color: 'red'
      })
    }
    
    setRecentActivity(activities.slice(0, 5))
  }, [currentAnalysis])

  // Listen for storage events to update across tabs
  useEffect(() => {
    const handleStorageChange = () => {
      const savedHistory = localStorage.getItem('analysisHistory')
      const history = savedHistory ? JSON.parse(savedHistory) : []
      setStats(prev => ({ ...prev, projectsAnalyzed: history.length + (currentAnalysis ? 1 : 0) }))
    }
    
    window.addEventListener('storage', handleStorageChange)
    return () => window.removeEventListener('storage', handleStorageChange)
  }, [currentAnalysis])

  const statCards = [
    { 
      label: 'Projects Analyzed', 
      value: stats.projectsAnalyzed, 
      icon: GitBranch, 
      color: 'text-blue-400',
      bgColor: 'bg-blue-500/10',
      link: '/analysis'
    },
    { 
      label: 'Code Reviews', 
      value: stats.codeReviews, 
      icon: Code, 
      color: 'text-green-400',
      bgColor: 'bg-green-500/10',
      link: '/review'
    },
    { 
      label: 'Issues Found', 
      value: stats.issuesFound, 
      icon: AlertCircle, 
      color: 'text-red-400',
      bgColor: 'bg-red-500/10',
      link: '/review'
    },
    { 
      label: 'Quality Score', 
      value: stats.qualityScore + '%', 
      icon: CheckCircle, 
      color: 'text-purple-400',
      bgColor: 'bg-purple-500/10',
      link: '/health'
    },
    { 
      label: 'Vulnerabilities', 
      value: stats.vulnerabilitiesFound, 
      icon: Shield, 
      color: 'text-yellow-400',
      bgColor: 'bg-yellow-500/10',
      link: '/security'
    },
    { 
      label: 'Test Cases', 
      value: stats.testCasesGenerated, 
      icon: Activity, 
      color: 'text-cyan-400',
      bgColor: 'bg-cyan-500/10',
      link: '/test-generator'
    },
  ]

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-semibold">Dashboard</h1>
        <div className="text-sm text-dark-400">
          Last updated: {new Date().toLocaleTimeString()}
        </div>
      </div>
      
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        {statCards.map((stat) => (
          <Link to={stat.link} key={stat.label}>
            <div className="card hover:border-blue-500/50 transition-all duration-200 cursor-pointer group">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-dark-300 text-sm">{stat.label}</p>
                  <p className="text-2xl font-bold mt-1">{stat.value}</p>
                </div>
                <div className={`${stat.bgColor} p-3 rounded-lg group-hover:scale-110 transition-transform duration-200`}>
                  <stat.icon className={`w-5 h-5 ${stat.color}`} />
                </div>
              </div>
            </div>
          </Link>
        ))}
      </div>

      {/* Current Project Section */}
      {currentAnalysis && (
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Current Project</h2>
            <Link to="/analysis" className="text-sm text-blue-400 hover:text-blue-300">
              View Details →
            </Link>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-dark-300 text-sm">Project Name</p>
              <p className="font-mono text-lg font-semibold">{currentAnalysis.name || 'Unknown'}</p>
            </div>
            <div>
              <p className="text-dark-300 text-sm">Files Analyzed</p>
              <p className="text-lg font-semibold">{currentAnalysis.files_count || 0}</p>
            </div>
            <div>
              <p className="text-dark-300 text-sm">Total Lines</p>
              <p className="text-lg font-semibold">{currentAnalysis.total_lines?.toLocaleString() || 0}</p>
            </div>
            <div>
              <p className="text-dark-300 text-sm">Complexity Score</p>
              <div className="flex items-center space-x-2">
                <span className="text-lg font-semibold">{currentAnalysis.complexity_score || 0}/10</span>
                <div className="flex-1 bg-dark-700 rounded-full h-2">
                  <div 
                    className={`rounded-full h-2 transition-all ${
                      (currentAnalysis.complexity_score || 0) <= 3 ? 'bg-green-500' :
                      (currentAnalysis.complexity_score || 0) <= 6 ? 'bg-yellow-500' : 'bg-red-500'
                    }`}
                    style={{ width: `${((currentAnalysis.complexity_score || 0) / 10) * 100}%` }}
                  />
                </div>
              </div>
            </div>
          </div>
          
          {/* Languages */}
          {currentAnalysis.languages && Object.keys(currentAnalysis.languages).length > 0 && (
            <div className="mt-4 pt-4 border-t border-dark-700">
              <p className="text-dark-300 text-sm mb-2">Languages</p>
              <div className="flex flex-wrap gap-2">
                {Object.entries(currentAnalysis.languages).slice(0, 5).map(([lang, count]) => (
                  <span key={lang} className="px-2 py-1 bg-dark-700 rounded-md text-xs">
                    {lang}: {count} files
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-lg font-semibold mb-4">Recent Activity</h2>
          {recentActivity.length === 0 ? (
            <div className="text-center text-dark-400 py-8">
              <Activity className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>No activity yet</p>
              <p className="text-sm mt-2">Analyze a repository to see activity</p>
              <Link to="/analysis" className="mt-4 inline-block btn-primary text-sm">
                Start Analysis
              </Link>
            </div>
          ) : (
            <div className="space-y-3">
              {recentActivity.map((activity) => (
                <div key={activity.id} className="flex items-start space-x-3 p-3 bg-dark-700/50 rounded-lg hover:bg-dark-700 transition-colors">
                  <div className={`p-2 rounded-lg bg-${activity.color}-500/10`}>
                    <activity.icon className={`w-4 h-4 text-${activity.color}-400`} />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium">{activity.title}</p>
                    <p className="text-xs text-dark-400">{activity.description}</p>
                    <p className="text-xs text-dark-500 mt-1">{activity.time}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Quick Actions */}
        <div className="card">
          <h2 className="text-lg font-semibold mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <Link to="/analysis" className="p-3 bg-dark-700 rounded-lg hover:bg-dark-600 transition-all text-left group">
              <FolderGit2 className="w-5 h-5 text-blue-400 mb-2 group-hover:scale-110 transition-transform" />
              <p className="font-medium text-sm">Analyze Repository</p>
              <p className="text-xs text-dark-400 mt-1">Upload or connect GitHub repo</p>
            </Link>
            <Link to="/review" className="p-3 bg-dark-700 rounded-lg hover:bg-dark-600 transition-all text-left group">
              <Code className="w-5 h-5 text-green-400 mb-2 group-hover:scale-110 transition-transform" />
              <p className="font-medium text-sm">Code Review</p>
              <p className="text-xs text-dark-400 mt-1">Review code for issues</p>
            </Link>
            <Link to="/explain" className="p-3 bg-dark-700 rounded-lg hover:bg-dark-600 transition-all text-left group">
              <Bug className="w-5 h-5 text-red-400 mb-2 group-hover:scale-110 transition-transform" />
              <p className="font-medium text-sm">Error Explainer</p>
              <p className="text-xs text-dark-400 mt-1">Understand error messages</p>
            </Link>
            <Link to="/security" className="p-3 bg-dark-700 rounded-lg hover:bg-dark-600 transition-all text-left group">
              <Shield className="w-5 h-5 text-yellow-400 mb-2 group-hover:scale-110 transition-transform" />
              <p className="font-medium text-sm">Security Scan</p>
              <p className="text-xs text-dark-400 mt-1">Check for vulnerabilities</p>
            </Link>
            <Link to="/commit" className="p-3 bg-dark-700 rounded-lg hover:bg-dark-600 transition-all text-left group">
              <GitBranch className="w-5 h-5 text-purple-400 mb-2 group-hover:scale-110 transition-transform" />
              <p className="font-medium text-sm">Generate Commit</p>
              <p className="text-xs text-dark-400 mt-1">AI-powered commit messages</p>
            </Link>
            <Link to="/pr-review" className="p-3 bg-dark-700 rounded-lg hover:bg-dark-600 transition-all text-left group">
              <GitPullRequest className="w-5 h-5 text-cyan-400 mb-2 group-hover:scale-110 transition-transform" />
              <p className="font-medium text-sm">PR Review</p>
              <p className="text-xs text-dark-400 mt-1">Review pull requests</p>
            </Link>
          </div>
        </div>
      </div>

      {/* Insights Section */}
      {currentAnalysis && (
        <div className="card bg-gradient-to-r from-blue-500/10 to-purple-500/10">
          <div className="flex items-start">
            <TrendingUp className="w-6 h-6 text-blue-400 mr-3 flex-shrink-0 mt-1" />
            <div>
              <h3 className="text-lg font-semibold mb-2">AI Insight</h3>
              <p className="text-sm text-dark-300">
                Based on your codebase analysis, {currentAnalysis.name} has {
                  (currentAnalysis.complexity_score || 0) <= 3 ? 'excellent' :
                  (currentAnalysis.complexity_score || 0) <= 6 ? 'moderate' : 'high'
                } complexity.
                {
                  (currentAnalysis.complexity_score || 0) > 6 ? 
                  ' Consider refactoring complex modules to improve maintainability.' :
                  ' Keep up the good work!'
                }
              </p>
              <Link to="/health" className="inline-block mt-3 text-sm text-blue-400 hover:text-blue-300">
                View detailed health report →
              </Link>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}