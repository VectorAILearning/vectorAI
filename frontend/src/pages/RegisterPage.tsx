import { useState, type FormEvent } from "react";
import FormVerify from "../components/FormVerify";

export default function RegisterPage() {
  const [email, setEmail] = useState<string>("");
  const [regPassword, setRegPassword] = useState<string>("");
  const [repeatPassword, setRepeatPassword] = useState<string>("");
  const [showErrorPass, setShowErrorPass] = useState<boolean>(false);
  const [showVerifyCode, setShowVerifyCode] = useState<boolean>(false);
  const [disabledButton, setDisabledButton] = useState<boolean>(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setShowErrorPass(false);
    if (regPassword !== repeatPassword) {
      setShowErrorPass(true);
      return;
    }
    try {
      await new Promise(() => {
        setDisabledButton(true);
        setTimeout(() => {
          setShowVerifyCode(true);
        }, 1000);
      });
    } finally {
      /* empty */
    }
  };

  return (
    <section className="min-h-screen flex flex-col items-center justify-center p-4 bg-base-100">
      <div className="flex items-center w-full max-w-md flex-col mx-auto gap-5 p-8 bg-base-200 rounded-xl shadow-lg border border-base-300">
        {showVerifyCode ? (
          <FormVerify />
        ) : (
          <>
            <h6 className="mb-5 text-center text-xl text-base-content">
              Регистрация
            </h6>
            {showErrorPass && (
              <h1 className="text-error mb-[20px] text-center">
                Пароли не совпадают
              </h1>
            )}
            <form onSubmit={handleSubmit}>
              <div className="flex flex-col gap-3">
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
                    disabled={disabledButton}
                    className="text-base-content"
                    onChange={(e) => setEmail(e.target.value)}
                  />
                </label>
                <div className="validator-hint hidden text-error">
                  Укажите действующую почту
                </div>
                <h6 className="text-base-content">Пароль</h6>

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
                    disabled={disabledButton}
                    required
                    placeholder="Пароль"
                    minLength={8}
                    pattern="(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}"
                    title="Должно быть более 8 символов, включая цифры, строчные буквы, заглавные буквы"
                    className="text-base-content"
                    onChange={(e) => setRegPassword(e.target.value)}
                  />
                </label>
                <p className="validator-hint hidden text-error">
                  Должно быть более 8 символов, включая
                  <br />
                  Хотя бы одну цифру <br />
                  Хотя бы одна строчная буква <br />
                  Хотя бы одна заглавная буква
                </p>
                <h6 className="text-base-content">Повторите пароль</h6>

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
                    disabled={disabledButton}
                    placeholder="Пароль"
                    minLength={8}
                    pattern="(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}"
                    title="Должно быть более 8 символов, включая цифры, строчные буквы, заглавные буквы"
                    className="text-base-content"
                    onChange={(e) => setRepeatPassword(e.target.value)}
                  />
                </label>
                <p className="validator-hint hidden text-error">
                  Должно быть более 8 символов, включая
                  <br />
                  Хотя бы одну цифру <br />
                  Хотя бы одна строчная буква <br />
                  Хотя бы одна заглавная буква
                </p>
                <div className="flex w-full">
                  <button
                    disabled={disabledButton}
                    className="btn btn-primary w-full max-w-xs md:btn-md mt-[10px] font-medium"
                  >
                    {disabledButton ? (
                      <span className="loading loading-spinner"></span>
                    ) : (
                      "Зарегистрироваться"
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
