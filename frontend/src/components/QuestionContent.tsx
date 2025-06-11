import React, { useState } from "react";

export default function QuestionContent({ questionContent }) {
  const [selectOptions, setSelectedOptions] = useState<string>("");
  const [isSolution, setIsSolution] = useState<boolean>(false);
  const [SolutionError, setSolutionError] = useState<boolean>(false);
  console.log(questionContent);
  const handleSubmit = () => {
    if (selectOptions === questionContent.answer) {
      setIsSolution(true);
      setSolutionError(false);
    } else {
      setSolutionError(true);
    }
  };
  return (
    <div>
      <div className="font-semibold">{questionContent.question}</div>
      {questionContent.options?.map((opt: string, i: number) => (
        <div key={i}>
          <div className="mb-2">
            <input
              disabled={isSolution}
              type="checkbox"
              name="question_options"
              id=""
              value={opt}
              onChange={() => setSelectedOptions(opt)}
            />
            <label className="ml-[10px]" htmlFor="">
              {opt}
            </label>
          </div>
        </div>
      ))}
      <div className="mt-3">
        <button
          onClick={handleSubmit}
          disabled={isSolution}
          className="btn btn-primary"
        >
          Ответить
        </button>
        {SolutionError && (
          <div>
            <span className="text-error">Неверно!</span>
          </div>
        )}
        {isSolution && (
          <div>
            <span className="text-success">Верно!</span>
          </div>
        )}
      </div>
    </div>
  );
}
