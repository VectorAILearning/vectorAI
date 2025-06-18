import { useState } from "react";
import ReactMarkdown from "react-markdown";

export default function QuestionContent({ questionContent }) {
  if (
    !questionContent ||
    typeof questionContent !== "object" ||
    typeof questionContent.question !== "string" ||
    !Array.isArray(questionContent.options)
  ) {
    return (
      <div className="text-error">
        Нет данных для вопроса.
        <pre>{JSON.stringify(questionContent, null, 2)}</pre>
      </div>
    );
  }

  const [selectOptions, setSelectedOptions] = useState<string>("");
  const [isSolution, setIsSolution] = useState<boolean>(false);
  const [SolutionError, setSolutionError] = useState<boolean>(false);
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
      <ReactMarkdown>{questionContent.question}</ReactMarkdown>
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
            <label className="ml-2" htmlFor="">
              {opt}
            </label>
          </div>
        </div>
      ))}
      <div className="mt-3">
        <button
          onClick={handleSubmit}
          disabled={isSolution}
          className="btn btn-primary mt-2"
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
