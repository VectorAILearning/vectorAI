interface TestContentProps {
  testContent: any;
}

export default function TestContent({ testContent }: TestContentProps) {
  if (!testContent || typeof testContent.question !== "string") {
    return (
      <div className="text-error">
        Некорректный формат test:{" "}
        <pre>{JSON.stringify(testContent, null, 2)}</pre>
      </div>
    );
  }

  return <div className="bg-base-200 p-2 rounded">{testContent.question}</div>;
}
