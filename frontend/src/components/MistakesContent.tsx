import ReactMarkdown from "react-markdown";

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
    <div className="overflow-auto">
      {mistakesContent.mistakes.map((item: any, idx: number) => {
        if (item.code) {
          const code = item.code;
          return (
            <div key={idx} className="mb-2">
              <div className="relative">
                <pre>
                  <code>{code.source}</code>
                  {code.language && (
                    <span className="absolute top-3 right-3 text-xs text-base-content/60">
                      {code.language}
                    </span>
                  )}
                </pre>
              </div>
              {code.explanation && (
                <div className="text-xs mt-1 text-base-content/70">
                  <ReactMarkdown>{code.explanation}</ReactMarkdown>
                </div>
              )}
            </div>
          );
        }
        if (item.text) {
          return (
            <div key={idx} className="mb-2">
              <ReactMarkdown>{item.text}</ReactMarkdown>
            </div>
          );
        }
        return (
          <div key={idx} className="text-error">
            <pre>{JSON.stringify(item, null, 2)}</pre>
          </div>
        );
      })}
    </div>
  );
}
