import { useCallback, useEffect, useRef, useState } from "react";

export function useReplay({ session, driver }) {
  const wsRef = useRef(null);
  const speedRef = useRef(4);
  const [data, setData] = useState([]);
  const [info, setInfo] = useState(null);
  const [status, setStatus] = useState("connecting");
  const [speed, setSpeedState] = useState(4);

  const connect = useCallback(() => {
    wsRef.current?.close();
    setData([]);
    setInfo(null);
    setStatus("connecting");

    const proto = window.location.protocol === "https:" ? "wss" : "ws";
    const url = `${proto}://${window.location.host}/ws/replay?session=${session}&driver=${driver}&speed=${speedRef.current}`;
    const ws = new WebSocket(url);
    wsRef.current = ws;
    const isCurrent = () => wsRef.current === ws; // ignore events from replaced sockets

    ws.onmessage = (e) => {
      if (!isCurrent()) return;
      const m = JSON.parse(e.data);
      if (m.type === "ready") {
        setInfo(m);
        setStatus("playing");
      } else if (m.type === "samples") {
        const firstT = m.data[0].t;
        // drop anything at or after the new batch: handles seeking backwards
        setData((prev) => prev.filter((d) => d.t < firstT).concat(m.data));
      } else if (m.type === "done") {
        setStatus("done");
      } else if (m.type === "error") {
        setStatus(`error: ${m.message}`);
      }
    };

    ws.onclose = () => {
      if (isCurrent()) {
        setStatus((s) => (s === "done" || s.startsWith("error") ? s : "closed"));
      }
    };
  }, [session, driver]);

  useEffect(() => {
    connect();
    return () => {
      wsRef.current?.close();
      wsRef.current = null;
    };
  }, [connect]);

  const send = useCallback((cmd) => {
    const ws = wsRef.current;
    if (ws && ws.readyState === WebSocket.OPEN) ws.send(JSON.stringify(cmd));
  }, []);

  const play = () => {
    send({ action: "play" });
    setStatus((s) => (s === "paused" ? "playing" : s));
  };
  const pause = () => {
    send({ action: "pause" });
    setStatus((s) => (s === "playing" ? "paused" : s));
  };
  const seek = (t) => send({ action: "seek", value: t });
  const setSpeed = (v) => {
    speedRef.current = v;
    setSpeedState(v);
    send({ action: "speed", value: v });
  };

  return { data, info, status, speed, play, pause, seek, setSpeed, restart: connect };
}