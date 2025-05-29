import { BrowserRouter, Routes, Route } from "react-router-dom";
import HomePage from "./pages/HomePage";
import AuthPage from "./pages/AuthPage";
import CoursesPage from "./pages/CoursesPage";
import ForgetPasswordPage from "./pages/ForgetPasswordPage";
import ChangePasswordPage from "./pages/ChangePasswordPage";
import RegisterPage from "./pages/RegisterPage";
import MainLayout from "./pages/MainLayout.tsx";
import UserProfilePage from "./pages/UserProfilePage.tsx";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<MainLayout />}>
          <Route path="/" element={<HomePage />} />
          <Route path="/auth" element={<AuthPage />} />
          <Route path="/courses" element={<CoursesPage />} />
          <Route path="/auth/recover" element={<ForgetPasswordPage />} />
          <Route path="/auth/changepass" element={<ChangePasswordPage />} />
          <Route path="/auth/register" element={<RegisterPage />} />
          <Route path="/profile" element={<UserProfilePage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
