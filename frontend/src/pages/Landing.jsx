import { Link } from 'react-router-dom'
import { Code2, Shield, Zap, GitBranch } from 'lucide-react'

export default function Landing() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-dark-900 to-dark-800">
      <div className="max-w-7xl mx-auto px-6 py-20">
        <div className="text-center">
          <h1 className="text-5xl font-bold mb-4">
            AI-Powered Engineering
            <span className="text-blue-500"> Productivity</span>
          </h1>
          <p className="text-xl text-dark-300 mb-8 max-w-2xl mx-auto">
            Analyze repositories, review code, explain errors, and improve code quality with intelligent assistance
          </p>
          <Link
            to="/dashboard"
            className="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            Get Started
            <Zap className="ml-2 w-5 h-5" />
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-20">
          <div className="card">
            <Code2 className="w-12 h-12 text-blue-500 mb-4" />
            <h3 className="text-lg font-semibold mb-2">Smart Code Review</h3>
            <p className="text-dark-300">Get senior-level code reviews with actionable insights</p>
          </div>
          <div className="card">
            <GitBranch className="w-12 h-12 text-blue-500 mb-4" />
            <h3 className="text-lg font-semibold mb-2">Repo Analysis</h3>
            <p className="text-dark-300">Understand any codebase structure and complexity</p>
          </div>
          <div className="card">
            <Shield className="w-12 h-12 text-blue-500 mb-4" />
            <h3 className="text-lg font-semibold mb-2">Error Explanations</h3>
            <p className="text-dark-300">Get clear, educational error explanations and fixes</p>
          </div>
        </div>
      </div>
    </div>
  )
}