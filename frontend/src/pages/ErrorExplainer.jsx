import { useState } from 'react'

export default function ErrorExplainer() {
  const [error, setError] = useState('')

  return (
    <div>
      <h1 className="text-2xl font-semibold mb-6">Error Explainer</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-lg font-semibold mb-4">Paste Error Message</h2>
          <textarea
            value={error}
            onChange={(e) => setError(e.target.value)}
            placeholder="Paste your error message or stack trace here..."
            rows={10}
            className="w-full bg-dark-700 rounded-md p-3 font-mono text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button className="mt-4 btn-primary w-full">
            Explain Error
          </button>
        </div>

        <div className="card">
          <h2 className="text-lg font-semibold mb-4">Explanation</h2>
          <div className="text-center text-dark-400 py-8">
            Error explanation will appear here
          </div>
        </div>
      </div>
    </div>
  )
}