import React, { useState } from "react";
import { HiOutlineClipboard } from "react-icons/hi";

export default function CopyButton({
  value,
  title = "Скопировать",
  className = "",
}: {
  value: string;
  title?: string;
  className?: string;
}) {
  const [copied, setCopied] = useState(false);

  const handleCopy = (e: React.MouseEvent) => {
    e.stopPropagation();
    navigator.clipboard.writeText(value);
    setCopied(true);
    setTimeout(() => setCopied(false), 1000);
  };

  return (
    <span className="relative inline-block">
      <button
        className={`btn btn-xs btn-ghost text-base-content ${className}`}
        title={title}
        onClick={handleCopy}
        tabIndex={-1}
        type="button"
      >
        <HiOutlineClipboard className="w-4 h-4" />
      </button>
      <span
        className={`absolute -top-6 left-1/2 -translate-x-1/2 px-2 py-1 text-xs rounded bg-base-200 text-base-content shadow border border-base-300 z-10 whitespace-nowrap transition-opacity duration-300 ${copied ? "opacity-100" : "opacity-0 pointer-events-none"}`}
      >
        Скопировано!
      </span>
    </span>
  );
}
