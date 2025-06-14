import { useState, useEffect, useRef, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { usePersistentWebSocket } from "../hooks/usePersistentWebSocket";
import axiosInstance from "../api/axiosInstance.ts";
import { useAppSelector } from "../store/index.ts";

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
  const [status, setStatus] = useState<string>("chating");
  const [isSessionReady, setIsSessionReady] = useState(false);
  const [wsTimestamp, setWsTimestamp] = useState(Date.now());
  const [botOptions, setBotOptions] = useState<string[] | null>(null);
  const navigate = useNavigate();
  const chatRef = useRef<HTMLDivElement | null>(null);
  const inputRef = useRef<HTMLInputElement | null>(null);
  const token = useAppSelector((state) => state.auth.token);

  const addIfNew = useCallback((msg: Message) => {
    setMessages((prev) => {
      if (msg.id && prev.some((m) => m.id === msg.id)) return prev;
      if (
        !msg.id &&
        prev.length &&
        prev[prev.length - 1].text === msg.text &&
        prev[prev.length - 1].type === msg.type
      )
        return prev;
      return [...prev, msg];
    });
  }, []);

  const readyToConnect = isSessionReady;
  const wsHost = import.meta.env.VITE_WS_HOST;
  const wsUrl =
    readyToConnect && token
      ? `${wsHost}/ws/audit?token=${encodeURIComponent(token)}`
      : `${wsHost}/ws/audit`;

  const handleWsMessage = useCallback(
    (event: MessageEvent, ws: WebSocket) => {
      try {
        const data = JSON.parse(event.data);

        if (data.type === "duplicate_connection") {
          ws.close(4000);
          return;
        }

        if (data.type === "course_created_start") {
          setStatus("course_creating");
        }
        if (data.type === "course_generation_done") {
          setStatus("course_generation_done");
          ws.close();
          return;
        }
        if (!data.who || (data.who !== "user" && data.who !== "bot"))
          data.who = "bot";
        addIfNew(data);
        setInput("");
        if (data.who === "bot" && data.type === "chat") {
          try {
            const parsed = JSON.parse(data.text);
            if (parsed.options && Array.isArray(parsed.options)) {
              setBotOptions(parsed.options);
            } else {
              setBotOptions(null);
            }
          } catch {
            setBotOptions(null);
          }
        } else {
          setBotOptions(null);
        }
      } catch {
        addIfNew({ text: event.data, who: "bot", type: "chat" });
        setInput("");
        setBotOptions(null);
      }
    },
    [addIfNew],
  );

  const updateSessionState = useCallback((data: any) => {
    setMessages(Array.isArray(data.messages) ? data.messages : []);
    setResetCount(typeof data.reset_count === "number" ? data.reset_count : 0);
    setStatus(typeof data.status === "string" ? data.status : "chating");
    setIsSessionReady(true);
    if (Array.isArray(data.messages)) {
      const last = data.messages.at(-1);
      if (last && last.who === "bot" && last.type === "chat") {
        try {
          const parsed = JSON.parse(last.text);
          if (parsed.options && Array.isArray(parsed.options)) {
            setBotOptions(parsed.options);
          } else {
            setBotOptions(null);
          }
        } catch {
          setBotOptions(null);
        }
      } else {
        setBotOptions(null);
      }
    } else {
      setBotOptions(null);
    }
  }, []);

  const resetSessionState = useCallback(() => {
    setMessages([]);
    setInput("");
    setStatus("chating");
    setIsSessionReady(false);
    setTimeout(() => {
      setIsSessionReady(true);
      setWsTimestamp(Date.now());
      reconnect();
      focusInput();
    }, 0);
  }, []);

  const focusInput = useCallback(() => {
    inputRef.current?.focus();
  }, []);

  const handleWsClose = useCallback((e: CloseEvent) => {
    if (e.code === 4001) {
      setStatus("no_subscription");
    }
  }, []);

  const { connected, send, reconnect } = usePersistentWebSocket(
    wsUrl,
    handleWsMessage,
    {
      shouldReconnect:
        status !== "course_generation_done" &&
        status !== "no_subscription" &&
        readyToConnect,
      reconnectDelay: 2000,
      onClose: handleWsClose,
    },
  );

  useEffect(() => {
    if (chatRef.current)
      chatRef.current.scrollTop = chatRef.current.scrollHeight;
  }, [messages]);

  const handleReset = async () => {
    try {
      const res = await axiosInstance.post("/audit/reset-chat", {});
      const data = res.data;
      setIsSessionReady(false);
      setInput("");
      setTimeout(() => {
        updateSessionState(data);
        setWsTimestamp(Date.now());
        reconnect();
        focusInput();
      }, 0);
    } catch {
      resetSessionState();
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && connected) {
      const msg: Message = { text: input.trim(), who: "user", type: "chat" };
      addIfNew(msg);
      send(JSON.stringify(msg));
      setInput("");
      setBotOptions(null);
    }
  };

  const lastMsg = messages.at(-1);
  const canSend =
    connected &&
    !messages.some((m) => m.type === "system") &&
    !messages.some((m) => m.type === "audit_done") &&
    (messages.length === 0 ||
      (lastMsg?.who === "bot" && lastMsg.type === "chat")) &&
    status === "chating";

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
    if (status === "chating" && messages.length === 0) {
      inputRef.current?.focus();
    }
  }, [status, messages]);

  const placeholder =
    status === "no_subscription"
      ? "Пожалуйста, авторизуйтесь или купите подписку, чтобы продолжить."
      : !connected && status === "chating"
        ? "Восстанавливаем соединение..."
        : status === "course_generation_done"
          ? "Курс создан! Получите его ниже."
          : status !== "chating" && messages.length
            ? "Ждём ответа бота..."
            : messages.length
              ? "Введите ответ..."
              : "Чему бы вы хотели научиться?";

  const maxResets = 3;
  const resetsLeft = maxResets - resetCount;

  const checkSubscription = import.meta.env.VITE_CHECK_SUBSCRIPTION !== "false";

  useEffect(() => {
    (async () => {
      try {
        const res = await axiosInstance.get("/audit/session-info");
        const data = res.data;
        updateSessionState(data);
      } catch {}
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const renderBotMessage = useCallback((m: Message) => {
    if (m.who === "bot" && m.type === "chat") {
      try {
        const parsed = JSON.parse(m.text);
        return parsed.question ?? m.text;
      } catch {
        return m.text;
      }
    }
    return m.text;
  }, []);

  return (
    <div className="min-h-screen flex flex-col items-center bg-base-100">
      <div className="w-full max-w-lg flex flex-col gap-4 flex-1 pt-8">
        <h1 className="text-5xl font-bold text-center mb-2 text-base-content">
          Твоё <span className="text-primary">развитие</span>
        </h1>
        <p className="text-xl text-center text-base-content/70 mb-4">
          Без воды. Без давления. Всё по-твоему.
        </p>

        <form className="flex gap-2 w-full" onSubmit={handleSubmit}>
          <label
            className="input input-bordered input-lg w-full flex items-center gap-2 
            bg-base-200 border-base-300 text-base-content"
          >
            <input
              ref={inputRef}
              type="text"
              placeholder={placeholder}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={status !== "chating" || !canSend}
              className="text-base-content flex-1"
            />
            <kbd className="kbd text-base-content">Enter</kbd>
          </label>
        </form>
        {botOptions && (
          <div className="flex flex-row flex-wrap gap-2">
            {botOptions.map((opt, idx) => (
              <div
                key={idx}
                className="cursor-pointer bg-primary rounded px-3 py-1 hover:scale-105 \
                transition text-xs w-auto whitespace-pre-line text-white"
                onClick={() => {
                  setInput(opt);
                  inputRef.current?.focus();
                }}
              >
                {opt}
              </div>
            ))}
          </div>
        )}

        {messages.length > 0 && (
          <div
            ref={chatRef}
            className="flex-1 overflow-y-auto rounded-lg shadow bg-base-200 p-4 text-base-content"
            style={{ minHeight: 200, maxHeight: 400 }}
          >
            {messages
              .filter((m) => m.type === "chat" || m.type === "chat_info")
              .map((m, i) => (
                <div
                  key={m.id || i}
                  className={`chat ${m.who === "user" ? "chat-end" : "chat-start"}`}
                >
                  <div
                    className={`chat-bubble ${m.who === "user" ? "chat-bubble-primary" : "bg-base-100 text-base-content border border-base-300"}`}
                  >
                    {renderBotMessage(m)}
                  </div>
                </div>
              ))}
          </div>
        )}

        <div className="flex gap-2 justify-center">
          {messages.length > 0 && (
            <button
              className="btn btn-secondary mt-4"
              onClick={handleReset}
              disabled={
                checkSubscription && (status !== "chating" || resetsLeft <= 0)
              }
            >
              Сбросить чат
            </button>
          )}
          {status === "course_generation_done" && (
            <button
              className="btn btn-primary mt-4"
              onClick={() => navigate("/course")}
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
