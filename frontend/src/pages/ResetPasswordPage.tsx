import { useAppDispatch, useAppSelector } from "../store";
import {useEffect, useState} from "react";
import {Navigate, useNavigate, useSearchParams} from "react-router-dom";
import {clearState, resetPassword} from "../store/passwordSlice.ts";

const ResetPasswordPage = () => {
  const [password, setPassword] = useState("");
  const { status, message, error } = useAppSelector((state) => state.password);
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");
  const dispatch = useAppDispatch();
  const navigate = useNavigate();


  const onSubmitResetPassword = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (token) {
      dispatch(resetPassword({ token, new_password: password }));
    }
  };


  useEffect(() => {
    let timer: ReturnType<typeof setTimeout>;

    if (status === 'succeeded' || status === 'failed') {
      timer = setTimeout(() => {
        dispatch(clearState())
        navigate('/auth', { replace: true });
      }, 2000);
    }

    return () => clearTimeout(timer); // очищаем таймер при размонтировании
  }, [status, navigate])

  if (error) {
    return (
        <div className="min-h-screen flex flex-col items-center justify-center bg-base-100">
          <div className="flex itemss-center  max-w-md flex-col mx-auto gap-5 p-8 bg-base-200 rounded-xl shadow-lg border border-base-300">
            {error}
          </div>
        </div>
    );
  }
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-base-100">
      <div className="flex itemss-center  max-w-md flex-col mx-auto gap-5 p-8 bg-base-200 rounded-xl shadow-lg border border-base-300">
        {status === "succeeded" ? (
          <div>{message}</div>
        ) : (
          <form onSubmit={onSubmitResetPassword}>
            <div className="flex flex-col gap-3">
              {/* input email */}
              <div className="flex">
                <h6 className="text-base-content text-sm">
                  Введите новый пароль
                </h6>
              </div>
              <label className="input validator">
                <svg
                  className="h-[1em] opacity-50"
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                >
                  <g
                    strokeLinejoin="round"
                    strokeLinecap="round"
                    strokeWidth="2.5"
                    fill="none"
                    stroke="currentColor"
                  >
                    <rect width="20" height="16" x="2" y="4" rx="2"></rect>
                    <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"></path>
                  </g>
                </svg>
                <input
                  type="password"
                  placeholder="Пароль"
                  required
                  className="text-base-content"
                  onChange={(e) => setPassword(e.target.value)}
                />
              </label>

              <div className="flex w-full">
                <button className="btn btn-primary w-full max-w-xs md:btn-md mt-[10px] font-medium">
                  {status == "loading" ? (
                    <div className="btn-square flex justify-center">
                      <span className="loading loading-spinner"></span>
                    </div>
                  ) : (
                    "Обновить пароль"
                  )}
                </button>
              </div>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};

export default ResetPasswordPage;
