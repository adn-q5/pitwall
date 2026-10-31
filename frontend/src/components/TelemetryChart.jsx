import { CartesianGrid, Line, LineChart, ResponsiveContainer, XAxis, YAxis } from "recharts";

export default function TelemetryChart({ title, data, duration, lines, yDomain, height = 220 }) {
  return (
    <div className="card">
      <h3>{title}</h3>
      <ResponsiveContainer width="100%" height={height}>
        <LineChart data={data}>
          <CartesianGrid stroke="#2a2a2a" />
          <XAxis
            dataKey="t"
            type="number"
            domain={[0, duration]}
            tickFormatter={(v) => `${Math.round(v)}s`}
          />
          <YAxis domain={yDomain} />
          {lines.map((l) => (
            <Line
              key={l.key}
              dataKey={l.key}
              stroke={l.color}
              strokeWidth={2}
              dot={false}
              isAnimationActive={false}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}