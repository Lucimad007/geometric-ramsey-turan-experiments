"use client";

export type SweepRow = {
  regime: string;
  k: number;
  ell: number;
  both_rate: number;
  arc_rate: number;
  stripe_rate: number;
  target_cross_density: number;
  internal_edge_rate_W: number | null;
};

const REGIMES = [
  { id: "section-3.1-scale", label: "μ = ε/√(2k), ε = 0.2, K = 5" },
  { id: "smaller-epsilon-K", label: "μ = ε/√(2k), ε = 0.05, K = 2" },
  { id: "fixed-thresholds", label: "μ = 0.05, K = 2" },
];

export default function SweepChart({ rows, note }: { rows: SweepRow[]; note: string }) {
  return (
    <section className="sweep">
      <h2>Cross acceptance against dimension</h2>
      <p className="rule">{note}</p>
      {REGIMES.map((regime) => (
        <div key={regime.id} className="sweep-block">
          <h3>{regime.label}</h3>
          <div className="sweep-grid">
            {[1, 2].map((ell) => (
              <Series
                key={ell}
                title={`ℓ = ${ell}, target ℓ/p = ${(ell / 3).toFixed(3)}`}
                rows={rows.filter((row) => row.regime === regime.id && row.ell === ell)}
              />
            ))}
          </div>
        </div>
      ))}
    </section>
  );
}

function Series({ title, rows }: { title: string; rows: SweepRow[] }) {
  const width = 360;
  const height = 160;
  const pad = 28;
  const ordered = [...rows].sort((a, b) => a.k - b.k);
  if (ordered.length === 0) return null;
  const target = ordered[0].target_cross_density;
  const xs = ordered.map((row) => row.k);
  const xOf = (k: number) => pad + ((Math.log2(k) - Math.log2(xs[0])) / (Math.log2(xs[xs.length - 1]) - Math.log2(xs[0]) || 1)) * (width - 2 * pad);
  const yOf = (value: number) => height - pad - Math.min(1, Math.max(0, value)) * (height - 2 * pad);
  const line = (key: "both_rate" | "arc_rate" | "stripe_rate") =>
    ordered.map((row, index) => `${index === 0 ? "M" : "L"} ${xOf(row.k)} ${yOf(row[key])}`).join(" ");

  return (
    <figure>
      <figcaption>{title}</figcaption>
      <svg viewBox={`0 0 ${width} ${height}`} role="img">
        <line x1={pad} x2={width - pad} y1={yOf(target)} y2={yOf(target)} className="target" />
        <path d={line("arc_rate")} className="series arc" />
        <path d={line("stripe_rate")} className="series stripe" />
        <path d={line("both_rate")} className="series both" />
        {ordered.map((row) => (
          <text key={row.k} x={xOf(row.k)} y={height - 8} textAnchor="middle" className="tick">
            {row.k}
          </text>
        ))}
      </svg>
      <p className="legend-line">
        <span className="key both" /> B2 (both) <span className="key arc" /> arc only <span className="key stripe" /> stripe only{" "}
        <span className="key target" /> ℓ/p
      </p>
    </figure>
  );
}
