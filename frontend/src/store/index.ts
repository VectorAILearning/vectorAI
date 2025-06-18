import { configureStore } from "@reduxjs/toolkit";
import sessionReducer from "./sessionSlice";
import userReducer from "./userSlice.ts";
import uiReducer from "./uiSlice.ts";
import userCoursesReducer from "./userCoursesSlice.ts";
import authReducer from "./authSlice";
import userLessonsReducer from "./userLessonsSlice.ts"

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
    userLessons: userLessonsReducer,
    ui: uiReducer,
    auth: authReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;
export const useAppDispatch = () => useDispatch<AppDispatch>();
