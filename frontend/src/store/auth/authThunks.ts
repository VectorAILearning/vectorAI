import { createAsyncThunk } from "@reduxjs/toolkit";
import qs from "qs";
import type { AxiosError } from "axios";

import axios from "../../api/axiosInstance.ts";
import type {
  ErrorResponse,
  LoginRequest,
  LoginResponse,
  MessageResponse,
  RegisterPayload,
} from "./authTypes.ts";

export const loginUser = createAsyncThunk<
  LoginResponse,
  LoginRequest,
  { rejectValue: string }
>("auth/login", async (payload, { rejectWithValue }) => {
  try {
    const response = await axios.post("/auth/login", qs.stringify(payload), {
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
    });
    return response.data;
  } catch (error) {
    const err = error as AxiosError<ErrorResponse>;
    if (err.response?.status === 401 || err.response?.status === 403) {
      return rejectWithValue(
        err.response.data.detail ?? "Ошибка валидации данных",
      );
    }
    return rejectWithValue("Ошибка авторизации");
  }
});

export const registerUser = createAsyncThunk<
  MessageResponse,
  RegisterPayload,
  { rejectValue: string }
>("auth/register", async (payload, { rejectWithValue }) => {
  try {
    const response = await axios.post<MessageResponse>(
      "/auth/register",
      payload,
    );
    return response.data;
  } catch (error) {
    const err = error as AxiosError<ErrorResponse>;
    if (err.response?.status === 422 || err.response?.status === 400) {
      return rejectWithValue(err.response.data.detail);
    }
    return rejectWithValue("Неизвестаня ошибка при регистрации");
  }
});

export const verifyEmail = createAsyncThunk<
  MessageResponse,
  string,
  { rejectValue: string }
>("auth/verifyEmail", async (token: string, { rejectWithValue }) => {
  try {
    const response = await axios.get(`/auth/verify-email?token=${token}`);
    return response.data;
  } catch (error) {
    const err = error as AxiosError<ErrorResponse>;

    if (err.response?.status === 400) {
      return rejectWithValue(err.response.data.detail);
    }

    return rejectWithValue("Ошибка сервера");
  }
});
