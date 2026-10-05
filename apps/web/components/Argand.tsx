"use client";

import type { Experiment } from "@/lib/types";

type Pair = NonNullable<Experiment["cross_cloud"]>[number];

export default function Argand({
  pairs,
  arcUpper,
  threshold,
  selectedId,
}: {
  pairs: Pair[];
  arcUpper: number;
  threshold: number;
  selectedId: string;
}) {
  const shown = pairs.filter((pair) => pair.w === selectedId || pair.z === selectedId);
  const size = 280;
  const center = size / 2;
  const scale = center - 18;
  const wedge = wedgePath(center, scale, arcUpper);

  return (
    <figure className="argand">
      <svg viewBox={`0 0 ${size} ${size}`} role="img" aria-label="Inner products in the complex plane">
        <circle cx={center} cy={center} r={scale} className="disk" />
        <path d={wedge} className="arc" />
        {shown.map((pair) => {
          const x = center + pair.re * scale;
          const y = center - pair.im * scale;
          const tone = pair.edge ? "edge" : pair.arc ? "arc-only" : pair.stripe ? "stripe-only" : "neither";
          return <circle key={`${pair.w}-${pair.z}`} cx={x} cy={y} r={pair.edge ? 3.2 : 2.2} className={tone} />;
        })}
        <line x1={center - scale} x2={center + scale} y1={center} y2={center} className="axis" />
        <line x1={center} x2={center} y1={center - scale} y2={center + scale} className="axis" />
      </svg>
      <figcaption>
        ⟨w, z⟩ for {selectedId}. The shaded sector is [0, {arcUpper.toFixed(3)}]. A cross edge
        also needs min<sub>h</sub> |Im(ρ<sup>h</sup> ⟨w, z⟩)| ≥ {threshold.toFixed(4)}. Gold points
        pass both tests. Blue points lie in the arc but inside a stripe. The threshold is drawn
        as a number because the stripes are rotated copies, not a single horizontal band.
      </figcaption>
    </figure>
  );
}

function wedgePath(center: number, scale: number, upper: number): string {
  const start = polar(center, scale, 0);
  const end = polar(center, scale, upper);
  const large = upper > Math.PI ? 1 : 0;
  return `M ${center} ${center} L ${start.x} ${start.y} A ${scale} ${scale} 0 ${large} 0 ${end.x} ${end.y} Z`;
}

function polar(center: number, scale: number, angle: number): { x: number; y: number } {
  return {
    x: center + scale * Math.cos(angle),
    y: center - scale * Math.sin(angle),
  };
}
