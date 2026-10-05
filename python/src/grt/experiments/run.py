"""Write the shipped finite experiments to data/ and the web public folder."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np

from grt.analysis.stats import analyse
from grt.graphs.complex_be import build_graph
from grt.graphs.samples import sample_complex_sphere

REPO_ROOT = Path(__file__).resolve().parents[4]
DATA_DIR = REPO_ROOT / "data"
WEB_DATA = REPO_ROOT / "apps" / "web" / "public" / "data"

MU = 0.05
K_STRIPE = 2.0
P = 3


def main() -> None:
    records = [_hand_record(), *_random_records()]
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    WEB_DATA.mkdir(parents=True, exist_ok=True)
    index = []
    summary_rows = []
    for record in records:
        path_name = f"{record['id']}.json"
        text = json.dumps(record, indent=2)
        (DATA_DIR / path_name).write_text(text, encoding="utf-8")
        (WEB_DATA / path_name).write_text(text, encoding="utf-8")
        index.append(
            {
                "id": record["id"],
                "title": record["title"],
                "file": path_name,
            }
        )
        stats = record["statistics"]
        summary_rows.append(
            {
                "id": record["id"],
                "p": record["parameters"]["p"],
                "ell": record["parameters"]["ell"],
                "mu": record["parameters"]["mu"],
                "K": record["parameters"]["K"],
                "k": record["parameters"]["k"],
                "seed": record["seed"],
                "vertices": stats["vertex_count"],
                "edges": stats["edge_count"],
                "edge_density": stats["edge_density"],
                "cross_density": stats["cross_density"],
                "internal_density_W": stats["internal_density_W"],
                "internal_density_Z": stats["internal_density_Z"],
            }
        )
    (DATA_DIR / "index.json").write_text(json.dumps(index, indent=2), encoding="utf-8")
    (WEB_DATA / "index.json").write_text(json.dumps(index, indent=2), encoding="utf-8")
    with (DATA_DIR / "summary.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summary_rows[0].keys()))
        writer.writeheader()
        writer.writerows(summary_rows)
    print(f"wrote {len(records)} experiments to {DATA_DIR}")


def _hand_record() -> dict:
    rho = np.exp(2j * np.pi / 3)
    angle = np.pi / 6
    part_w = [
        np.array([1, 0], dtype=np.complex128),
        np.array([rho, 0], dtype=np.complex128),
        np.array([0, 1], dtype=np.complex128),
    ]
    part_z = [
        np.array([np.exp(-1j * angle), 0], dtype=np.complex128),
        np.array([-1, 0], dtype=np.complex128),
        np.array([0, 1], dtype=np.complex128),
    ]
    return _record(
        experiment_id="hand-p3-ell1",
        title="Hand points in C^2",
        description=(
            "Six explicit unit vectors in C^2. The second W-point is ρ times the first, so "
            "the stored B1 witness on that pair is h = 2: the earlier point is a ρ^2-rotate "
            "of the later one, and the distance is zero. z0 is chosen so that ⟨w0, z0⟩ = exp(iπ/6), "
            "which lies in the arc [0, 2π/3] and outside the imaginary stripes for Kμ = 0.1. "
            "z1 = (−1, 0) fails both cross conditions against w0. This file is for inspection, not for density."
        ),
        sampler="hand",
        seed=None,
        part_w=part_w,
        part_z=part_z,
        ell=1,
    )


def _random_records() -> list[dict]:
    specs = [
        ("random-k2-n12-ell1", 2, 12, 1, 1),
        ("random-k2-n12-ell2", 2, 12, 2, 1),
        ("random-k2-n24-ell1", 2, 24, 1, 2),
        ("random-k3-n12-ell1", 3, 12, 1, 3),
        ("random-k3-n24-ell2", 3, 24, 2, 4),
    ]
    records = []
    for experiment_id, k, n, ell, seed in specs:
        part_w = sample_complex_sphere(n, k, seed=seed)
        part_z = sample_complex_sphere(n, k, seed=seed + 1000)
        records.append(
            _record(
                experiment_id=experiment_id,
                title=f"Uniform sample, k={k}, n={n}, ℓ={ell}",
                description=(
                    "Each part is an i.i.d. uniform sample on the complex unit sphere, "
                    "from normalised real Gaussians. The seed for Z is the seed for W plus 1000. "
                    "Thresholds are μ = 0.05 and K = 2, fixed so that both edge rules can fire "
                    "on a small sample. These thresholds do not follow the paper's asymptotic "
                    "hierarchy, and the sample is not an equal-measure partition."
                ),
                sampler="uniform-sphere",
                seed=seed,
                part_w=part_w,
                part_z=part_z,
                ell=ell,
            )
        )
    return records


def _record(
    experiment_id: str,
    title: str,
    description: str,
    sampler: str,
    seed: int | None,
    part_w: list[np.ndarray],
    part_z: list[np.ndarray],
    ell: int,
) -> dict:
    graph = build_graph(part_w, part_z, p=P, ell=ell, mu=MU, k_stripe=K_STRIPE)
    graph["id"] = experiment_id
    graph["title"] = title
    graph["description"] = description
    graph["sampler"] = sampler
    graph["seed"] = seed
    graph["z_seed"] = None if seed is None else seed + 1000
    graph["statistics"] = analyse(graph, p=P)
    graph["notes"] = [
        "Edge rules are B1 and B2 from Section 3.1.",
        "guarantees is intentionally empty of theorems.",
    ]
    return graph


if __name__ == "__main__":
    main()
