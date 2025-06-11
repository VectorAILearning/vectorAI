import React, { useState } from "react";

interface PracticeContentProps {
  practiceContent: any;
}

export default function PracticeContent({
  practiceContent,
}: PracticeContentProps) {
  if (!practiceContent || typeof practiceContent.task !== "string") {
    return (
      <div className="text-error">
        Некорректный формат practice:{" "}
        <pre>{JSON.stringify(practiceContent, null, 2)}</pre>
      </div>
    );
  }

  const [isSolution, setIsSolution] = useState<boolean>(false);
  return (
    <div>
      <h6>{practiceContent.task}</h6>
      <div className="mt-[10px]">
        <textarea
          className="textarea w-full"
          placeholder="Ваше решение"
        ></textarea>
        <div className="flex justify-center mt-[10px]">
          <button className="btn btn-primary">Проверить</button>
        </div>
      </div>
    </div>
  );
}
