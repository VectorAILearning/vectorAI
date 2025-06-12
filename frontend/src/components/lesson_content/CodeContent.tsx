import { useRef, useState } from "react";
import Editor from "@monaco-editor/react";
import type * as monacoEditor from "monaco-editor";

interface CodeContentProps {
  codeContent: {
    source: string;
    language?: string;
    executable?: boolean;
    explanation?: string;
  };
}

export default function CodeContent({ codeContent }: CodeContentProps) {
  const [code, setCode] = useState(codeContent.source);
  const editorRef = useRef<any>(null);
  const [height, setHeight] = useState(300);

  const handleEditorMount = (
    editor: monacoEditor.editor.IStandaloneCodeEditor,
    monaco: typeof monacoEditor
  ) => {
    editorRef.current = editor;
    const contentHeight = editor.getContentHeight();
    setHeight(contentHeight + 20);

    editor.onDidContentSizeChange(() => {
      const newHeight = editor.getContentHeight();
      setHeight(newHeight + 20);
    });
    monaco.editor.defineTheme("custom-dark", {
      base: "vs-dark",
      inherit: true,
      rules: [],
      colors: {
        "editor.background": "#191e24",
      },
    });
  
    monaco.editor.setTheme("custom-dark");
  };

  return (
    <div className="mb-4">
      <div className="relative rounded-md border border-base-content/10 p-1">
        <Editor
          value={code}
          language={codeContent.language || "javascript"}
          onChange={(val) => setCode(val || "")}
          theme="vs-dark"
          onMount={handleEditorMount}
          options={{
            readOnly: !codeContent.executable,
            fontSize: 14,
            minimap: { enabled: false },
            scrollBeyondLastLine: false,
            wordWrap: "on",
            lineNumbers: "on"
          }}
          height={height}
        />
        {codeContent.language && (
          <div className="absolute top-1 right-3 text-xs text-base-content/50 bg-base-300 px-2 py-1 rounded">
            {codeContent.language}
          </div>
        )}
      </div>

      {codeContent.explanation && (
        <div className="text-sm mt-2 text-base-content/70">
          {codeContent.explanation}
        </div>
      )}
    </div>
  );
}
