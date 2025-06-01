import { useState, useEffect, useRef, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { usePersistentWebSocket } from "../hooks/usePersistentWebSocket";

type Message = {
  id?: string;
  text: string;
  who: "user" | "bot";
  type?: string;
};

export default function HomePage() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [resetCount, setResetCount] = useState(0);
  const [status, setStatus] = useState(() => localStorage.getItem("status") || "chating");

  const navigate = useNavigate();

  const chatRef = useRef<HTMLDivElement | null>(null);
  const inputRef = useRef<HTMLInputElement | null>(null);
  const seenRef = useRef<Set<string>>(new Set());

  const addIfNew = useCallback((msg: Message) => {
    if (!msg.id || !seenRef.current.has(msg.id)) {
      if (msg.id) seenRef.current.add(msg.id);
      setMessages((prev) => [...prev, msg]);
    }
  }, []);

  const buildWsUrl = useCallback(() => {
    const wsHost = import.meta.env.VITE_WS_HOST;
    return `${wsHost}/ws/audit`;
  }, []);

  const handleWsMessage = useCallback(
    (event: MessageEvent, ws: WebSocket) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === "session_info") {
          if (Array.isArray(data.messages)) {
            data.messages.forEach((m: Message) => {
              if (m.id) seenRef.current.add(m.id);
            });
            setMessages(data.messages);
            const last = data.messages.at(-1);
            if (last?.type === "course_created_done") {
              setStatus("course_created");
              localStorage.setItem("status", "course_created");
              ws.close();
            }
          }
          if (typeof data.reset_count === "number")
            setResetCount(data.reset_count);
          return;
        }
        if (data.type === "course_created_start") {
          setStatus("course_creating");
          localStorage.setItem("status", "course_creating");
        }
        if (data.type === "course_created_done") {
          setStatus("course_created");
          localStorage.setItem("status", "course_created");
          ws.close();
          return;
        }
        if (!data.who || (data.who !== "user" && data.who !== "bot"))
          data.who = "bot";
        addIfNew(data);
        setInput("");
      } catch {
        addIfNew({ text: event.data, who: "bot", type: "chat" });
        setInput("");
      }
    },
    [addIfNew],
  );

  const { connected, send, reconnect } = usePersistentWebSocket(
    buildWsUrl,
    handleWsMessage,
    {
      shouldReconnect: status !== "course_created",
      reconnectDelay: 2000,
    },
  );

  useEffect(() => {
    if (chatRef.current)
      chatRef.current.scrollTop = chatRef.current.scrollHeight;
  }, [messages]);

  const handleReset = async () => {
    await fetch(`${import.meta.env.VITE_API_HOST}/api/v1/audit/reset-chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    });
    setMessages([]);
    setInput("");
    setStatus("chating");
    localStorage.setItem("status", "chating");
    reconnect();
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && connected) {
      const msg: Message = { text: input.trim(), who: "user", type: "chat" };
      addIfNew(msg);
      send(JSON.stringify(msg));
      setInput("");
    }
  };

  const lastMsg = messages.at(-1);
  const canSend =
    connected &&
    !messages.some((m) => m.type === "system") &&
    !messages.some((m) => m.type === "audit_done") &&
    (messages.length === 0 ||
      (lastMsg?.who === "bot" && lastMsg.type === "chat")) &&
    status === "chating"

  useEffect(() => {
    const last = messages.at(-1);
    if (last?.who === "bot" && last.type === "chat") {
      inputRef.current?.focus();
    }
  }, [messages]);

  useEffect(() => {
    if (connected && status === "chating") {
      inputRef.current?.focus();
    }
  }, [connected, status]);

  useEffect(() => {
    localStorage.setItem("status", status);
  }, [status]);

  const placeholder =
    !connected && status === "chating" && messages.length
      ? "Восстанавливаем соединение..."
      : status === "course_created"
        ? "Курс создан! Получите его ниже."
        : status !== "chating" && messages.length
          ? "Ждём ответа бота..."
          : messages.length
            ? "Введите ответ..."
            : "Чему бы вы хотели научиться?";

  const maxResets = 3;
  const resetsLeft = maxResets - resetCount;

  return (
    <div className="min-h-screen flex flex-col items-center bg-base-100">
      <div className="w-full max-w-md flex flex-col gap-4 flex-1 pt-8">
        <h1 className="text-5xl font-bold text-center mb-2 text-base-content">
          Твоё <span className="text-primary">развитие</span>
        </h1>
        <p className="text-xl text-center text-base-content/70 mb-4">
          Без воды. Без давления. Всё по-твоему.
        </p>

        <form className="flex gap-2 w-full" onSubmit={handleSubmit}>
          <label className="input input-bordered input-lg w-full flex items-center gap-2 bg-base-200 border-base-300 text-base-content">
            <input
              ref={inputRef}
              type="text"
              placeholder={placeholder}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={status !== "chating" || !canSend}
              className="bg-base-200 text-base-content flex-1"
            />
            <kbd className="kbd kbd-sm text-base-content bg-base-100 border-base-300">
              Enter
            </kbd>
          </label>
        </form>

        {messages.length > 0 && (
          <div
            ref={chatRef}
            className="flex-1 overflow-y-auto rounded-lg shadow bg-base-200 p-4 text-base-content"
            style={{ minHeight: 200, maxHeight: 400 }}
          >
            {messages
              .filter((m) => m.type === "chat")
              .map((m, i) => (
                <div
                  key={m.id || i}
                  className={`chat ${m.who === "user" ? "chat-end" : "chat-start"}`}
                >
                  <div
                    className={`chat-bubble ${m.who === "user" ? "chat-bubble-primary" : "bg-base-100 text-base-content border border-base-300"}`}
                  >
                    {m.text}
                  </div>
                </div>
              ))}
          </div>
        )}

        <div className="flex gap-2 justify-center">
          {messages.length > 0 && (
            <button className="btn btn-secondary mt-4" onClick={handleReset} disabled={status !== "chating" || resetsLeft <= 0}>
              Сбросить чат
            </button>
          )}
          {status === "course_created" && (
            <button
              className="btn btn-primary mt-4"
              onClick={() => navigate("/courses")}
            >
              Получить курс
            </button>
          )}
        </div>

        {messages.length > 0 && (
          <div className="text-sm text-base-content/60 mt-2 text-center">
            Осталось сбросов: {resetsLeft}
          </div>
        )}
      </div>
    </div>
  );
}
