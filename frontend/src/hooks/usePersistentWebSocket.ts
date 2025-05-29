import { useCallback, useEffect, useRef, useState } from "react";

interface Options {
  shouldReconnect?: boolean;
  reconnectDelay?: number;
}

export function usePersistentWebSocket(
  buildUrl: () => string,
  onMessage: (e: MessageEvent, ws: WebSocket) => void,
  opts: Options = {},
) {
  const { shouldReconnect = true, reconnectDelay = 2000 } = opts;

  const shouldReconnectRef = useRef(shouldReconnect);
  useEffect(() => {
    shouldReconnectRef.current = shouldReconnect;
  }, [shouldReconnect]);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimer = useRef<number | null>(null);
  const [connected, setConnected] = useState(false);

  const connect = useCallback(() => {
    if (reconnectTimer.current) {
      clearTimeout(reconnectTimer.current);
      reconnectTimer.current = null;
    }

    const url = buildUrl();
    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => setConnected(true);
    ws.onmessage = (e) => onMessage(e, ws);
    ws.onerror = (e) => {
      if (ws.readyState !== WebSocket.CLOSED) {
        console.error("WS error", e);
      }
    };
    ws.onclose = () => {
      setConnected(false);
      if (shouldReconnectRef.current) {
        reconnectTimer.current = window.setTimeout(connect, reconnectDelay);
      }
    };
  }, [buildUrl, onMessage, reconnectDelay]);

  useEffect(() => {
    connect();
    return () => {
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);

      const ws = wsRef.current;
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const reconnect = useCallback(() => {
    if (shouldReconnectRef.current) connect();
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
