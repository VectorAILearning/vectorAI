import axios from "axios";
import { jwtDecode } from "jwt-decode";
import { store } from "../store";
import { logOut, updateToken } from "../store/authSlice.ts";
import type { IToken } from "../types/token.ts";

interface TokenPayload {
  exp: number;
  [key: string]: any;
}

const apiHost = import.meta.env.VITE_API_HOST;

const axiosInstance = axios.create({
  baseURL: `${apiHost}/api/v1`,
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true,
});

const refreshAxios = axios.create({
  baseURL: `${apiHost}/api/v1`,
  headers: { "Content-Type": "application/json" },
  withCredentials: true,
});

let isRefreshing = false;
let failedQueue: any[] = [];

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (token) prom.resolve(token);
    else prom.reject(error);
  });
  failedQueue = [];
};

axiosInstance.interceptors.request.use(async (config) => {
  let token = localStorage.getItem("token");

  if (token && config.headers) {
    const decoded = jwtDecode<TokenPayload>(token);
    const expiresAt = decoded.exp * 1000;
    const now = Date.now();
    const buffer = 60 * 1000;

    if (expiresAt - now < buffer && !isRefreshing) {
      isRefreshing = true;
      try {
        const { data } = await axiosInstance.post<IToken>("/auth/refresh");

        localStorage.setItem("token", data.access_token);
        store.dispatch(updateToken(data));
        processQueue(null, data.access_token);
        token = data.access_token;
      } catch (err) {
        processQueue(err, null);
        store.dispatch(logOut());
        throw err;
      } finally {
        isRefreshing = false;
      }
    } else if (isRefreshing) {
      return new Promise((resolve, reject) => {
        failedQueue.push({
          resolve: (token: string) => {
            config.headers!.Authorization = `Bearer ${token}`;
            resolve(config);
          },
          reject: (err: any) => reject(err),
        });
      });
    }

    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const { data } = await refreshAxios.post<IToken>("/auth/refresh");

        localStorage.setItem("token", data.access_token);
        store.dispatch(updateToken(data));

        originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
        return axiosInstance(originalRequest);
      } catch (err) {
        store.dispatch(logOut());
        return Promise.reject(err);
      }
    }
    return Promise.reject(error);
  },
);

export default axiosInstance;
