import ReactMarkdown from "react-markdown";

interface ExamplesContentProps {
  examplesContent: any;
}

export default function ExamplesContent({
  examplesContent,
}: ExamplesContentProps) {
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
                  <div>{code.explanation}</div>
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
