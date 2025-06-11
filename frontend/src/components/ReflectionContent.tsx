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
      <span className="font-semibold">Рефлексия:</span>{" "}
      {reflectionContent.prompt}
    </div>
  );
}
