import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000, // 60 seconds timeout for large operations
});

// Request interceptor for logging
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
      const errorMessage = error.response.data?.detail || error.response.data?.message || 'An error occurred';
      console.error(`[API Error] ${error.response.status}: ${errorMessage}`);
      
      switch (error.response.status) {
        case 400:
          throw new Error(errorMessage || 'Bad request');
        case 404:
          throw new Error(errorMessage || 'Resource not found');
        case 413:
          throw new Error('File too large. Please upload a smaller file.');
        case 429:
          throw new Error('Too many requests. Please try again later.');
        case 500:
          throw new Error(errorMessage || 'Server error. Please try again later.');
        default:
          throw new Error(errorMessage || 'Request failed');
      }
    } else if (error.request) {
      console.error('[API Error] No response received:', error.request);
      throw new Error('Unable to connect to server. Please check if the backend is running.');
    } else {
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
    try {
      const response = await api.post('/api/analysis/github', { repo_url: repoUrl });
      return response.data;
    } catch (error) {
      if (error.response?.status === 404) {
        throw new Error(error.response?.data?.detail || 'Repository not found. Please check the URL and make sure the repository is public.');
      }
      throw error;
    }
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
    const response = await api.post('/api/review/', { code, language });
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
   * Get metrics for code quality over time
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

// ==================== BUG PREDICTION API ====================
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

// ==================== DOCUMENTATION API ====================
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

// ==================== CODE SEARCH API ====================
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

// ==================== HEALTH DASHBOARD API ====================
export const healthAPI = {
  /**
   * Analyze repository health
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
   * Get health metrics for a repository
   * @param {string} repoId - Repository identifier
   * @returns {Promise} Health metrics
   */
  getHealthMetrics: async (repoId) => {
    const response = await api.get(`/api/health/metrics/${repoId}`);
    return response.data;
  }
};

// ==================== REFACTOR SUGGESTIONS API ====================
export const refactorAPI = {
  /**
   * Get refactoring suggestions for code
   * @param {string} code - Source code
   * @param {string} language - Programming language
   * @returns {Promise} Refactoring recommendations
   */
  getSuggestions: async (code, language) => {
    const response = await api.post('/api/refactor/analyze', { code, language });
    return response.data;
  },
  
  /**
   * Analyze entire repository for refactoring opportunities
   * @param {Array} files - List of files with their data
   * @returns {Promise} Repository refactoring analysis
   */
  analyzeRepository: async (files) => {
    const response = await api.post('/api/refactor/analyze-repository', { files });
    return response.data;
  }
};

// ==================== DEPENDENCY SCANNER API ====================
export const dependencyAPI = {
  /**
   * Scan dependencies for vulnerabilities
   * @param {Object} repositoryData - Repository analysis data
   * @returns {Promise} Vulnerability report
   */
  scanDependencies: async (repositoryData) => {
    const response = await api.post('/api/dependencies/scan', { 
      repository_data: repositoryData 
    });
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
  }
};

// ==================== COMMIT GENERATOR API ====================
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
   * Generate conventional commit message from description
   * @param {string} description - Change description
   * @param {string} type - Commit type (feat, fix, docs, etc.)
   * @returns {Promise} Generated commit message
   */
  generateConventionalCommit: async (description, type = 'feat') => {
    const response = await api.post('/api/commit/generate', { description, commit_type: type });
    return response.data;
  },
  
  /**
   * Generate commit message with scope
   * @param {string} description - Change description
   * @param {string} type - Commit type
   * @param {string} scope - Commit scope
   * @returns {Promise} Generated commit message
   */
  generateCommitWithScope: async (description, type = 'feat', scope = null) => {
    const response = await api.post('/api/commit/generate', { 
      description, 
      commit_type: type, 
      scope 
    });
    return response.data;
  },
  
  /**
   * Parse a commit message to extract type and description
   * @param {string} commitMessage - Commit message to parse
   * @returns {Promise} Parsed commit data
   */
  parseCommit: async (commitMessage) => {
    const response = await api.post('/api/commit/parse', { commit_message: commitMessage });
    return response.data;
  },
  
  /**
   * Get available commit types
   * @returns {Promise} List of commit types
   */
  getCommitTypes: async () => {
    const response = await api.get('/api/commit/types');
    return response.data;
  }
};

// ==================== PR REVIEW API ====================
export const prAPI = {
  /**
   * Review a pull request
   * @param {string} diff - Git diff content
   * @param {string} title - PR title
   * @param {string} description - PR description
   * @returns {Promise} PR review results
   */
  reviewPR: async (diff, title = '', description = '') => {
    const response = await api.post('/api/pr/review', { 
      diff, 
      pr_title: title, 
      pr_description: description 
    });
    return response.data;
  }
};

// ==================== TEST GENERATOR API ====================
export const testAPI = {
  /**
   * Generate unit tests for code
   * @param {string} code - Source code
   * @param {string} language - Programming language
   * @param {string} functionName - Optional function name to test
   * @returns {Promise} Generated test code
   */
  generateTests: async (code, language, functionName = '') => {
    const response = await api.post('/api/test/generate', { 
      code, 
      language,
      function_name: functionName
    });
    return response.data;
  },
  
  /**
   * Generate edge cases for a function
   * @param {string} code - Source code
   * @param {string} language - Programming language
   * @returns {Promise} Edge case test scenarios
   */
  generateEdgeCases: async (code, language) => {
    const response = await api.post('/api/test/edge-cases', { 
      code, 
      language 
    });
    return response.data;
  }
};

// ==================== DEPENDENCY GRAPH API ====================
export const graphAPI = {
  /**
   * Get dependency graph for repository
   * @param {Object} repositoryData - Repository analysis data
   * @returns {Promise} Graph data for visualization
   */
  getDependencyGraph: async (repositoryData) => {
    const response = await api.post('/api/graph/build', { 
      repository_data: repositoryData 
    });
    return response.data;
  }
};

// ==================== AI CHAT API ====================
export const chatAPI = {
  /**
   * Send message to AI chat assistant
   * @param {string} message - User message
   * @param {Object} repositoryData - Repository data for context
   * @param {string} conversationId - Optional conversation ID
   * @returns {Promise} AI response
   */
  sendMessage: async (message, repositoryData, conversationId = null) => {
    const response = await api.post('/api/chat/message', {
      message,
      repository_data: repositoryData,
      conversation_id: conversationId
    });
    return response.data;
  },
  
  /**
   * Get conversation history
   * @param {string} conversationId - Conversation identifier
   * @returns {Promise} Chat history
   */
  getHistory: async (conversationId) => {
    const response = await api.get(`/api/chat/history/${conversationId}`);
    return response.data;
  },
  
  /**
   * Get suggested questions for repository
   * @param {Object} repositoryData - Repository data
   * @returns {Promise} Suggested questions
   */
  getSuggestions: async (repositoryData) => {
    const response = await api.post('/api/chat/suggestions', repositoryData);
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