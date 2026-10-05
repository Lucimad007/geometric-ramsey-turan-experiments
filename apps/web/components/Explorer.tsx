"use client";

import { Canvas } from "@react-three/fiber";
import { useEffect, useMemo, useState } from "react";
import Scene from "@/components/Scene";
import type { EdgeRecord, Experiment, IndexEntry } from "@/lib/types";

const STAT_ROWS: { key: string; label: string }[] = [
  { key: "vertex_count", label: "|V|" },
  { key: "edge_count", label: "|E|" },
  { key: "edge_density", label: "edge density" },
  { key: "internal_density_W", label: "internal density W" },
  { key: "internal_density_Z", label: "internal density Z" },
  { key: "cross_density", label: "cross density" },
  { key: "degree_min", label: "degree min" },
  { key: "degree_mean", label: "degree mean" },
  { key: "degree_max", label: "degree max" },
  { key: "component_count", label: "components" },
  { key: "triangle_count", label: "triangles" },
  { key: "max_clique_size_at_most", label: "largest clique within cap" },
  { key: "independence_number", label: "independence number" },
  { key: "p_independence_number", label: "p-independence number" },
];

export default function Explorer() {
  const [index, setIndex] = useState<IndexEntry[]>([]);
  const [currentId, setCurrentId] = useState<string>("");
  const [experiment, setExperiment] = useState<Experiment | null>(null);
  const [mode, setMode] = useState<"geometry" | "graph">("graph");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("/data/index.json")
      .then((response) => response.json())
      .then((entries: IndexEntry[]) => {
        setIndex(entries);
        setCurrentId(entries[0]?.id ?? "");
      })
      .catch(() => setError("Could not load /data/index.json"));
  }, []);

  useEffect(() => {
    const entry = index.find((item) => item.id === currentId);
    if (!entry) return;
    setSelectedId(null);
    fetch(`/data/${entry.file}`)
      .then((response) => response.json())
      .then((payload: Experiment) => setExperiment(payload))
      .catch(() => setError(`Could not load ${entry.file}`));
  }, [currentId, index]);

  const incident = useMemo(() => {
    if (!experiment || !selectedId) return [];
    return experiment.edges.filter(
      (edge) => edge.source === selectedId || edge.target === selectedId,
    );
  }, [experiment, selectedId]);

  return (
    <div className="shell">
      <header>
        <p className="eyebrow">Computational companion</p>
        <h1>Geometric constructions for Ramsey–Turán theory</h1>
        <p className="lede">
          Finite samples of the complex Bollobás–Erdős edge rules from Liu, Reiher,
          Sharifzadeh, and Staden. The picture is a coordinate projection. The numbers
          are counts on the loaded sample.
        </p>
      </header>
      <div className="layout">
        <section className="stage">
          <div className="stage-bar">
            <div className="toggle">
              <button
                type="button"
                className={mode === "geometry" ? "active" : ""}
                onClick={() => setMode("geometry")}
              >
                Points
              </button>
              <button
                type="button"
                className={mode === "graph" ? "active" : ""}
                onClick={() => setMode("graph")}
              >
                Graph
              </button>
            </div>
            <p className="projection">
              Drawn coordinates are the first three entries of φ(z) = (x₁, y₁, …, x_k, y_k).
              For k &gt; 2 this is a shadow of S<sup>2k−1</sup>(R).
            </p>
          </div>
          <div className="canvas-wrap">
            {experiment ? (
              <Canvas camera={{ position: [1.6, 1.2, 1.8], fov: 45 }}>
                <Scene
                  points={experiment.points}
                  edges={experiment.edges}
                  mode={mode}
                  selectedId={selectedId}
                  onSelect={setSelectedId}
                />
              </Canvas>
            ) : (
              <p className="loading">{error ?? "Loading sample…"}</p>
            )}
          </div>
          <ul className="legend">
            <li><span className="swatch w" /> W</li>
            <li><span className="swatch z" /> Z</li>
            <li><span className="swatch s" /> selected</li>
          </ul>
        </section>
        <aside>
          <label className="field">
            Dataset
            <select
              value={currentId}
              onChange={(event) => setCurrentId(event.target.value)}
            >
              {index.map((entry) => (
                <option key={entry.id} value={entry.id}>
                  {entry.title}
                </option>
              ))}
            </select>
          </label>
          {experiment && (
            <>
              <p className="description">{experiment.description}</p>
              <dl className="params">
                <div><dt>p</dt><dd>{experiment.parameters.p}</dd></div>
                <div><dt>ℓ</dt><dd>{experiment.parameters.ell}</dd></div>
                <div><dt>μ</dt><dd>{experiment.parameters.mu}</dd></div>
                <div><dt>K</dt><dd>{experiment.parameters.K}</dd></div>
                <div><dt>k</dt><dd>{experiment.parameters.k}</dd></div>
                <div><dt>seed</dt><dd>{experiment.seed ?? "—"}</dd></div>
              </dl>
              <p className="guarantee">{experiment.guarantees}</p>
              <h2>Measured on this sample</h2>
              <table>
                <tbody>
                  {STAT_ROWS.map((row) =>
                    experiment.statistics[row.key] === undefined ? null : (
                      <tr key={row.key}>
                        <th>{row.label}</th>
                        <td>{formatStat(experiment.statistics[row.key])}</td>
                      </tr>
                    ),
                  )}
                </tbody>
              </table>
              <Omitted statistics={experiment.statistics} />
              <h2>Rules, as evaluated in Python</h2>
              <p className="rule">
                Internal: some h ∈ {"{1,…,p−1}"} has ‖w − ρ<sup>h</sup> w′‖ ≤ √μ.
              </p>
              <p className="rule">
                Cross: |Im(ρ<sup>h</sup> ⟨w, z⟩)| ≥ Kμ for every h, and arg⟨w, z⟩ ∈ [0, 2πℓ/p].
              </p>
              <Selection
                selectedId={selectedId}
                incident={incident}
                onClear={() => setSelectedId(null)}
              />
            </>
          )}
        </aside>
      </div>
    </div>
  );
}

