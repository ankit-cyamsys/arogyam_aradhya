import axios from "axios";

const api = axios.create({ baseURL: "/api", timeout: 15000 });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("aa_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    // Network / server-down: no response object at all. Give a clear, actionable message.
    if (!err.response) {
      err.friendlyMessage =
        "Cannot reach the server. Please make sure the backend is running (port 8000).";
    } else if (err.response.status === 401) {
      const isAuthCall = err.config?.url?.includes("/auth/");
      if (!isAuthCall) localStorage.removeItem("aa_token");
      err.friendlyMessage = err.response.data?.detail || "Your session expired. Please log in again.";
    } else {
      err.friendlyMessage = err.response.data?.detail || "Something went wrong. Please try again.";
    }
    return Promise.reject(err);
  }
);

export default api;
