import { BrowserRouter, Routes, Route } from "react-router-dom";
import HomePage from "./pages/HomePage";
import AuthPage from "./pages/AuthPage";
import CoursesPage from "./pages/CoursePage.tsx";
import ForgetPasswordPage from "./pages/ForgetPasswordPage";
import ChangePasswordPage from "./pages/ChangePasswordPage";
import RegisterPage from "./pages/RegisterPage";
import MainLayout from "./layouts/MainLayout.tsx";
import UserProfilePage from "./pages/UserProfilePage.tsx";
import LessonsPage from "./pages/LessonsPage.tsx";
import CourseRedirectPage from "./pages/CourseRedirectPage.tsx";
import GenerateTasksPage from "./pages/GenerateTasksPage.tsx";
import CourseLayout from "./layouts/CourseLayout.tsx";
import CheckEmailPage from "./pages/CheckEmailPage.tsx";
import VerifyEmailPage from "./pages/VerifyEmailPage.tsx";
import PrivateRoute from "./components/PrivateRoute.tsx";
import PublicRoute from "./components/PublicRoute.tsx";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<MainLayout />}>
          <Route path="/" element={<HomePage />} />
          <Route
              path="/auth"
              element={
                <PublicRoute>
                  <AuthPage />
                </PublicRoute>
              }
          />
          <Route path="/auth/recover" element={<ForgetPasswordPage />} />
          <Route path="/auth/changepass" element={<ChangePasswordPage />} />
          <Route path="/auth/register" element={<RegisterPage />} />
          <Route
              path="/profile"
              element={
                <PrivateRoute>
                  <UserProfilePage />
                </PrivateRoute>
              }
          />
          <Route path="/generate_tasks" element={<GenerateTasksPage />} />
        </Route>
        <Route path="/course" element={<CourseLayout />}>
          <Route path="" element={<CourseRedirectPage />} />
          <Route path=":courseId" element={<CoursesPage />} />
          <Route path=":courseId/lesson/:lessonId" element={<LessonsPage />} />
        </Route>
          <Route path="/check_email" element={<CheckEmailPage />} />
          <Route path="/verify_email" element={<VerifyEmailPage />} />
      </Routes>
    </BrowserRouter>
  );
}
