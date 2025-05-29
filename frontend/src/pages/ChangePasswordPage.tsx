import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";

export default function ChangePasswordPage() {
  const [showErrorPass, setShowErrorPass] = useState<boolean>(false);
  const [newPassword, setNewPassword] = useState<string>("");
  const [repeatPassword, setRepeatPassword] = useState<string>("");
  const [isSave, setIsSave] = useState<boolean>(false);
  const [isSaved, setIsSaved] = useState<boolean>(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setShowErrorPass(false);
    if (newPassword !== repeatPassword) {
      setShowErrorPass(true);
      return;
    }
    setIsSave(true);
    try {
      await new Promise(() => {
        setTimeout(() => {
          setIsSaved(true);
        }, 1000);
      });
    } finally {
      setIsSaved(false);
    }
  };

  return (
    <section>
      <div className="min-h-screen flex flex-col items-center justify-center p-4 bg-base-100">
        <div className="flex items-center w-full max-w-md flex-col mx-auto gap-5 p-8 bg-base-200 rounded-xl shadow-lg border border-base-300">
          {isSaved ? (
            <div className="flex items-center flex-col gap-2">
              <p className="text-base-content">Пароль Сохранен</p>
              <p className="text-base-content">
                Хотите{" "}
                <Link className="text-primary underline" to="/auth">
                  войти
                </Link>
                ?
              </p>
            </div>
          ) : (
            <>
              <h6 className="mb-5 text-center text-xl text-base-content">
                Смена пароля
              </h6>
              {showErrorPass && (
                <h1 className="text-error mb-[20px] text-center">
                  Пароли не совпадают
                </h1>
              )}
              <form onSubmit={handleSubmit}>
                <div className="flex flex-col gap-3">
                  <h6 className="text-base-content">Новый пароль</h6>
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
                      onChange={(e) => setNewPassword(e.target.value)}
                    />
                  </label>
                  <p className="validator-hint hidden text-error">
                    Должно быть более 8 символов, включая
                    <br />
                    Хотя бы одну цифру <br />
                    Хотя бы одна строчная буква <br />
                    Хотя бы одна заглавная буква
                  </p>
                  {/* input password */}
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
                    <button className="btn btn-primary w-full max-w-xs md:btn-md mt-[10px] font-medium">
                      {isSave ? (
                        <div className="btn-square flex justify-center">
                          <span className="loading loading-spinner"></span>
                        </div>
                      ) : (
                        "Сохранить"
                      )}
                    </button>
                  </div>
                </div>
              </form>
            </>
          )}
        </div>
      </div>
    </section>
  );
}
