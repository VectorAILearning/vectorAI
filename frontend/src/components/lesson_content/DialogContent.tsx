import { HiUser, HiAcademicCap } from "react-icons/hi";

interface DialogContentProps {
  dialogContent: any;
}

export default function DialogContent({ dialogContent }: DialogContentProps) {
  if (!dialogContent || !Array.isArray(dialogContent.dialog)) {
    return (
      <div className="text-error">
        Некорректный формат dialog:{" "}
        <pre>{JSON.stringify(dialogContent, null, 2)}</pre>
      </div>
    );
  }

  return (
    <div>
      {dialogContent.dialog.map((rep: any, idx: number) => (
        <div
          key={idx}
          className={`chat ${rep.role === "ученик" ? "chat-end" : "chat-start"}`}
        >
          <div className="chat-image avatar">
            <div className="rounded-full bg-base-200 flex items-center justify-center">
              {rep.role === "ученик" ? (
                <HiUser className="w-12 h-12 text-base-content/70 p-1.5" />
              ) : (
                <HiAcademicCap className="w-12 h-12 text-base-content/70 p-1.5" />
              )}
            </div>
          </div>
          <div className="chat-header">
            {rep.role === "ученик" ? "ученик" : "преподаватель"}
          </div>
          <div className="chat-bubble bg-base-200 text-base-content">
            {rep.text}
          </div>
        </div>
      ))}
    </div>
  );
}
