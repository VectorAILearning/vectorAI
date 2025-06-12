import type { PayloadAction } from "@reduxjs/toolkit";

import type { AuthState } from "../authSlice.ts";
import type { LoginResponse, MessageResponse } from "./authTypes.ts";

export const handleLoginPending = (state: AuthState) => {
  state.loading = true;
  state.error = null;
};

export const handleLoginFulfilled = (
  state: AuthState,
  action: PayloadAction<LoginResponse>,
) => {
  state.loading = false;
  state.token = action.payload.access_token;
  state.refreshToken = action.payload.refresh_token;
  state.error = null;
  state.isAuth = true;

  localStorage.setItem("token", action.payload.access_token);
  localStorage.setItem("refreshToken", action.payload.refresh_token);
};

export const handleLoginRejected = (
  state: AuthState,
  action: PayloadAction<string | undefined>,
) => {
  state.loading = false;
  state.token = null;
  state.refreshToken = null;
  state.error = action.payload ?? "Неизвестная ошибка";
  state.message = null;
};

export const handleRegisterPending = (state: AuthState) => {
  state.loading = true;
  state.error = null;
  state.message = null;
};

export const handleRegisterFulfilled = (
  state: AuthState,
  action: PayloadAction<MessageResponse>,
) => {
  state.loading = false;
  state.message = action.payload.result;
};

export const handleRegisterRejected = (
  state: AuthState,
  action: PayloadAction<string | undefined>,
) => {
  state.loading = false;
  state.error = action.payload ?? "Неизвестаня ошибка";
};

export const handleVerifyEmailPending = (state: AuthState) => {
  state.loading = true;
};
export const handleVerifyEmailFulfilled = (
  state: AuthState,
  action: PayloadAction<MessageResponse>,
) => {
  state.loading = false;
  state.message = action.payload.result;
};
export const handleVerifyEmailRejected = (
  state: AuthState,
  action: PayloadAction<string | undefined>,
) => {
  state.loading = false;
  state.error = action.payload ?? "Неизвестная ошибка";
};
