import { configureStore } from "@reduxjs/toolkit";
import sessionReducer from "./sessionSlice";
import userReducer from "./userProfileSlice.ts";
import uiReducer from "./uiSlice.ts";
import userCoursesReducer from "./userCoursesSlice.ts";

import {
  type TypedUseSelectorHook,
  useDispatch,
  useSelector,
} from "react-redux";

export const store = configureStore({
  reducer: {
    session: sessionReducer,
    user: userReducer,
    userCourses: userCoursesReducer,
    ui: uiReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;
export const useAppDispatch = () => useDispatch<AppDispatch>();
