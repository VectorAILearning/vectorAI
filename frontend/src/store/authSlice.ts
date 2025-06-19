import { createSlice, type PayloadAction } from "@reduxjs/toolkit";
import { loginUser, registerUser, verifyEmail } from "./auth/authThunks.ts";
import {
  handleLoginFulfilled,
  handleLoginPending,
  handleLoginRejected,
  handleRegisterFulfilled,
  handleRegisterPending,
  handleRegisterRejected,
  handleVerifyEmailFulfilled,
  handleVerifyEmailPending,
  handleVerifyEmailRejected,
} from "./auth/authHandlers.ts";
import type { IToken } from "../types/token.ts";

export interface AuthState {
  token: string | null;
  loading: boolean;
  error: string | null;
  message: string | null;
  isAuth: boolean;
}

const initialState: AuthState = {
  token: localStorage.getItem("token"),
  loading: false,
  error: null,
  message: null,
  isAuth: !!localStorage.getItem("token"),
};

const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    logOut(state) {
      state.token = null;
      state.isAuth = false;
      localStorage.removeItem("token");
    },
    updateToken(state, action: PayloadAction<IToken>) {
      state.token = action.payload.access_token;
      state.isAuth = true;
    },
    clearAuthState(state) {
      state.message = null;
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder.addCase(registerUser.pending, handleRegisterPending);
    builder.addCase(registerUser.fulfilled, handleRegisterFulfilled);
    builder.addCase(registerUser.rejected, handleRegisterRejected);

    builder.addCase(verifyEmail.pending, handleVerifyEmailPending);
    builder.addCase(verifyEmail.fulfilled, handleVerifyEmailFulfilled);
    builder.addCase(verifyEmail.rejected, handleVerifyEmailRejected);

    builder.addCase(loginUser.pending, handleLoginPending);
    builder.addCase(loginUser.fulfilled, handleLoginFulfilled);
    builder.addCase(loginUser.rejected, handleLoginRejected);
  },
});
export const { logOut, updateToken, clearAuthState } = authSlice.actions;
export default authSlice.reducer;
