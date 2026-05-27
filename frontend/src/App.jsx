import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './components/layout/Layout'
import Landing from './pages/Landing'
import Dashboard from './pages/Dashboard'
import RepositoryAnalysis from './pages/RepositoryAnalysis'
import CodeReview from './pages/CodeReview'
import ErrorExplainer from './pages/ErrorExplainer'
import BugPrediction from './pages/BugPrediction'
import Documentation from './pages/Documentation'
import CodeSearch from './pages/CodeSearch'
import HealthDashboard from './pages/HealthDashboard'
import RefactorSuggestions from './pages/RefactorSuggestions'
import DependencyScanner from './pages/DependencyScanner'
import CommitGenerator from './pages/CommitGenerator'
import PRReviewAssistant from './pages/PRReviewAssistant'

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
          <Route path="/bug-prediction" element={<BugPrediction />} />
          <Route path="/docs" element={<Documentation />} />
          <Route path="/search" element={<CodeSearch />} />
          <Route path="/health" element={<HealthDashboard />} />
          <Route path="/refactor" element={<RefactorSuggestions />} />
          <Route path="/security" element={<DependencyScanner />} />
          <Route path="/commit" element={<CommitGenerator />} />
          <Route path="/pr-review" element={<PRReviewAssistant />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App