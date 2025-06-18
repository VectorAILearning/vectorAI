import { createSlice } from "@reduxjs/toolkit";
import type { PayloadAction } from "@reduxjs/toolkit";

interface Lesson {
  id: string;
  title: string;
  description?: string;
  [key: string]: any;
}

interface Module {
  id: string;
  title: string;
  lessons: Lesson[];
  [key: string]: any;
}

interface Course {
  id: string;
  title: string;
  description?: string;
  modules: Module[];
  [key: string]: any;
}

interface UserCoursesState {
  courses: Course[];
  selectedCourse: Course | null;
  selectedLesson: Lesson | null;
}

const initialState: UserCoursesState = {
  courses: [],
  selectedCourse: null,
  selectedLesson: null,
};

const userCoursesSlice = createSlice({
  name: "userCourses",
  initialState,
  reducers: {
    setCourses(state, action: PayloadAction<Course[]>) {
      state.courses = action.payload;
    },
    setSelectedCourse(state, action: PayloadAction<Course | null>) {
      state.selectedCourse = action.payload;
    },
  },
});

export const { setCourses, setSelectedCourse } =
  userCoursesSlice.actions;
export default userCoursesSlice.reducer;
