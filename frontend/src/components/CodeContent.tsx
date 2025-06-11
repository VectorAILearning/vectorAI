interface CodeContentProps {
  codeContent: {
    source: string;
    language?: string;
    executable?: boolean;
    explanation?: string;
  };
}

export default function CodeContent({ codeContent }: CodeContentProps) {
  if (!codeContent || typeof codeContent.source !== "string") {
    return (
      <div className="text-error">
        Некорректный формат code:{" "}
        <pre>{JSON.stringify(codeContent, null, 2)}</pre>
      </div>
    );
  }
  return (
    <div className="overflow-auto">
      <div className="mb-2">
        <div className="relative">
          <pre className="bg-base-200 p-4 rounded-lg text-sm overflow-x-auto break-words whitespace-pre-wrap font-mono">
            <code>{codeContent.source}</code>
            {codeContent.language && (
              <span className="absolute top-2 right-3 text-xs text-base-content/60">
                {codeContent.language}
              </span>
            )}
          </pre>
        </div>

        {codeContent.explanation && (
          <div className="text-xs mt-2 text-base-content/70">
            {codeContent.explanation}
          </div>
        )}
      </div>
    </div>
  );
}
