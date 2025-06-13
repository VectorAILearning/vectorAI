import ReactMarkdown from "react-markdown";

interface TestContentProps {
  testContent?: any;
}

export default function TestContent({ testContent }: TestContentProps) {
  if (
    !testContent ||
    typeof testContent !== "object" ||
    typeof testContent.question !== "string"
  ) {
    return (
      <div className="text-error">
        Нет данных для теста.
        <pre>{JSON.stringify(testContent, null, 2)}</pre>
      </div>
    );
  }

  return <ReactMarkdown>{testContent.question}</ReactMarkdown>;
}
