import { useState, type FormEvent } from "react";
import { useAppDispatch, useAppSelector } from "../store";
import { requestPasswordReset } from "../store/passwordSlice.ts";
import {Navigate} from "react-router-dom";

export default function ForgetPasswordPage() {
  const [email, setEmail] = useState<string>("");

  const dispatch = useAppDispatch();
  const { status, error, message } = useAppSelector((state) => state.password);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();

    dispatch(requestPasswordReset(email));
  };

  return (
    <section className="min-h-screen flex flex-col items-center justify-center p-4 bg-base-100">
      <div className="flex items-center w-full max-w-md flex-col mx-auto gap-5 p-8 bg-base-200 rounded-xl shadow-lg border border-base-300">
        {status === "succeeded" ? (
          <div className="text-center">
            <h6 className="text-lg font-bold text-xl mb-4 text-base-content">
              Проверьте вашу почту
            </h6>
            <p className="text-base-content text-sm">{message}</p>
          </div>
        ) : (
          <>
            <h6 className="mb-5 text-center text-xl text-base-content">
              Восстановление пароля
            </h6>
            <form onSubmit={handleSubmit}>
              <div className="flex flex-col gap-3">
                {/* input email */}
                <div className="flex">
                  <h6 className="text-base-content text-sm text-red-600">{error}</h6>
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
                    type="email"
                    placeholder="Почта"
                    required
                    className="text-base-content"
                    onChange={(e) => setEmail(e.target.value)}
                  />
                </label>
                <div className="validator-hint hidden text-error">
                  Укажите действующую почту
                </div>
                <div className="flex w-full">
                  <button className="btn btn-primary w-full max-w-xs md:btn-md mt-[10px] font-medium">
                    {status == "loading" ? (
                      <div className="btn-square flex justify-center">
                        <span className="loading loading-spinner"></span>
                      </div>
                    ) : (
                      "Отправить письмо"
                    )}
                  </button>
                </div>
              </div>
            </form>
          </>
        )}
      </div>
    </section>
  );
}
