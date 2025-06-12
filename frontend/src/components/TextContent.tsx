import ReactMarkdown from "react-markdown";

interface TextContentProps {
  textContent: any;
}

export default function TextContent({ textContent }: TextContentProps) {
  if (!textContent || typeof textContent.text !== "string") {
    return (
      <div className="text-error">
        Некорректный формат text:{" "}
        <pre>{JSON.stringify(textContent, null, 2)}</pre>
      </div>
    );
  }
  return <ReactMarkdown>{textContent.text}</ReactMarkdown>;
}
