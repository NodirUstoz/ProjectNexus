/**
 * Custom hook for WebSocket connections with auto-reconnect,
 * used for real-time task board updates and collaborative features.
 */

import { useCallback, useEffect, useRef, useState } from 'react';

interface UseWebSocketOptions {
  url: string;
  onMessage?: (data: any) => void;
  onOpen?: () => void;
  onClose?: () => void;
  reconnectInterval?: number;
  maxRetries?: number;
  autoConnect?: boolean;
}

interface UseWebSocketReturn {
  isConnected: boolean;
  lastMessage: any;
  sendMessage: (data: any) => void;
  connect: () => void;
  disconnect: () => void;
}

export function useWebSocket({
  url,
  onMessage,
  onOpen,
  onClose,
  reconnectInterval = 3000,
  maxRetries = 10,
  autoConnect = true,
}: UseWebSocketOptions): UseWebSocketReturn {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<any>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const retriesRef = useRef(0);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout>>();

  const connect = useCallback(() => {
    const token = localStorage.getItem('access_token');
    if (!token) return;

    const wsUrl = `${url}${url.includes('?') ? '&' : '?'}token=${token}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      setIsConnected(true);
      retriesRef.current = 0;
      onOpen?.();
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setLastMessage(data);
        onMessage?.(data);
      } catch {
        // Non-JSON message, ignore
      }
    };

    ws.onclose = () => {
      setIsConnected(false);
      wsRef.current = null;
      onClose?.();

      // Auto-reconnect with exponential backoff
      if (retriesRef.current < maxRetries) {
        const delay = reconnectInterval * Math.pow(1.5, retriesRef.current);
        reconnectTimeoutRef.current = setTimeout(() => {
          retriesRef.current += 1;
          connect();
        }, delay);
      }
    };

    ws.onerror = () => {
      ws.close();
    };

    wsRef.current = ws;
  }, [url, onMessage, onOpen, onClose, reconnectInterval, maxRetries]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    retriesRef.current = maxRetries; // Prevent reconnection
    wsRef.current?.close();
    wsRef.current = null;
    setIsConnected(false);
  }, [maxRetries]);

  const sendMessage = useCallback((data: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    }
  }, []);

  useEffect(() => {
    if (autoConnect) {
      connect();
    }
    return () => {
      disconnect();
    };
  }, [autoConnect, connect, disconnect]);

  return { isConnected, lastMessage, sendMessage, connect, disconnect };
}
