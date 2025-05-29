import { useState, type FormEvent } from "react";

export default function ForgetPasswordPage() {
  const [email, setEmail] = useState<string | null>("");
  const [isSubmited, setIsSubmited] = useState<boolean>(false);
  const [isSubmiting, setIsSubmiting] = useState<boolean>(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setIsSubmited(true);
    try {
      await new Promise(() =>
        setTimeout(() => {
          setIsSubmiting(true);
        }, 1000),
      );
    } finally {
      setIsSubmiting(false);
    }
  };
  return (
    <section className="min-h-screen flex flex-col items-center justify-center p-4 bg-base-100">
      <div className="flex items-center w-full max-w-md flex-col mx-auto gap-5 p-8 bg-base-200 rounded-xl shadow-lg border border-base-300">
        {isSubmiting ? (
          <div className="text-center">
            <h6 className="text-lg font-bold text-xl mb-4 text-base-content">
              Проверьте вашу почту
            </h6>
            <p className="text-base-content text-sm">
              Письмо с инструкциями по восстановлению пароля было отправлено на
              <br />
              <span className="font-medium">{email}</span>
            </p>
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
                  <h6 className="text-base-content text-sm">Почта</h6>
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
                    disabled={isSubmited}
                    className="text-base-content"
                    onChange={(e) => setEmail(e.target.value)}
                  />
                </label>
                <div className="validator-hint hidden text-error">
                  Укажите действующую почту
                </div>
                <div className="flex w-full">
                  <button
                    disabled={isSubmited}
                    className="btn btn-primary w-full max-w-xs md:btn-md mt-[10px] font-medium"
                  >
                    {isSubmited ? (
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
