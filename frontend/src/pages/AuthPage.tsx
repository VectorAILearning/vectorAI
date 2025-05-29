import { useState, useEffect, useRef } from "react";
import { Link } from "react-router-dom";

export default function AuthPage() {
  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");

  return (
    <section className="min-h-screen flex flex-col items-center justify-center p-4 bg-base-100">
      <div className="flex items-center w-full max-w-md flex-col mx-auto gap-5 p-8 bg-base-200 rounded-xl shadow-lg border border-base-300">
        <h6 className="mb-5 text-center text-xl text-base-content">
          Авторизация
        </h6>
        <form>
          <div className="flex flex-col gap-3">
            {/* input email */}
            <div className="flex">
              <h6 className="text-base-content">Почта</h6>
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
            {/* input password */}
            <h6 className="text-base-content">Пароль</h6>
            <div className="flex flex-col items-end">
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
                    <path d="M2.586 17.414A2 2 0 0 0 2 18.828V21a1 1 0 0 0 1 1h3a1 1 0 0 0 1-1v-1a1 1 0 0 1 1-1h1a1 1 0 0 0 1-1v-1a1 1 0 0 1 1-1h.172a2 2 0 0 0 1.414-.586l.814-.814a6.5 6.5 0 1 0-4-4z"></path>
                    <circle
                      cx="16.5"
                      cy="7.5"
                      r=".5"
                      fill="currentColor"
                    ></circle>
                  </g>
                </svg>
                <input
                  type="password"
                  required
                  placeholder="Пароль"
                  minLength={8}
                  pattern="(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}"
                  title="Должно быть более 8 символов, включая цифры, строчные буквы, заглавные буквы"
                  className="text-base-content"
                  onChange={(e) => setPassword(e.target.value)}
                />
              </label>
              <div className="justify-end text-[10px] mt-[5px]">
                <Link className="text-primary" to="/auth/recover">
                  Забыли пароль?{" "}
                </Link>
              </div>
            </div>
            <p className="validator-hint hidden text-error">
              Должно быть более 8 символов, включая
              <br />
              Хотя бы одну цифру <br />
              Хотя бы одна строчная буква <br />
              Хотя бы одна заглавная буква
            </p>

            <div className="flex w-full">
              <button className="btn btn-primary w-full max-w-xs md:btn-md mt-[10px] font-medium">
                Войти
              </button>
            </div>
          </div>
        </form>

        <button
          className="btn bg-white shadow-md hover:shadow-lg border border-base-300 rounded-[50px] p-2 transition-all duration-200 flex items-center justify-center"
          style={{ minWidth: 48, minHeight: 48 }}
        >
          <svg
            aria-label="Google logo"
            width="16"
            height="16"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 512 512"
          >
            <g>
              <path d="m0 0H512V512H0" fill="#fff"></path>
              <path
                fill="#34a853"
                d="M153 292c30 82 118 95 171 60h62v48A192 192 0 0190 341"
              ></path>
              <path
                fill="#4285f4"
                d="m386 400a140 175 0 0053-179H260v74h102q-7 37-38 57"
              ></path>
              <path
                fill="#fbbc02"
                d="m90 341a208 200 0 010-171l63 49q-12 37 0 73"
              ></path>
              <path
                fill="#ea4335"
                d="m153 219c22-69 116-109 179-50l55-54c-78-75-230-72-297 55"
              ></path>
            </g>
          </svg>
        </button>
      </div>
      <div className="mt-[50px] gap-3 flex flex-col items-center">
        <div>
          <p className="text-base-content">
            Нет аккаунта?{" "}
            <Link to="/auth/register" className="text-primary underline">
              Зарегистрируйся!
            </Link>
          </p>
        </div>
        <div></div>
      </div>
    </section>
  );
}
