import React from "react";

interface MistakesContentProps {
  mistakesContent: any;
}

export default function MistakesContent({
  mistakesContent,
}: MistakesContentProps) {
  if (!mistakesContent || !Array.isArray(mistakesContent.mistakes)) {
    return (
      <div className="text-error">
        Некорректный формат mistakes:{" "}
        <pre>{JSON.stringify(mistakesContent, null, 2)}</pre>
      </div>
    );
  }

  return (
    <div>
      {mistakesContent.mistakes.map((item: any, idx: number) => {
        // Старый формат: просто строка
        if (typeof item === "string") {
          return <p key={idx}>{item}</p>;
        }
        // Новый формат: объект с code
        if (item.code) {
          const code = item.code;
          return (
            <div key={idx} className="mb-2">
              <div className="font-bold text-xs mb-1">{code.language}</div>
              <pre className="bg-base-200 p-2 rounded">
                <code>{code.source}</code>
              </pre>
              {code.explanation && (
                <div className="text-xs mt-1 text-base-content/70">
                  {code.explanation}
                </div>
              )}
            </div>
          );
        }
        // Новый формат: объект с text
        if (item.text) {
          return (
            <div key={idx} className="mb-2">
              <div className="bg-base-200 p-2 rounded">{item.text}</div>
            </div>
          );
        }
        // Если структура не совпадает — выводим как есть
        return (
          <div key={idx} className="text-error">
            <pre>{JSON.stringify(item, null, 2)}</pre>
          </div>
        );
      })}
    </div>
  );
}
