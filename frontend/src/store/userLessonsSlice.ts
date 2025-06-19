import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import axiosInstance from "../api/axiosInstance.ts";

type ContentType =
  | "text"
  | "video"
  | "code"
  | "dialog"
  | "practice"
  | "reflection"
  | "test";

interface Content {
  id: string;
  type: ContentType;
  position: number;
}

interface Lesson {
  id: string;
  title: string;
  description?: string;
  contents: Content[];
  estimated_time_hours: number;
  goal: string;
  is_completed: boolean;
  position: number;
}

export const fetchUserLessonsById = createAsyncThunk(
  "usersLessons/fetchById",
  async (lessonId: string) => {
    const response = await axiosInstance.get(lessonId);
    return response.data;
  },
);

interface LessonState {
  selectedLessons: Lesson[];
  loading: "idle" | "loading" | "succeeded" | "failed";
  error: string | null;
}

const initialState: LessonState = {
  selectedLessons: [],
  loading: "idle",
  error: null,
};

const userLessonsSlice = createSlice({
  name: "userLessons",
  initialState,
  reducers: {
    clearUserLessons: (state) => {
      state.selectedLessons = [];
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchUserLessonsById.pending, (state) => {
        state.loading = "loading";
      })
      .addCase(fetchUserLessonsById.fulfilled, (state, action) => {
        state.loading = "succeeded";
        state.selectedLessons = action.payload;
      })
      .addCase(fetchUserLessonsById.rejected, (state, action) => {
        state.loading = "failed";
        state.error = action.error.message || "Unknown error";
      });
  },
});

export const { clearUserLessons } = userLessonsSlice.actions;
export default userLessonsSlice.reducer;
