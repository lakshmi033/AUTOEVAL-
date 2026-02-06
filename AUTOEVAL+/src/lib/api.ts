import axios from 'axios';

// Create an axios instance with default config
export const api = axios.create({
    baseURL: 'http://localhost:8000', // Backend URL
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request Interceptor: Attach Token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response Interceptor: Handle Errors (Global)
api.interceptors.response.use(
    (response) => response,
    (error) => {
        // Handle 401 Unauthorized (Session Expired)
        if (error.response && error.response.status === 401) {
            // Check if the error is from a login attempt, in which case we DONT want to redirect
            // We want the user to see "Invalid password" etc.
            if (error.config.url && !error.config.url.includes('/login')) {
                // Clear token and redirect to login SELECTION page if 401 Unauthorized (Session Expired)
                localStorage.removeItem('token');
                localStorage.removeItem('autoeval_user');
                window.location.href = '/login';
            }
        }
        return Promise.reject(error);
    }
);
