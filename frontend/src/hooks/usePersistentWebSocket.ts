import { useCallback, useEffect, useRef, useState } from "react";

interface Options {
  shouldReconnect?: boolean;
  reconnectDelay?: number;
  onClose?: (e: CloseEvent) => void;
}

export function usePersistentWebSocket(
  url: string,
  onMessage: (e: MessageEvent, ws: WebSocket) => void,
  opts: Options = {},
) {
  const { shouldReconnect = true, reconnectDelay = 2000, onClose } = opts;

  const shouldReconnectRef = useRef(shouldReconnect);
  useEffect(() => {
    shouldReconnectRef.current = shouldReconnect;
  }, [shouldReconnect]);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimer = useRef<number | null>(null);
  const lastUrlRef = useRef<string>("");

  const [connected, setConnected] = useState(false);

  const hasActiveSocket = () =>
    wsRef.current &&
    (wsRef.current.readyState === WebSocket.OPEN ||
      wsRef.current.readyState === WebSocket.CONNECTING);

  const connect = useCallback(() => {
    if (wsRef.current) {
      try {
        wsRef.current.onclose = null;
        wsRef.current.close();
      } catch {}
    }

    if (!url) {
      setConnected(false);
      return;
    }

    if (url === lastUrlRef.current && hasActiveSocket()) {
      return;
    }
    lastUrlRef.current = url;

    if (reconnectTimer.current) {
      clearTimeout(reconnectTimer.current);
      reconnectTimer.current = null;
    }

    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      setConnected(true);
    };

    ws.onmessage = (e) => {
      onMessage(e, ws);
    };

    ws.onerror = (e) => {
      console.error("WS error", e);
      ws.close();
    };

    ws.onclose = (e) => {
      setConnected(false);
      if (wsRef.current === ws) {
        wsRef.current = null;
      }
      if (typeof onClose === "function") {
        onClose(e);
      }
      if (e.code === 4000 || e.code === 4001) {
        return;
      }
      if (shouldReconnectRef.current) {
        reconnectTimer.current = window.setTimeout(connect, reconnectDelay);
      }
    };
  }, [url, onMessage, reconnectDelay, onClose]);

  useEffect(() => {
    connect();

    return () => {
      if (reconnectTimer.current) {
        clearTimeout(reconnectTimer.current);
      }
      if (wsRef.current) {
        try {
          wsRef.current.close();
        } catch {}
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [url]);

  const reconnect = useCallback(() => {
    if (shouldReconnectRef.current) {
      connect();
    }
  }, [connect]);

  const send = useCallback(
    (data: string | Blob | ArrayBuffer | ArrayBufferView) => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(data);
      }
    },
    [],
  );

  return { ws: wsRef.current, connected, send, reconnect };
}
