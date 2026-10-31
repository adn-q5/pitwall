import TelemetryChart from "./components/TelemetryChart";
import { useReplay } from "./hooks/useReplay";
import "./App.css";

const SESSION = 9693; // Australia 2025 race
const DRIVER = 1; // Verstappen
const SPEEDS = [1, 4, 10];

function Stat({ label, value, unit }) {
  return (
    <div className="stat">
      <span className="stat-label">{label}</span>
      <span className="stat-value">
        {value ?? "–"}
        {value != null && unit ? <small> {unit}</small> : null}
      </span>
    </div>
  );
}

export default function App() {
  const r = useReplay({ session: SESSION, driver: DRIVER });
  const last = r.data[r.data.length - 1];
  const duration = r.info?.lap_duration ?? 90;
  const ready = r.info !== null;

  return (
    <main className="app">
      <header>
        <h1>PitWall</h1>
        <span className="status">{r.status}</span>
      </header>

      <section className="controls">
        <button onClick={r.play} disabled={!ready}>Play</button>
        <button onClick={r.pause} disabled={!ready}>Pause</button>
        {SPEEDS.map((s) => (
          <button
            key={s}
            className={r.speed === s ? "active" : ""}
            onClick={() => r.setSpeed(s)}
          >
            {s}x
          </button>
        ))}
        <button onClick={r.restart}>Replay lap</button>
      </section>

      <input
        className="scrub"
        type="range"
        min={0}
        max={duration}
        step={0.1}
        value={last?.t ?? 0}
        disabled={!ready || r.status === "done"}
        onChange={(e) => r.seek(Number(e.target.value))}
      />

      <section className="readouts">
        <Stat label="Speed" value={last?.speed} unit="km/h" />
        <Stat label="Gear" value={last?.gear} />
        <Stat label="Throttle" value={last?.throttle} unit="%" />
        <Stat label="RPM" value={last?.rpm} />
      </section>

      <TelemetryChart
        title="Speed (km/h)"
        data={r.data}
        duration={duration}
        yDomain={[0, 350]}
        lines={[{ key: "speed", color: "#4cc9f0" }]}
      />
      <TelemetryChart
        title="Throttle (green) and brake (red)"
        data={r.data}
        duration={duration}
        yDomain={[0, 100]}
        height={180}
        lines={[
          { key: "throttle", color: "#80ed99" },
          { key: "brake", color: "#ff595e" },
        ]}
      />
    </main>
  );
}