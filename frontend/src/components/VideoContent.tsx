interface VideoContentProps {
  videoContent: any;
}

export default function VideoContent({ videoContent }: VideoContentProps) {
  if (
    !videoContent ||
    typeof videoContent.title !== "string" ||
    typeof videoContent.description !== "string" ||
    typeof videoContent.url !== "string"
  ) {
    return (
      <div className="text-error">
        Некорректный формат video:{" "}
        <pre>{JSON.stringify(videoContent, null, 2)}</pre>
      </div>
    );
  }

  return (
    <div className="bg-base-200 p-2 rounded">
      <div className="font-bold mb-1">{videoContent.title}</div>
      <div className="mb-2 text-base-content/70">
        {videoContent.description}
      </div>
      <video controls className="w-full max-h-96 rounded">
        <source src={videoContent.url} type="video/mp4" />
        Ваш браузер не поддерживает видео.
      </video>
    </div>
  );
}
