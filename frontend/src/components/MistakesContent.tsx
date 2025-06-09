import React from "react";

export default function MistakesContent({ mistakesContent }) {
  return (
    <div>
      {mistakesContent.mistakes.map((content) => (
        <p>{content}</p>
      ))}
    </div>
  );
}
