// Authentication utilities for PCC Prototype

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const TOKEN_KEY = 'pcc_auth_token';

/**
 * Login with username and password
 * @param {string} username 
 * @param {string} password 
 * @returns {Promise<{success: boolean, error?: string}>}
 */
export async function login(username, password) {
  try {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    const response = await fetch(`${API_BASE_URL}/token`, {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      throw new Error('Invalid credentials');
    }

    const data = await response.json();
    
    // Store token in localStorage
    localStorage.setItem(TOKEN_KEY, data.access_token);
    
    return { success: true };
  } catch (error) {
    console.error('Login error:', error);
    return { success: false, error: error.message };
  }
}

/**
 * Login with demo credentials
 * @returns {Promise<{success: boolean, error?: string}>}
 */
export async function loginWithDemoCredentials() {
  return login('admin', 'admin123');
}

/**
 * Get authorization headers for API requests
 * @returns {Object} Headers object with Authorization header
 */
export function getAuthHeaders() {
  const token = localStorage.getItem(TOKEN_KEY);
  if (!token) {
    return {};
  }
  
  return {
    'Authorization': `Bearer ${token}`
  };
}

/**
 * Check if user is authenticated
 * @returns {boolean}
 */
export function isAuthenticated() {
  const token = localStorage.getItem(TOKEN_KEY);
  return !!token;
}

/**
 * Logout - clear stored token
 */
export function logout() {
  localStorage.removeItem(TOKEN_KEY);
}

/**
 * Make authenticated API request
 * @param {string} url 
 * @param {Object} options 
 * @returns {Promise<Response>}
 */
export async function authenticatedFetch(url, options = {}) {
  const authHeaders = getAuthHeaders();
  
  return fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      ...authHeaders
    }
  });
}