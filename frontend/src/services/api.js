import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const analysisAPI = {
  uploadZip: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/api/analysis/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
  
  analyzeGithub: async (repoUrl) => {
    const response = await api.post('/api/analysis/github', { repo_url: repoUrl });
    return response.data;
  },
};

export const reviewAPI = {
  reviewCode: async (code, language = 'python') => {
    const response = await api.post('/api/review/', { code, language });
    return response.data;
  },
};

export default api;