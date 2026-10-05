import assert from "node:assert/strict";
import test from "node:test";
import { projectPhi } from "./project.ts";

test("projectPhi reads the real isometry in order x, y, x, y", () => {
  const projected = projectPhi([
    { re: 0.2, im: -0.4 },
    { re: 0.6, im: 0.1 },
  ]);
  assert.deepEqual(projected, [0.2, -0.4, 0.6]);
});

test("projectPhi pads missing coordinates with zero", () => {
  assert.deepEqual(projectPhi([{ re: 1, im: 0 }]), [1, 0, 0]);
});
