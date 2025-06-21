import { configureStore } from "@reduxjs/toolkit";
import userReducer from "./userSlice.ts";
import authReducer from "./authSlice";

import {
  type TypedUseSelectorHook,
  useDispatch,
  useSelector,
} from "react-redux";
import passwordSlice from "./passwordSlice.ts";

export const store = configureStore({
  reducer: {
    user: userReducer,
    auth: authReducer,
    password: passwordSlice,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;
export const useAppDispatch = () => useDispatch<AppDispatch>();
