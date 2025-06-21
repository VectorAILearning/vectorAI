import { BrowserRouter, Routes, Route } from "react-router-dom";
import HomePage from "./pages/HomePage";
import AuthPage from "./pages/AuthPage";
import ForgetPasswordPage from "./pages/ForgetPasswordPage";
import ChangePasswordPage from "./pages/ChangePasswordPage";
import RegisterPage from "./pages/RegisterPage";
import MainLayout from "./layouts/MainLayout.tsx";
import UserProfilePage from "./pages/UserProfilePage.tsx";
import CheckEmailPage from "./pages/CheckEmailPage.tsx";
import VerifyEmailPage from "./pages/VerifyEmailPage.tsx";
import PrivateRoute from "./components/PrivateRoute.tsx";
import PublicRoute from "./components/PublicRoute.tsx";
import { useAuthUser } from "./hooks/useAuthUser.ts";
import ResetPasswordPage from "./pages/ResetPasswordPage.tsx";

export default function App() {
  useAuthUser();
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
          <Route path="/reset_password" element={<ResetPasswordPage />} />

          <Route
            path="/profile"
            element={
              <PrivateRoute>
                <UserProfilePage />
              </PrivateRoute>
            }
          />
        </Route>

        <Route path="/check_email" element={<CheckEmailPage />} />
        <Route path="/verify_email" element={<VerifyEmailPage />} />
      </Routes>
    </BrowserRouter>
  );
}
