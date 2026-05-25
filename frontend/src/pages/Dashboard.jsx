import { Activity, GitBranch, AlertCircle, CheckCircle } from 'lucide-react'

export default function Dashboard() {
  const stats = [
    { label: 'Projects Analyzed', value: '0', icon: GitBranch, color: 'text-blue-500' },
    { label: 'Code Reviews', value: '0', icon: Activity, color: 'text-green-500' },
    { label: 'Issues Found', value: '0', icon: AlertCircle, color: 'text-red-500' },
    { label: 'Quality Score', value: 'N/A', icon: CheckCircle, color: 'text-purple-500' },
  ]

  return (
    <div>
      <h1 className="text-2xl font-semibold mb-6">Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {stats.map((stat) => (
          <div key={stat.label} className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-dark-300 text-sm">{stat.label}</p>
                <p className="text-2xl font-semibold mt-1">{stat.value}</p>
              </div>
              <stat.icon className={`w-8 h-8 ${stat.color}`} />
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-lg font-semibold mb-4">Recent Activity</h2>
          <div className="text-center text-dark-400 py-8">
            No activity yet. Start by analyzing a repository.
          </div>
        </div>
        
        <div className="card">
          <h2 className="text-lg font-semibold mb-4">Quick Actions</h2>
          <div className="space-y-3">
            <button className="w-full text-left px-4 py-3 bg-dark-700 rounded-md hover:bg-dark-600 transition-colors">
              📁 Upload Repository
            </button>
            <button className="w-full text-left px-4 py-3 bg-dark-700 rounded-md hover:bg-dark-600 transition-colors">
              🔍 Review Code
            </button>
            <button className="w-full text-left px-4 py-3 bg-dark-700 rounded-md hover:bg-dark-600 transition-colors">
              ❌ Explain Error
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}