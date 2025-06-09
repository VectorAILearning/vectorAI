import React from "react";

export default function DialogContent({ dialogContent }) {
  return (
    <div>
      {dialogContent.dialog?.map((rep: any, i: number) => (
        <div
          key={i}
          className={`chat ${rep.role === "ученик" ? "chat-end" : "chat-start"}`}
        >
          <div className="chat-image avatar">
            <div className="w-10 rounded-full">
              <img
                alt="Tailwind CSS chat bubble component"
                src={
                  rep.role === "ученик"
                    ? "https://img.daisyui.com/images/profile/demo/anakeen@192.webp"
                    : "https://img.daisyui.com/images/profile/demo/kenobee@192.webp"
                }
              />
            </div>
          </div>
          <div className="chat-header">
            {rep.role === "ученик" ? "ученик" : "преподаватель"}
          </div>
          <div className="chat-bubble">{rep.text}</div>
        </div>
      ))}
    </div>
  );
}
