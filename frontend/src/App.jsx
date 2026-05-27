import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './components/layout/Layout'
import ErrorBoundary from './components/common/ErrorBoundary'

// Lazy load pages for better performance
import { lazy, Suspense } from 'react'
import LoadingSpinner from './components/common/LoadingSpinner'

const Landing = lazy(() => import('./pages/Landing'))
const Dashboard = lazy(() => import('./pages/Dashboard'))
const RepositoryAnalysis = lazy(() => import('./pages/RepositoryAnalysis'))
const CodeReview = lazy(() => import('./pages/CodeReview'))
const ErrorExplainer = lazy(() => import('./pages/ErrorExplainer'))
const BugPrediction = lazy(() => import('./pages/BugPrediction'))
const Documentation = lazy(() => import('./pages/Documentation'))
const CodeSearch = lazy(() => import('./pages/CodeSearch'))
const HealthDashboard = lazy(() => import('./pages/HealthDashboard'))
const RefactorSuggestions = lazy(() => import('./pages/RefactorSuggestions'))
const DependencyScanner = lazy(() => import('./pages/DependencyScanner'))
const CommitGenerator = lazy(() => import('./pages/CommitGenerator'))
const PRReviewAssistant = lazy(() => import('./pages/PRReviewAssistant'))
const TestGenerator = lazy(() => import('./pages/TestGenerator'))
const DependencyGraph = lazy(() => import('./pages/DependencyGraph'))
const AIChat = lazy(() => import('./pages/AIChat'))

function App() {
  return (
    <ErrorBoundary>
      <Router>
        <Layout>
          <Suspense fallback={<LoadingSpinner text="Loading..." />}>
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
              <Route path="/test-generator" element={<TestGenerator />} />
              <Route path="/dependency-graph" element={<DependencyGraph />} />
              <Route path="/chat" element={<AIChat />} />
            </Routes>
          </Suspense>
        </Layout>
      </Router>
    </ErrorBoundary>
  )
}

export default App