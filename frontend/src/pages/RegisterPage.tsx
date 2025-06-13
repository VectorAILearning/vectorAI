import { useForm } from "react-hook-form";
import { useAppDispatch, useAppSelector } from "../store";
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { registerUser } from "../store/auth/authThunks.ts";

type RegisterFormInputs = {
  email: string;
  password: string;
  confirmPassword: string;
};

export default function RegisterPage() {
  const { message, loading, error } = useAppSelector((state) => state.auth);
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<RegisterFormInputs>();

  const onSubmit = (data: RegisterFormInputs) => {
    dispatch(registerUser({ username: data.email, password: data.password }));
  };

  const password = watch("password");

  useEffect(() => {
    if (message) {
      navigate("/check_email");
    }
  }, [message]);
  return (
    <>
      {loading ? (
        <div className="min-h-screen flex items-center justify-center">
          <span className="loading loading-ring loading-xl"></span>
        </div>
      ) : (
        <div className="max-w-md mx-auto mt-16 p-6 bg-base-100 text-base-content rounded-2xl shadow-lg border border-base-300">
          <h2 className="text-2xl font-bold mb-6 text-center">Регистрация</h2>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div>
              <label className="block text-sm font-medium">Email</label>
              <div className="text-red-500">{error}</div>
              <input
                type="email"
                {...register("email", {
                  required: "Email обязателен",
                  pattern: {
                    value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                    message: "Введите корректный email",
                  },
                })}
                className="input input-bordered w-full mt-1"
              />
              {errors.email && (
                <p className="text-error text-sm mt-1">
                  {errors.email.message}
                </p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium">Пароль</label>
              <input
                type="password"
                {...register("password", {
                  required: "Пароль обязателен",
                  minLength: {
                    value: 6,
                    message: "Минимум 6 символов",
                  },
                })}
                className="input input-bordered w-full mt-1"
              />
              {errors.password && (
                <p className="text-error text-sm mt-1">
                  {errors.password.message}
                </p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium">
                Подтверждение пароля
              </label>
              <input
                type="password"
                {...register("confirmPassword", {
                  required: "Подтвердите пароль",
                  validate: (value) =>
                    value === password || "Пароли не совпадают",
                })}
                className="input input-bordered w-full mt-1"
              />
              {errors.confirmPassword && (
                <p className="text-error text-sm mt-1">
                  {errors.confirmPassword.message}
                </p>
              )}
            </div>

            <button type="submit" className="btn btn-primary w-full">
              Зарегистрироваться
            </button>
          </form>
        </div>
      )}
    </>
  );
}
