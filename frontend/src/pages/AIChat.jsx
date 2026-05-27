import { useState, useEffect, useRef } from 'react'
import {
  MessageSquare,
  Send,
  User,
  Bot,
  Loader2,
  Plus,
  Trash2,
  Copy,
  Check
} from 'lucide-react'
import useAppStore from '../store/useAppStore'
import { chatAPI } from '../services/api'
import ReactMarkdown from 'react-markdown'

export default function AIChat() {
  const { currentAnalysis } = useAppStore()
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [conversationId, setConversationId] = useState(null)
  const [suggestions, setSuggestions] = useState([])
  const [copied, setCopied] = useState(false)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => {
    if (currentAnalysis) {
      loadSuggestions()
      startNewConversation()
    }
  }, [currentAnalysis])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const loadSuggestions = async () => {
    try {
      const result = await chatAPI.getSuggestions(currentAnalysis)
      setSuggestions(result.suggestions.slice(0, 5))
    } catch (error) {
      console.error('Failed to load suggestions:', error)
    }
  }

  const startNewConversation = async () => {
    setMessages([])
    setConversationId(null)
    
    // Add welcome message
    setMessages([
      {
        role: 'assistant',
        content: `## 👋 Hello! I'm your AI coding assistant for **${currentAnalysis?.name || 'this repository'}**.

I can help you understand the codebase, explain architecture, debug issues, and suggest improvements.

### What would you like to know?

${suggestions.map(s => `- ${s}`).join('\n')}

Just type your question below! 🚀`,
        timestamp: new Date().toISOString()
      }
    ])
  }

  const handleSend = async () => {
    if (!input.trim() || loading) return
    
    const userMessage = input.trim()
    setInput('')
    
    // Add user message
    setMessages(prev => [...prev, {
      role: 'user',
      content: userMessage,
      timestamp: new Date().toISOString()
    }])
    
    setLoading(true)
    
    try {
      const result = await chatAPI.sendMessage(
        userMessage,
        currentAnalysis,
        conversationId
      )
      
      if (result.success) {
        if (!conversationId) {
          setConversationId(result.conversation_id)
        }
        
        // Add assistant response
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: result.response,
          timestamp: new Date().toISOString()
        }])
        
        // Update suggestions
        if (result.suggested_questions) {
          setSuggestions(result.suggested_questions)
        }
      }
    } catch (error) {
      console.error('Chat failed:', error)
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString(),
        isError: true
      }])
    } finally {
      setLoading(false)
      inputRef.current?.focus()
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleCopyCode = (content) => {
    // Extract code blocks
    const codeMatch = content.match(/```[\s\S]*?```/g)
    if (codeMatch) {
      const code = codeMatch[0].replace(/```\w*\n/g, '').replace(/```/g, '')
      navigator.clipboard.writeText(code)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const formatTime = (timestamp) => {
    const date = new Date(timestamp)
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  if (!currentAnalysis) {
    return (
      <div>
        <h1 className="text-2xl font-semibold mb-6">AI Pair Programmer</h1>
        <div className="card text-center py-12">
          <MessageSquare className="w-16 h-16 text-dark-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium mb-2">No Repository Analyzed</h3>
          <p className="text-dark-300">
            First analyze a repository to chat with AI about it
          </p>
        </div>
      </div>
    )
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-semibold">AI Pair Programmer</h1>
        <button
          onClick={startNewConversation}
          className="btn-secondary flex items-center text-sm"
        >
          <Plus className="w-4 h-4 mr-2" />
          New Chat
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Chat Area */}
        <div className="lg:col-span-3">
          <div className="card flex flex-col" style={{ height: '600px' }}>
            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div className={`max-w-[80%] ${msg.role === 'user' ? 'order-2' : 'order-1'}`}>
                    <div className="flex items-center mb-1">
                      {msg.role === 'assistant' ? (
                        <Bot className="w-4 h-4 text-blue-400 mr-1" />
                      ) : (
                        <User className="w-4 h-4 text-green-400 mr-1" />
                      )}
                      <span className="text-xs text-dark-400">
                        {msg.role === 'assistant' ? 'AI Assistant' : 'You'} • {formatTime(msg.timestamp)}
                      </span>
                    </div>
                    <div className={`rounded-lg p-3 ${
                      msg.role === 'user' 
                        ? 'bg-blue-600 text-white' 
                        : msg.isError 
                          ? 'bg-red-500/20 border border-red-500/20'
                          : 'bg-dark-700'
                    }`}>
                      {msg.role === 'assistant' ? (
                        <div className="prose prose-invert prose-sm max-w-none">
                          <ReactMarkdown
                            components={{
                              code({ node, inline, className, children, ...props }) {
                                return inline ? (
                                  <code className="bg-dark-800 px-1 rounded" {...props}>
                                    {children}
                                  </code>
                                ) : (
                                  <div className="relative">
                                    <pre className="bg-dark-900 rounded p-3 overflow-x-auto">
                                      <code {...props}>{children}</code>
                                    </pre>
                                    <button
                                      onClick={() => handleCopyCode(String(children))}
                                      className="absolute top-2 right-2 text-dark-400 hover:text-dark-200"
                                    >
                                      <Copy className="w-4 h-4" />
                                    </button>
                                  </div>
                                )
                              }
                            }}
                          >
                            {msg.content}
                          </ReactMarkdown>
                        </div>
                      ) : (
                        <p className="whitespace-pre-wrap">{msg.content}</p>
                      )}
                    </div>
                  </div>
                </div>
              ))}
              
              {loading && (
                <div className="flex justify-start">
                  <div className="bg-dark-700 rounded-lg p-3">
                    <Loader2 className="w-5 h-5 animate-spin text-blue-400" />
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="border-t border-dark-700 p-4">
              <div className="flex space-x-2">
                <textarea
                  ref={inputRef}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask me anything about this codebase..."
                  rows={2}
                  className="flex-1 bg-dark-700 rounded-md p-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                />
                <button
                  onClick={handleSend}
                  disabled={!input.trim() || loading}
                  className="btn-primary px-4 flex items-center justify-center"
                >
                  {loading ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Send className="w-4 h-4" />
                  )}
                </button>
              </div>
              <p className="text-xs text-dark-400 mt-2">
                Press Enter to send, Shift+Enter for new line
              </p>
            </div>
          </div>
        </div>

        {/* Suggestions Panel */}
        <div className="card">
          <h3 className="text-sm font-medium mb-3">Suggested Questions</h3>
          <div className="space-y-2">
            {suggestions.map((suggestion, idx) => (
              <button
                key={idx}
                onClick={() => setInput(suggestion)}
                className="w-full text-left text-sm p-2 bg-dark-700 rounded-md hover:bg-dark-600 transition-colors"
              >
                {suggestion}
              </button>
            ))}
          </div>

          <div className="border-t border-dark-700 mt-4 pt-4">
            <h3 className="text-sm font-medium mb-2">What I Can Help With</h3>
            <div className="space-y-1 text-xs text-dark-300">
              <p>📐 Explain architecture</p>
              <p>🔍 Explain functions and code</p>
              <p>🐛 Debug errors and issues</p>
              <p>✨ Suggest best practices</p>
              <p>📦 Explain dependencies</p>
              <p>📝 Review code snippets</p>
              <p>🔄 Suggest refactoring</p>
            </div>
          </div>

          <div className="border-t border-dark-700 mt-4 pt-4">
            <h3 className="text-sm font-medium mb-2">About Current Repository</h3>
            <div className="text-xs text-dark-300 space-y-1">
              <p>📁 {currentAnalysis?.name || 'Unknown'}</p>
              <p>📄 {currentAnalysis?.files_count || 0} files</p>
              <p>🔧 Complexity: {currentAnalysis?.complexity_score || 'N/A'}/10</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}