function Selection({
  selectedId,
  incident,
  onClear,
}: {
  selectedId: string | null;
  incident: EdgeRecord[];
  onClear: () => void;
}) {
  if (!selectedId) {
    return <p className="hint">Select a point to read the stored witness for each incident edge.</p>;
  }
  return (
    <div className="selection">
      <div className="selection-head">
        <h2>{selectedId}</h2>
        <button type="button" onClick={onClear}>Clear</button>
      </div>
      {incident.length === 0 && <p>No incident edges in this sample.</p>}
      <ul>
        {incident.map((edge) => {
          const other = edge.source === selectedId ? edge.target : edge.source;
          return (
            <li key={`${edge.source}-${edge.target}`}>
              <strong>{other}</strong>
              <span>{edge.kind}</span>
              <Witness witness={edge.witness} kind={edge.kind} />
            </li>
          );
        })}
      </ul>
    </div>
  );
}

function Witness({ witness, kind }: { witness: Record<string, number>; kind: string }) {
  if (kind === "internal") {
    return (
      <p>
        h = {witness.h}, distance {formatStat(witness.distance)} ≤ √μ = {formatStat(witness.threshold)}
      </p>
    );
  }
  return (
    <p>
      arg = {formatStat(witness.argument)} in [0, {formatStat(witness.argument_upper)}], min |Im| ={" "}
      {formatStat(witness.min_abs_im)} ≥ {formatStat(witness.im_threshold)}
    </p>
  );
}

function Omitted({ statistics }: { statistics: Record<string, number | string | null> }) {
  const notes = Object.entries(statistics).filter(([key]) => key.endsWith("_omitted"));
  if (notes.length === 0) return null;
  return (
    <ul className="omitted">
      {notes.map(([key, value]) => (
        <li key={key}>
          {key.replaceAll("_", " ")}: {String(value)}
        </li>
      ))}
    </ul>
  );
}

function formatStat(value: number | string | null | undefined): string {
  if (value === null || value === undefined) return "—";
  if (typeof value === "string") return value;
  if (Number.isInteger(value)) return String(value);
  return value.toFixed(4);
}
