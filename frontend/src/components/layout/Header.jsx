import { useState } from 'react'
import { Search, Bell, Zap } from 'lucide-react'

export default function Header() {
  const [searchFocused, setSearchFocused] = useState(false)
  const [showNotifications, setShowNotifications] = useState(false)
  
  const notifications = [
    { id: 1, title: 'Analysis Complete', message: 'Repository analysis finished', time: '2 min ago', read: false },
    { id: 2, title: 'Issues Found', message: '12 code issues detected', time: '1 hour ago', read: false },
  ]

  return (
    <header className="h-16 bg-dark-800 border-b border-dark-700 flex items-center justify-between px-6">
      {/* Search Bar */}
      <div className="flex-1 max-w-md">
        <div className={`relative transition-all duration-200 ${searchFocused ? 'scale-105' : ''}`}>
          <Search className={`absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 transition-colors ${searchFocused ? 'text-blue-400' : 'text-dark-400'}`} />
          <input
            type="text"
            placeholder="Search files, functions, or commands... (Ctrl+K)"
            onFocus={() => setSearchFocused(true)}
            onBlur={() => setSearchFocused(false)}
            className="w-full bg-dark-700 rounded-lg pl-10 pr-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
          />
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
            <kbd className="hidden sm:inline-block px-1.5 py-0.5 text-xs font-mono text-dark-400 bg-dark-600 rounded">⌘K</kbd>
          </div>
        </div>
      </div>
      
      {/* Right side actions */}
      <div className="flex items-center space-x-3">
        {/* AI Status Badge */}
        <div className="hidden sm:flex items-center space-x-2 px-3 py-1.5 bg-gradient-to-r from-blue-500/10 to-purple-500/10 rounded-full">
          <Zap className="w-3 h-3 text-yellow-400" />
          <span className="text-xs text-dark-300">AI Ready</span>
          <div className="w-1.5 h-1.5 bg-green-400 rounded-full animate-pulse"></div>
        </div>
        
        {/* Notifications */}
        <div className="relative">
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            className="relative p-2 rounded-lg hover:bg-dark-700 transition-colors"
          >
            <Bell className="w-5 h-5 text-dark-300" />
            {notifications.filter(n => !n.read).length > 0 && (
              <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full animate-pulse"></span>
            )}
          </button>
          
          {showNotifications && (
            <div className="absolute right-0 mt-2 w-80 bg-dark-800 border border-dark-700 rounded-lg shadow-xl z-50 animate-fade-in">
              <div className="p-3 border-b border-dark-700">
                <h3 className="font-semibold">Notifications</h3>
              </div>
              <div className="max-h-96 overflow-y-auto">
                {notifications.map(notif => (
                  <div key={notif.id} className={`p-3 hover:bg-dark-700 cursor-pointer transition-colors ${!notif.read ? 'bg-blue-500/5' : ''}`}>
                    <p className="text-sm font-medium">{notif.title}</p>
                    <p className="text-xs text-dark-400 mt-1">{notif.message}</p>
                    <p className="text-xs text-dark-500 mt-1">{notif.time}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
        
        {/* Version */}
        <div className="hidden lg:block text-xs text-dark-500">
          v1.0.0
        </div>
      </div>
    </header>
  )
}