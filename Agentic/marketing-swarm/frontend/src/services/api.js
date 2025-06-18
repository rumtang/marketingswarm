import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for auth token
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API endpoints
export const startConversation = async (query, testMode = false) => {
  const response = await api.post('/api/conversation/start', {
    user_query: query,
    test_mode: testMode,
  });
  return response.data;
};

export const getHealth = async () => {
  const response = await api.get('/api/health');
  return response.data;
};

export const getLaunchStatus = async () => {
  const response = await api.get('/api/launch-status');
  return response.data;
};

export const getAgentStatus = async () => {
  const response = await api.get('/api/agents/status');
  return response.data;
};

export const getConversation = async (conversationId) => {
  const response = await api.get(`/api/conversation/${conversationId}`);
  return response.data;
};

export const activateDemoSafeMode = async () => {
  const response = await api.post('/api/emergency/demo-safe-mode');
  return response.data;
};

export const resetSystem = async () => {
  const response = await api.post('/api/emergency/reset-system');
  return response.data;
};

export const restartAgents = async () => {
  const response = await api.post('/api/agents/restart');
  return response.data;
};

export default api;