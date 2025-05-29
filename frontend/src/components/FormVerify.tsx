import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";

export default function FormVerify() {
  const [queryCode, setQueryCode] = useState<string>("");
  const [VerifyCompleted, setVerifyCompleted] = useState<boolean>(false);
  const [VerifyShowCompleted, setVerifyShowCompleted] =
    useState<boolean>(false);
  const verifyCode = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    const filteredValue = value.replace(/\D/g, "");
    setQueryCode(filteredValue.slice(0, 4));
    let queryCodeCompleted = queryCode.length + 1;
    if (queryCodeCompleted === 4) {
      setVerifyCompleted(true);
      setTimeout(() => {
        setVerifyShowCompleted(true);
      }, 1000);
    }
    console.log(queryCodeCompleted);
  };

  return (
    <div>
      {VerifyShowCompleted ? (
        <div className="flex flex-col items-center">
          <p>Спасибо за подтверждение</p>
          <p>
            Хотите{" "}
            <Link to="/auth" className="text-info">
              войти?
            </Link>
          </p>
        </div>
      ) : (
        <>
          <div className="mb-[20px]">
            <h6 className="text-center">Подтвердите почту</h6>
          </div>
          <div>
            <p className="text-[12px]">Выслали 4-х значный код вам на почту</p>
            <input
              value={queryCode}
              className="input validator"
              required
              disabled={VerifyCompleted}
              onChange={(e) => {
                verifyCode(e);
              }}
              type="text"
              placeholder="Введите 4-х значных код"
              maxLength={4}
              title="Must be between be 1 to 4"
            />
            <p className="validator-hint">Должен быть 4-х значный код</p>
          </div>
        </>
      )}
    </div>
  );
}
