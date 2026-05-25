import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './components/layout/Layout'
import Landing from './pages/Landing'
import Dashboard from './pages/Dashboard'
import RepositoryAnalysis from './pages/RepositoryAnalysis'
import CodeReview from './pages/CodeReview'
import ErrorExplainer from './pages/ErrorExplainer'

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/analysis" element={<RepositoryAnalysis />} />
          <Route path="/review" element={<CodeReview />} />
          <Route path="/explain" element={<ErrorExplainer />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App