import ReactMarkdown from "react-markdown";

interface ReflectionContentProps {
  reflectionContent: any;
}

export default function ReflectionContent({
  reflectionContent,
}: ReflectionContentProps) {
  if (!reflectionContent || typeof reflectionContent.prompt !== "string") {
    return (
      <div className="text-error">
        Некорректный формат reflection:{" "}
        <pre>{JSON.stringify(reflectionContent, null, 2)}</pre>
      </div>
    );
  }
  return (
    <div>
      <ReactMarkdown>{reflectionContent.prompt}</ReactMarkdown>
      <div className="mt-2">
        <textarea
          className="textarea w-full"
          placeholder="Ваш ответ"
        ></textarea>
        <div className="flex justify-center mt-2">
          <button className="btn btn-primary">Сохранить</button>
        </div>
      </div>
    </div>
  );
}
