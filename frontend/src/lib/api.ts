// lib/api.ts
import axios from "axios";

export const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000",
  withCredentials: true, // important for cookie-based auth or secure refresh
});

api.interceptors.request.use(config => {
  const accessToken = localStorage.getItem("access_token");
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});

// Optional: Automatically refresh token on 401
api.interceptors.response.use(
  res => res,
  async err => {
    if (err.response?.status === 401) {
      try {
        const refreshRes = await api.post("/users/refresh");
        localStorage.setItem("access_token", refreshRes.data.access_token);
        err.config.headers.Authorization = `Bearer ${refreshRes.data.access_token}`;
        return api(err.config);
      } catch (refreshErr) {
        console.log(refreshErr);
        localStorage.removeItem("access_token");
        window.location.href = "/login";
      }
    }
    return Promise.reject(err);
  }
);

export default api;
