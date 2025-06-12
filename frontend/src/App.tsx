import { BrowserRouter, Routes, Route, useParams } from "react-router-dom";
import HomePage from "./pages/HomePage";
import AuthPage from "./pages/AuthPage";
import CoursesPage from "./pages/CoursesPage";
import ForgetPasswordPage from "./pages/ForgetPasswordPage";
import ChangePasswordPage from "./pages/ChangePasswordPage";
import RegisterPage from "./pages/RegisterPage";
import MainLayout from "./pages/MainLayout.tsx";
import UserProfilePage from "./pages/UserProfilePage.tsx";
import LessonsPage from "./pages/LessonsPage.tsx";
import CourseRedirectPage from "./pages/CourseRedirectPage.tsx";
import GenerateTasksPage from "./pages/GenerateTasksPage.tsx";
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
          <Route path="/course/:courseId" element={<CoursesPage />} />
          <Route
            path="/course/:courseId/lesson/:lessonId"
            element={<LessonsPage />}
          />
          <Route path="/auth/recover" element={<ForgetPasswordPage />} />
          <Route path="/auth/changepass" element={<ChangePasswordPage />} />
          <Route path="/auth/register" element={<RegisterPage />} />
          <Route path="/generate_tasks" element={<GenerateTasksPage />} />

          <Route
            path="/profile"
            element={
              <PrivateRoute>
                <UserProfilePage />
              </PrivateRoute>
            }
          />
          <Route path="/check_email" element={<CheckEmailPage />} />
          <Route path="/verify_email" element={<VerifyEmailPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
