import type { Coord } from "./types";

/** First three real coordinates of φ(z) = (x1, y1, …, xk, yk). */
export function projectPhi(coords: Coord[]): [number, number, number] {
  const flat: number[] = [];
  for (const coord of coords) {
    flat.push(coord.re, coord.im);
  }
  return [flat[0] ?? 0, flat[1] ?? 0, flat[2] ?? 0];
}
