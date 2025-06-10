interface ExamplesContentProps {
  examplesContent: any;
}

export default function ExamplesContent({
  examplesContent,
}: ExamplesContentProps) {
  // Универсальный рендер для разных структур
  if (!examplesContent || !Array.isArray(examplesContent.examples)) {
    return (
      <div className="text-error">
        Некорректный формат examples:{" "}
        <pre>{JSON.stringify(examplesContent, null, 2)}</pre>
      </div>
    );
  }

  return (
    <div className="overflow-auto">
      {examplesContent.examples.map((item: any, idx: number) => {
        // Старый формат: просто строка
        if (typeof item === "string") {
          return (
            <pre key={idx}>
              <code>{item}</code>
            </pre>
          );
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
