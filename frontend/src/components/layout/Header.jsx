import { Search, Bell, User } from 'lucide-react'

export default function Header() {
  return (
    <header className="h-16 bg-dark-800 border-b border-dark-700 flex items-center justify-between px-6">
      <div className="flex-1 max-w-md">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-dark-400" />
          <input
            type="text"
            placeholder="Search..."
            className="w-full bg-dark-700 text-dark-100 rounded-md pl-10 pr-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>
      <div className="flex items-center space-x-4">
        <Bell className="w-5 h-5 text-dark-300 cursor-pointer hover:text-dark-100" />
        <User className="w-5 h-5 text-dark-300 cursor-pointer hover:text-dark-100" />
      </div>
    </header>
  )
}