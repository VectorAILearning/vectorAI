import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import axios from "../api/axiosInstance.ts";
import type { ErrorResponse, MessageResponse } from "./auth/authTypes.ts";
import type { AxiosError } from "axios";

interface passwordState {
  status: "idle" | "loading" | "succeeded" | "failed";
  message: string | null;
  error: string | null;
}
const initialState: passwordState = {
  status: "idle",
  message: null,
  error: null,
};

export const requestPasswordReset = createAsyncThunk<
  MessageResponse,
  string,
  { rejectValue: string }
>("recoverPassword", async (email: string, { rejectWithValue }) => {
  try {
    const response = await axios.post("/auth/forgot-password", {
      username: email,
    });
    return response.data;
  } catch (error) {
    const err = error as AxiosError<ErrorResponse>;

    if (err.response?.status === 422) {
      return rejectWithValue(err.response.data.detail);
    }
    if (err.response?.status === 404) {
      return rejectWithValue(err.response.data.detail);
    }

    return rejectWithValue("Ошибка сервера");
  }
});

export const resetPassword = createAsyncThunk<
  string,
  { token: string; new_password: string },
  { rejectValue: string }
>("resetPassword", async ({ token, new_password }, { rejectWithValue }) => {
  try {
    const response = await axios.post("/auth/reset-password", {
      token,
      new_password,
    });
    return response.data.result;
  } catch (error) {
    const err = error as AxiosError<ErrorResponse>;
    if (err.response?.status === 422) {
      return rejectWithValue(err.response.data.detail);
    }
    if (err.response?.status === 400) {
      return rejectWithValue("Время действия ссылки истекло");
    }

    return rejectWithValue("Неизвестаня ошибка во время сброса пароля");
  }
});

const passwordSlice = createSlice({
  name: "password",
  initialState,
  reducers: {
      clearState(state) {
          state.status = "idle";
          state.message = null;
          state.error = null;
      }
  },
  extraReducers: (builder) => {
    builder
      .addCase(requestPasswordReset.pending, (state) => {
        state.status = "loading";
        state.message = null;
        state.error = null;
      })
      .addCase(requestPasswordReset.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.error = null;
        state.message = action.payload.result;
      })
      .addCase(requestPasswordReset.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.payload ?? "Неизвестаня ошибка";
        state.message = null;
      })
      .addCase(resetPassword.pending, (state) => {
        state.status = "loading";
        state.message = null;
        state.error = null;
      })
      .addCase(resetPassword.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.message = action.payload;
        state.error = null;
      })
      .addCase(resetPassword.rejected, (state, action) => {
        state.status = "failed";
        state.message = null;
        state.error = action.payload ?? "Неизвестаня ошибка";
      });
  },
});

export const {clearState} = passwordSlice.actions;
export default passwordSlice.reducer;
