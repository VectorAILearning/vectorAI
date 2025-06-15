import axios from "axios";
import { store } from "../store";
import { logOut, updateToken } from "../store/authSlice.ts";
import type { IToken } from "../types/token.ts";

const axiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_HOST + "/api/v1",
  headers: {
    "Content-Type": "application/json",
  },
});

axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const refreshToken = localStorage.getItem("refreshToken");
      if (!refreshToken) {
        store.dispatch(logOut());
        return Promise.reject(error);
      }
      try {
        const { data } = await axios.post<IToken>(
          "http://localhost:8000/api/v1/auth/refresh",
          { refresh_token: refreshToken },
        );
        store.dispatch(updateToken(data));
        localStorage.setItem("token", data.access_token);
        localStorage.setItem("refreshToken", data.refresh_token);
        axios.defaults.headers.Authorization = `Bearer ${data.access_token}`;
        return axiosInstance(originalRequest);
      } catch (error) {
        console.log("токен истек");
        store.dispatch(logOut());
        return Promise.reject(error);
      }
    }
    return Promise.reject(error);
  },
);

export default axiosInstance;
