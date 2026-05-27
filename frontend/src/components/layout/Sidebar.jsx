import { NavLink } from 'react-router-dom'
import { 
  LayoutDashboard, 
  FolderGit2, 
  Code2, 
  Bug,
  TrendingUp, 
  Shield,
  FileText,
  Search,
  Activity,
  Scissors 
} from 'lucide-react'

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Repository Analysis', href: '/analysis', icon: FolderGit2 },
  { name: 'Code Review', href: '/review', icon: Code2 },
  { name: 'Error Explainer', href: '/explain', icon: Bug },
  { name: 'Bug Prediction', href: '/bug-prediction', icon: TrendingUp }, // Add this
  { name: 'Documentation', href: '/docs', icon: FileText },
  { name: 'Code Search', href: '/search', icon: Search }, 
  { name: 'Health Dashboard', href: '/health', icon: Activity },
  { name: 'Refactor', href: '/refactor', icon: Scissors }, // Add this
]

export default function Sidebar() {
  return (
    <div className="w-64 bg-dark-800 border-r border-dark-700">
      <div className="flex items-center h-16 px-6 border-b border-dark-700">
        <Shield className="w-8 h-8 text-blue-500" />
        <span className="ml-2 text-lg font-semibold">AI Copilot</span>
      </div>
      <nav className="mt-6 px-4">
        {navigation.map((item) => (
          <NavLink
            key={item.name}
            to={item.href}
            className={({ isActive }) =>
              `flex items-center px-4 py-2 mt-2 text-sm rounded-md transition-colors ${
                isActive
                  ? 'bg-dark-700 text-blue-400'
                  : 'text-dark-200 hover:bg-dark-700 hover:text-white'
              }`
            }
          >
            <item.icon className="w-5 h-5 mr-3" />
            {item.name}
          </NavLink>
        ))}
      </nav>
    </div>
  )
}