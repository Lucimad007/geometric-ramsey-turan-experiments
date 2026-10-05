"use client";

import { OrbitControls } from "@react-three/drei";
import { useMemo } from "react";
import * as THREE from "three";
import { projectPhi } from "@/lib/project";
import type { EdgeRecord, PointRecord } from "@/lib/types";

const PART_COLOR = { W: "#1f4b6e", Z: "#8c3d2f" };

type SceneProps = {
  points: PointRecord[];
  edges: EdgeRecord[];
  mode: "geometry" | "graph";
  selectedId: string | null;
  onSelect: (id: string) => void;
};

export default function Scene({ points, edges, mode, selectedId, onSelect }: SceneProps) {
  const positions = useMemo(() => {
    const map = new Map<string, [number, number, number]>();
    for (const point of points) {
      map.set(point.id, projectPhi(point.coords));
    }
    return map;
  }, [points]);

  const neighborIds = useMemo(() => {
    const set = new Set<string>();
    if (!selectedId) return set;
    for (const edge of edges) {
      if (edge.source === selectedId) set.add(edge.target);
      if (edge.target === selectedId) set.add(edge.source);
    }
    return set;
  }, [edges, selectedId]);

  const visibleEdges = edges.filter((edge) => {
    if (mode === "graph") return true;
    if (!selectedId) return false;
    return edge.source === selectedId || edge.target === selectedId;
  });

  return (
    <>
      <color attach="background" args={["#f3efe6"]} />
      <ambientLight intensity={0.8} />
      <directionalLight position={[3, 4, 2]} intensity={0.6} />
      <gridHelper args={[4, 8, "#d9d1c4", "#e6dfd2"]} />
      <EdgeLines edges={visibleEdges} positions={positions} selectedId={selectedId} />
      {points.map((point) => {
        const position = positions.get(point.id) ?? [0, 0, 0];
        const selected = point.id === selectedId;
        const neighbor = neighborIds.has(point.id);
        const radius = selected ? 0.055 : neighbor ? 0.042 : 0.03;
        return (
          <mesh
            key={point.id}
            position={position}
            onClick={(event) => {
              event.stopPropagation();
              onSelect(point.id);
            }}
          >
            <sphereGeometry args={[radius, 24, 24]} />
            <meshStandardMaterial
              color={selected ? "#c4a35a" : neighbor ? "#d7c39a" : PART_COLOR[point.part]}
            />
          </mesh>
        );
      })}
      <OrbitControls makeDefault />
    </>
  );
}

function EdgeLines({
  edges,
  positions,
  selectedId,
}: {
  edges: EdgeRecord[];
  positions: Map<string, [number, number, number]>;
  selectedId: string | null;
}) {
  const geometry = useMemo(() => {
    const buffer = new Float32Array(edges.length * 6);
    edges.forEach((edge, index) => {
      const a = positions.get(edge.source) ?? [0, 0, 0];
      const b = positions.get(edge.target) ?? [0, 0, 0];
      buffer.set([...a, ...b], index * 6);
    });
    const result = new THREE.BufferGeometry();
    result.setAttribute("position", new THREE.BufferAttribute(buffer, 3));
    return result;
  }, [edges, positions]);

  const incident = selectedId
    ? edges.some((edge) => edge.source === selectedId || edge.target === selectedId)
    : false;

  return (
    <lineSegments geometry={geometry}>
      <lineBasicMaterial color={incident ? "#8a7040" : "#b7aea2"} />
    </lineSegments>
  );
}
