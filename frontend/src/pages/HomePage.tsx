import { useState, useEffect, useRef, useCallback } from "react";
import { useDispatch } from "react-redux";
import { setSessionId } from "../store/sessionSlice";
import { useNavigate } from "react-router-dom";
import { usePersistentWebSocket } from "../hooks/usePersistentWebSocket";

type Message = {
  text: string;
  who: "user" | "bot";
  type?: string;
};

export default function HomePage() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [resetCount, setResetCount] = useState(0);
  const [courseCreated, setCourseCreated] = useState(false);
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const chatRef = useRef<HTMLDivElement | null>(null);
  const inputRef = useRef<HTMLInputElement | null>(null);

  const buildWsUrl = useCallback(() => {
    const wsHost = import.meta.env.VITE_WS_HOST;
    const sessionId = localStorage.getItem("session_id");
    return sessionId
      ? `${wsHost}/ws/audit?session_id=${sessionId}`
      : `${wsHost}/ws/audit`;
  }, []);

  const handleWsMessage = useCallback(
    (event: MessageEvent, ws: WebSocket) => {
      let data;
      try {
        data = JSON.parse(event.data);
        if (data.type === "session_info") {
          if (typeof data.session_id === "string") {
            localStorage.setItem("session_id", data.session_id);
            dispatch(setSessionId(data.session_id));
          }
          if (Array.isArray(data.messages)) {
            setMessages(data.messages);
            const lastMsg = data.messages[data.messages.length - 1];
            if (lastMsg?.type === "course_created_done") {
              setCourseCreated(true);
            } else {
              setCourseCreated(false);
            }
          }
          if (typeof data.reset_count === "number")
            setResetCount(data.reset_count);
          return;
        }
        if (data.type === "course_created_done") {
          setCourseCreated(true);
          ws.close();
          return;
        }
        if (!data.who || (data.who !== "user" && data.who !== "bot")) {
          data.who = "bot";
        }
      } catch {
        data = { text: event.data, who: "bot", type: "chat" };
      }
      setMessages((prev) => [...prev, data]);
      setInput("");
    },
    [dispatch],
  );

  const { connected, send, reconnect } = usePersistentWebSocket(
    buildWsUrl,
    handleWsMessage,
    { shouldReconnect: !courseCreated, reconnectDelay: 2000 },
  );

  useEffect(() => {
    if (chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight;
    }
  }, [messages]);

  const handleReset = async () => {
    const sessionId = localStorage.getItem("session_id");
    if (!sessionId) return;
    const apiHost = import.meta.env.VITE_API_HOST;
    await fetch(`${apiHost}/api/v1/audit/reset-chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId }),
    });
    setMessages([]);
    setInput("");
    setCourseCreated(false);
    reconnect();
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && connected) {
      const msg = { text: input.trim(), who: "user" as const, type: "chat" };
      setMessages((prev) => [...prev, msg]);
      send(JSON.stringify(msg));
      setInput("");
    }
  };

  const lastMsg = messages[messages.length - 1];
  const canSend =
    connected &&
    !messages.some((m) => m.type === "system") &&
    !messages.some((m) => m.type === "audit_done") &&
    (messages.length === 0 ||
      (lastMsg?.who === "bot" && lastMsg.type === "chat"));

  useEffect(() => {
    if (canSend && inputRef.current) {
      inputRef.current.focus();
    }
  }, [canSend]);

  let inputPlaceholder = "";
  if (!connected && !courseCreated && messages.length > 0) {
    inputPlaceholder = "Восстанавливаем соединение...";
  } else if (courseCreated) {
    inputPlaceholder = "Курс создан! Получите его ниже.";
  } else if (!canSend && messages.length > 0) {
    inputPlaceholder = "Ждём ответа бота...";
  } else if (messages.length === 0) {
    inputPlaceholder = "Чему бы вы хотели научиться?";
  } else {
    inputPlaceholder = "Введите ответ...";
  }

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
              placeholder={inputPlaceholder}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={!canSend}
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
              .filter((msg: Message) => msg.type === "chat")
              .map((msg: Message, idx: number) => (
                <div
                  key={idx}
                  className={`chat ${msg.who === "user" ? "chat-end" : "chat-start"}`}
                >
                  <div
                    className={`chat-bubble ${msg.who === "user" ? "chat-bubble-primary" : "bg-base-100 text-base-content border border-base-300"}`}
                  >
                    {msg.text}
                  </div>
                </div>
              ))}
          </div>
        )}
        <div className="flex gap-2 justify-center">
          {messages.length > 0 && (
            <button className="btn btn-secondary mt-4" onClick={handleReset}>
              Сбросить чат
            </button>
          )}
          {courseCreated && (
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
            Количество сбросов: {resetCount}
          </div>
        )}
      </div>
    </div>
  );
}
