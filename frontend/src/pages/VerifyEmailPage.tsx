import { useAppDispatch, useAppSelector } from "../store";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useEffect } from "react";
import { verifyEmail } from "../store/auth/authThunks.ts";
import { clearAuthState } from "../store/authSlice.ts";

export default function VerifyEmailPage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");

  const dispatch = useAppDispatch();
  const { message, error } = useAppSelector((state) => state.auth);

  const navigate = useNavigate();


  useEffect(() => {
    if (token) {
      dispatch(verifyEmail(token));
      return () => {
        dispatch(clearAuthState());
      };
    }
  }, [token]);

  useEffect(() => {
    if (message || error) {
      const timer = setTimeout(() => {
        navigate("/auth");
      }, 2000);

      return () => clearTimeout(timer);
    }
  }, [message, error, navigate]);
  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="bg-white p-6 rounded-lg shadow-lg text-center">
        <h1>{message || error}</h1>
      </div>
    </div>
  );
}
