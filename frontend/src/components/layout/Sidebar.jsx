import { NavLink } from 'react-router-dom'
import { 
  LayoutDashboard, 
  FolderGit2, 
  Code2, 
  Bug, 
  TrendingUp,
  FileText,
  Search,
  Activity,
  Scissors,
  Shield,
  GitBranch,
  GitPullRequest,
  TestTube,
  MessageSquare
} from 'lucide-react'
import { useState } from 'react'

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Repository Analysis', href: '/analysis', icon: FolderGit2 },
  { name: 'Code Review', href: '/review', icon: Code2 },
  { name: 'Error Explainer', href: '/explain', icon: Bug },
  { name: 'Bug Prediction', href: '/bug-prediction', icon: TrendingUp },
  { name: 'Documentation', href: '/docs', icon: FileText },
  { name: 'Code Search', href: '/search', icon: Search },
  { name: 'Health Dashboard', href: '/health', icon: Activity },
  { name: 'Refactor', href: '/refactor', icon: Scissors },
  { name: 'Security Scanner', href: '/security', icon: Shield },
  { name: 'Commit Generator', href: '/commit', icon: GitBranch },
  { name: 'PR Review', href: '/pr-review', icon: GitPullRequest },
  { name: 'Test Generator', href: '/test-generator', icon: TestTube },
  { name: 'AI Chat', href: '/chat', icon: MessageSquare },
]

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false)

  return (
    <div className={`${collapsed ? 'w-20' : 'w-64'} bg-dark-800 border-r border-dark-700 transition-all duration-300 flex flex-col`}>
      <div className={`flex items-center ${collapsed ? 'justify-center' : 'justify-between'} h-16 px-4 border-b border-dark-700`}>
        {!collapsed && (
          <div className="flex items-center">
            <Code2 className="w-8 h-8 text-blue-500" />
            <span className="ml-2 text-lg font-semibold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              AI Copilot
            </span>
          </div>
        )}
        {collapsed && (
          <Code2 className="w-8 h-8 text-blue-500" />
        )}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="text-dark-400 hover:text-dark-200 transition-colors"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={collapsed ? "M13 5l7 7-7 7M5 5l7 7-7 7" : "M11 19l-7-7 7-7M19 19l-7-7 7-7"} />
          </svg>
        </button>
      </div>
      
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {navigation.map((item) => (
          <NavLink
            key={item.name}
            to={item.href}
            className={({ isActive }) =>
              `flex items-center ${collapsed ? 'justify-center' : 'px-3'} py-2.5 rounded-lg transition-all duration-200 group ${
                isActive
                  ? 'bg-gradient-to-r from-blue-500/20 to-purple-500/20 text-blue-400 border border-blue-500/20'
                  : 'text-dark-300 hover:bg-dark-700 hover:text-white'
              }`
            }
            title={collapsed ? item.name : ''}
          >
            <item.icon className={`w-5 h-5 ${collapsed ? '' : 'mr-3'} transition-transform group-hover:scale-105`} />
            {!collapsed && <span className="text-sm">{item.name}</span>}
          </NavLink>
        ))}
      </nav>
      
      <div className="p-4 border-t border-dark-700">
        <div className={`${collapsed ? 'text-center' : 'flex items-center'} p-3 bg-gradient-to-r from-blue-500/10 to-purple-500/10 rounded-lg`}>
          {!collapsed ? (
            <>
              <div className="flex-1">
                <p className="text-xs text-dark-400">AI Engine</p>
                <p className="text-xs font-medium text-green-400">● Active</p>
              </div>
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            </>
          ) : (
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse mx-auto"></div>
          )}
        </div>
      </div>
    </div>
  )
}