import { useAppSelector } from "../store";
import { useNavigate } from "react-router-dom";
import { useEffect } from "react";

export default function CheckEmailPage() {
  const message = useAppSelector((state) => state.auth.message);
  const navigate = useNavigate();
  useEffect(() => {
    if (!message) {
      navigate("/auth/register");
    }
  }, [message]);
  return (
    <div className="max-w-md mx-auto mt-20 text-center p-8 border border-gray-300 rounded-lg shadow-md">
      <h2 className="text-2xl font-semibold">Подтвердите вашу почту</h2>
      <p className="text-base mt-4">
        <strong>{message}</strong>.
      </p>
    </div>
  );
}
