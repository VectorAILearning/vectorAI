import React from "react";
import ReactMarkdown from "react-markdown";

export default function TextContent({ textContent }) {
  return (
    <div>
      <ReactMarkdown>{textContent.text}</ReactMarkdown>
    </div>
  );
}
