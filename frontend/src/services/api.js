import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds timeout for large file uploads
});

// Request interceptor for logging (development only)
api.interceptors.request.use(
  (config) => {
    if (import.meta.env.DEV) {
      console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`);
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response) {
      // Server responded with error status
      const errorMessage = error.response.data?.detail || error.response.data?.message || 'An error occurred';
      console.error(`[API Error] ${error.response.status}: ${errorMessage}`);
      
      // Handle specific status codes
      switch (error.response.status) {
        case 400:
          throw new Error(errorMessage || 'Bad request');
        case 401:
          throw new Error('Unauthorized. Please check your credentials.');
        case 403:
          throw new Error('Forbidden. You don\'t have permission to access this resource.');
        case 404:
          throw new Error('Resource not found');
        case 413:
          throw new Error('File too large. Please upload a smaller file.');
        case 429:
          throw new Error('Too many requests. Please try again later.');
        case 500:
          throw new Error('Server error. Please try again later.');
        default:
          throw new Error(errorMessage || 'Request failed');
      }
    } else if (error.request) {
      // Request was made but no response received
      console.error('[API Error] No response received:', error.request);
      throw new Error('Unable to connect to server. Please check if the backend is running.');
    } else {
      // Something else happened
      console.error('[API Error]', error.message);
      throw new Error(error.message || 'Request failed');
    }
  }
);

// ==================== REPOSITORY ANALYSIS API ====================
export const analysisAPI = {
  /**
   * Upload and analyze a ZIP file containing a repository
   * @param {File} file - ZIP file to upload
   * @returns {Promise} Analysis results
   */
  uploadZip: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/api/analysis/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total) {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          console.log(`Upload progress: ${percentCompleted}%`);
        }
      },
    });
    return response.data;
  },
  
  /**
   * Analyze a GitHub repository by URL
   * @param {string} repoUrl - Full GitHub repository URL
   * @returns {Promise} Analysis results
   */
  analyzeGithub: async (repoUrl) => {
    const response = await api.post('/api/analysis/github', { repo_url: repoUrl });
    return response.data;
  },
  
  /**
   * Get analysis status for long-running tasks
   * @param {string} taskId - Task ID from initial analysis request
   * @returns {Promise} Task status and results if completed
   */
  getAnalysisStatus: async (taskId) => {
    const response = await api.get(`/api/analysis/status/${taskId}`);
    return response.data;
  }
};

// ==================== CODE REVIEW API ====================
export const reviewAPI = {
  /**
   * Review code for issues, bugs, and improvements
   * @param {string} code - Source code to review
   * @param {string} language - Programming language (python, javascript, typescript)
   * @returns {Promise} Review results with issues and suggestions
   */
  reviewCode: async (code, language = 'python') => {
    const response = await api.post('/api/review/', { 
      code, 
      language 
    });
    return response.data;
  },
  
  /**
   * Get detailed analysis for a specific issue
   * @param {string} ruleId - Rule ID from review results
   * @returns {Promise} Detailed rule information
   */
  getRuleDetails: async (ruleId) => {
    const response = await api.get(`/api/review/rules/${ruleId}`);
    return response.data;
  },
  
  /**
   * Get metrics for code quality over time (for dashboard)
   * @param {string} repoId - Repository identifier
   * @returns {Promise} Historical metrics data
   */
  getQualityMetrics: async (repoId) => {
    const response = await api.get(`/api/review/metrics/${repoId}`);
    return response.data;
  }
};

// ==================== ERROR EXPLAINER API ====================
export const errorAPI = {
  /**
   * Explain an error message and provide fixes
   * @param {string} errorMessage - The error message or stack trace
   * @param {string} language - Programming language context
   * @param {string} context - Additional context (framework, environment)
   * @returns {Promise} Error explanation with causes and fixes
   */
  explainError: async (errorMessage, language = 'python', context = null) => {
    const response = await api.post('/api/error/explain', {
      error_message: errorMessage,
      language: language,
      context: context
    });
    return response.data;
  },
  
  /**
   * Get common errors and solutions for a language/framework
   * @param {string} language - Programming language
   * @param {string} framework - Optional framework name
   * @returns {Promise} Common error patterns and solutions
   */
  getCommonErrors: async (language, framework = null) => {
    const response = await api.get('/api/error/common', {
      params: { language, framework }
    });
    return response.data;
  }
};

// ==================== BUG PREDICTION API (Phase 5) ====================
export const bugPredictionAPI = {
  /**
   * Predict risky files in a repository
   * @param {string} repoId - Repository identifier
   * @param {Array} filesData - Files data for analysis
   * @returns {Promise} Risk analysis and predictions
   */
  predictRisks: async (repoId, filesData) => {
    const response = await api.post('/api/bug-prediction/analyze', { 
      repo_id: repoId, 
      files_data: filesData 
    });
    return response.data;
  },
  
  /**
   * Get maintainability score for a file
   * @param {string} filePath - Path to file
   * @param {Object} fileMetrics - File metrics
   * @returns {Promise} Maintainability metrics
   */
  getMaintainabilityScore: async (filePath, fileMetrics) => {
    const response = await api.post('/api/bug-prediction/predict-file', {
      file_path: filePath,
      file_metrics: fileMetrics
    });
    return response.data;
  }
};

// ==================== DOCUMENTATION API (Phase 6) ====================
export const docsAPI = {
  /**
   * Generate README for a repository
   * @param {Object} repoAnalysis - Repository analysis data
   * @returns {Promise} Generated README content
   */
  generateReadme: async (repoAnalysis) => {
    const response = await api.post('/api/docs/generate-readme', { 
      repo_analysis: repoAnalysis 
    });
    return response.data;
  },
  
  /**
   * Generate API documentation from code
   * @param {string} code - Source code
   * @param {string} language - Programming language
   * @returns {Promise} Generated documentation
   */
  generateApiDocs: async (code, language) => {
    const response = await api.post('/api/docs/generate-api-docs', { 
      code, 
      language 
    });
    return response.data;
  },
  
  /**
   * Summarize a code file
   * @param {string} code - Source code
   * @param {string} filePath - Path to the file
   * @returns {Promise} Code summary
   */
  summarizeCode: async (code, filePath) => {
    const response = await api.post('/api/docs/summarize-code', {
      code,
      file_path: filePath
    });
    return response.data;
  }
};

// ==================== CODE SEARCH API (Phase 7) ====================
export const searchAPI = {
  /**
   * Index a repository for searching
   * @param {Object} repositoryData - Repository analysis data
   * @returns {Promise} Indexing result
   */
  indexRepository: async (repositoryData) => {
    const response = await api.post('/api/search/index', { 
      repository_data: repositoryData 
    });
    return response.data;
  },
  
  /**
   * Search code semantically using natural language
   * @param {string} query - Natural language search query
   * @param {number} maxResults - Maximum number of results
   * @returns {Promise} Search results with relevance scores
   */
  semanticSearch: async (query, maxResults = 20) => {
    const response = await api.post('/api/search/search', { 
      query, 
      max_results: maxResults 
    });
    return response.data;
  },
  
  /**
   * Clear the search index
   * @returns {Promise} Clear result
   */
  clearIndex: async () => {
    const response = await api.post('/api/search/clear-index');
    return response.data;
  }
};

// ==================== HEALTH DASHBOARD API (Phase 8) ====================
// ==================== HEALTH DASHBOARD API (Phase 8) ====================
export const healthAPI = {
  /**
   * Get overall project health metrics
   * @param {Object} repositoryData - Repository analysis data
   * @returns {Promise} Health scores and metrics
   */
  analyzeHealth: async (repositoryData) => {
    const response = await api.post('/api/health/analyze', { 
      repository_data: repositoryData 
    });
    return response.data;
  },
  
  /**
   * Get historical metrics for repository
   * @param {string} repoId - Repository identifier
   * @returns {Promise} Historical metrics data
   */
  getHealthMetrics: async (repoId) => {
    const response = await api.get(`/api/health/metrics/${repoId}`);
    return response.data;
  },
  
  /**
   * Get technical debt analysis
   * @param {string} repoId - Repository identifier
   * @returns {Promise} Technical debt estimation
   */
  getTechnicalDebt: async (repoId) => {
    const response = await api.get(`/api/health/debt/${repoId}`);
    return response.data;
  },
  
  /**
   * Get code quality trends over time
   * @param {string} repoId - Repository identifier
   * @param {string} period - Time period (week, month, year)
   * @returns {Promise} Trend data
   */
  getQualityTrends: async (repoId, period = 'month') => {
    const response = await api.get(`/api/health/trends/${repoId}`, {
      params: { period }
    });
    return response.data;
  }
};

// ==================== REFACTOR SUGGESTIONS API (Phase 9) ====================
export const refactorAPI = {
  /**
   * Get refactoring suggestions for code
   * @param {string} code - Source code
   * @param {string} language - Programming language
   * @returns {Promise} Refactoring recommendations
   */
  getSuggestions: async (code, language) => {
    const response = await api.post('/api/refactor/suggest', { code, language });
    return response.data;
  },
  
  /**
   * Apply a refactoring suggestion automatically
   * @param {string} code - Original code
   * @param {string} suggestionId - Suggestion identifier
   * @returns {Promise} Refactored code
   */
  applyRefactor: async (code, suggestionId) => {
    const response = await api.post('/api/refactor/apply', { code, suggestion_id: suggestionId });
    return response.data;
  },
  
  /**
   * Get complexity analysis for a file
   * @param {string} code - Source code
   * @param {string} language - Programming language
   * @returns {Promise} Complexity metrics
   */
  analyzeComplexity: async (code, language) => {
    const response = await api.post('/api/refactor/complexity', { code, language });
    return response.data;
  }
};

// ==================== DEPENDENCY SCANNER API (Phase 10) ====================
export const dependencyAPI = {
  /**
   * Scan dependencies for vulnerabilities
   * @param {string} repoId - Repository identifier
   * @returns {Promise} Vulnerability report
   */
  scanDependencies: async (repoId) => {
    const response = await api.post('/api/dependencies/scan', { repo_id: repoId });
    return response.data;
  },
  
  /**
   * Check for outdated packages
   * @param {string} repoId - Repository identifier
   * @returns {Promise} Outdated packages list
   */
  checkOutdated: async (repoId) => {
    const response = await api.get(`/api/dependencies/outdated/${repoId}`);
    return response.data;
  },
  
  /**
   * Get security advisories for dependencies
   * @param {string} packageName - Package name
   * @param {string} version - Package version
   * @returns {Promise} Security advisories
   */
  getAdvisories: async (packageName, version) => {
    const response = await api.get('/api/dependencies/advisories', {
      params: { package: packageName, version }
    });
    return response.data;
  },
  
  /**
   * Generate dependency report
   * @param {string} repoId - Repository identifier
   * @returns {Promise} Report data
   */
  generateReport: async (repoId) => {
    const response = await api.get(`/api/dependencies/report/${repoId}`);
    return response.data;
  }
};

// ==================== COMMIT GENERATOR API (Phase 11) ====================
export const commitAPI = {
  /**
   * Generate commit message from git diff
   * @param {string} diff - Git diff content
   * @returns {Promise} Generated commit message
   */
  generateCommitMessage: async (diff) => {
    const response = await api.post('/api/commit/generate', { diff });
    return response.data;
  },
  
  /**
   * Analyze changes and suggest commit type
   * @param {string} diff - Git diff content
   * @returns {Promise} Change analysis and suggested type
   */
  analyzeChanges: async (diff) => {
    const response = await api.post('/api/commit/analyze', { diff });
    return response.data;
  },
  
  /**
   * Generate conventional commit message
   * @param {string} description - Change description
   * @param {string} type - Commit type (feat, fix, docs, etc.)
   * @returns {Promise} Formatted commit message
   */
  generateConventionalCommit: async (description, type = 'feat') => {
    const response = await api.post('/api/commit/conventional', {
      description,
      type
    });
    return response.data;
  }
};

// ==================== PR REVIEW API (Phase 12) ====================
export const prAPI = {
  /**
   * Review pull request changes
   * @param {string} prUrl - Pull request URL
   * @returns {Promise} PR review with comments
   */
  reviewPR: async (prUrl) => {
    const response = await api.post('/api/pr/review', { pr_url: prUrl });
    return response.data;
  },
  
  /**
   * Get impact analysis of changes
   * @param {string} repoId - Repository identifier
   * @param {string} branch - Branch name
   * @returns {Promise} Impact analysis report
   */
  getImpactAnalysis: async (repoId, branch) => {
    const response = await api.post('/api/pr/impact', { repo_id: repoId, branch });
    return response.data;
  },
  
  /**
   * Generate PR summary
   * @param {string} prUrl - Pull request URL
   * @returns {Promise} PR summary
   */
  generateSummary: async (prUrl) => {
    const response = await api.post('/api/pr/summary', { pr_url: prUrl });
    return response.data;
  }
};

// ==================== TEST GENERATOR API (Phase 13) ====================
export const testAPI = {
  /**
   * Generate unit tests for code
   * @param {string} code - Source code
   * @param {string} language - Programming language
   * @returns {Promise} Generated test code
   */
  generateTests: async (code, language) => {
    const response = await api.post('/api/test/generate', { code, language });
    return response.data;
  },
  
  /**
   * Generate edge cases for a function
   * @param {string} functionCode - Function implementation
   * @returns {Promise} Edge case test scenarios
   */
  generateEdgeCases: async (functionCode) => {
    const response = await api.post('/api/test/edge-cases', { code: functionCode });
    return response.data;
  },
  
  /**
   * Generate mock data for testing
   * @param {string} schema - Data schema or type
   * @returns {Promise} Mock data
   */
  generateMockData: async (schema) => {
    const response = await api.post('/api/test/mock-data', { schema });
    return response.data;
  }
};

// ==================== DEPENDENCY GRAPH API (Phase 14) ====================
export const graphAPI = {
  /**
   * Get dependency graph for repository
   * @param {string} repoId - Repository identifier
   * @returns {Promise} Graph data for visualization
   */
  getDependencyGraph: async (repoId) => {
    const response = await api.get(`/api/graph/dependencies/${repoId}`);
    return response.data;
  },
  
  /**
   * Get module relationships
   * @param {string} repoId - Repository identifier
   * @returns {Promise} Module relationship data
   */
  getModuleRelations: async (repoId) => {
    const response = await api.get(`/api/graph/modules/${repoId}`);
    return response.data;
  },
  
  /**
   * Get circular dependency warnings
   * @param {string} repoId - Repository identifier
   * @returns {Promise} Circular dependencies
   */
  getCircularDependencies: async (repoId) => {
    const response = await api.get(`/api/graph/circular/${repoId}`);
    return response.data;
  }
};

// ==================== AI CHAT API (Phase 15) ====================
export const chatAPI = {
  /**
   * Chat with repository context
   * @param {string} message - User message
   * @param {string} repoId - Repository identifier
   * @param {string} conversationId - Conversation ID for context
   * @returns {Promise} AI response with context
   */
  sendMessage: async (message, repoId, conversationId = null) => {
    const response = await api.post('/api/chat/message', {
      message,
      repo_id: repoId,
      conversation_id: conversationId
    });
    return response.data;
  },
  
  /**
   * Get chat history for a conversation
   * @param {string} conversationId - Conversation identifier
   * @returns {Promise} Chat history
   */
  getHistory: async (conversationId) => {
    const response = await api.get(`/api/chat/history/${conversationId}`);
    return response.data;
  },
  
  /**
   * Clear chat context for new conversation
   * @param {string} repoId - Repository identifier
   * @returns {Promise} New conversation ID
   */
  newConversation: async (repoId) => {
    const response = await api.post('/api/chat/new', { repo_id: repoId });
    return response.data;
  },
  
  /**
   * Get suggested questions for repository
   * @param {string} repoId - Repository identifier
   * @returns {Promise} Suggested questions
   */
  getSuggestions: async (repoId) => {
    const response = await api.get(`/api/chat/suggestions/${repoId}`);
    return response.data;
  }
};

// ==================== UTILITY FUNCTIONS ====================
export const utils = {
  /**
   * Check if backend is reachable
   * @returns {Promise<boolean>} Backend status
   */
  checkHealth: async () => {
    try {
      const response = await api.get('/health');
      return response.data.status === 'healthy';
    } catch (error) {
      return false;
    }
  },
  
  /**
   * Get API version and info
   * @returns {Promise} API information
   */
  getApiInfo: async () => {
    const response = await api.get('/');
    return response.data;
  },
  
  /**
   * Cancel ongoing request (useful for file uploads)
   * @returns {AbortController} Controller for aborting requests
   */
  createAbortController: () => {
    return new AbortController();
  },
  
  /**
   * Format file size for display
   * @param {number} bytes - File size in bytes
   * @returns {string} Formatted file size
   */
  formatFileSize: (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  },
  
  /**
   * Debounce function for search inputs
   * @param {Function} func - Function to debounce
   * @param {number} delay - Delay in milliseconds
   * @returns {Function} Debounced function
   */
  debounce: (func, delay) => {
    let timeoutId;
    return (...args) => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => func(...args), delay);
    };
  }
};

// Default export for convenience
export default api;