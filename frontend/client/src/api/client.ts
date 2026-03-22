import axios from 'axios';

// Create a centralized Axios instance
export const apiClient = axios.create({
    baseURL: '/api', // Vite proxy forwards this to localhost:5000
    headers: {
        'Content-Type': 'application/json',
    },
    // withCredentials: true, // Uncomment this when we add JWT cookies!
});

// Interceptor to unwrap the ApiResponse wrapper we built in Express
apiClient.interceptors.response.use(
    (response) => {
        // Our Express ApiResponse always sends data inside `response.data.data`
        return response.data.data; 
    },
    (error) => {
        // Standardize the error so React Query handles it cleanly
        const message = error.response?.data?.message || error.message || "An unexpected error occurred";
        return Promise.reject(new Error(message));
    }
);