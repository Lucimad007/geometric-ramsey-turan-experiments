"""Write the shipped finite experiments to data/ and the web public folder."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import numpy as np

from grt.analysis.mechanism import cross_cloud, mechanism_report, paper_thresholds
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
    records = [_hand_record(), _showcase_record(), *_random_records()]
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
    sweep = _density_sweep()
    sweep_text = json.dumps(sweep, indent=2)
    (DATA_DIR / "density-sweep.json").write_text(sweep_text, encoding="utf-8")
    (WEB_DATA / "density-sweep.json").write_text(sweep_text, encoding="utf-8")
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


def _showcase_record() -> dict:
    """A sample large enough to see the inner-product cloud, still small enough to draw."""
    k = 8
    epsilon = 0.2
    k_stripe = 5.0
    mu = paper_thresholds(k, epsilon, k_stripe)
    n = 24
    seed = 11
    return _record(
        experiment_id="mechanism-k8-n24-ell1",
        title="Inner-product cloud, k=8, ℓ=1",
        description=(
            "Uniform points on S^7(C), with μ = ε/√(2k) for ε = 0.2 and K = 5, "
            "the scale written in Section 3.1. The Argand diagram shows every ⟨w, z⟩. "
            "A point is a cross edge only when it lies in the arc of length 2π/3 and "
            "outside every imaginary stripe. This is not a fine equal-measure partition, "
            "and ε is not yet negligible compared with 1/K, so the cross rate need not be near 1/3."
        ),
        sampler="uniform-sphere",
        seed=seed,
        part_w=sample_complex_sphere(n, k, seed=seed),
        part_z=sample_complex_sphere(n, k, seed=seed + 1000),
        ell=1,
        mu=mu,
        k_stripe=k_stripe,
        store_cloud=True,
    )


def _density_sweep() -> dict:
    """Cross rate against dimension, for two threshold regimes and ℓ = 1, 2."""
    rows = []
    n = 48
    for regime, epsilon, k_stripe, fixed_mu in (
        ("section-3.1-scale", 0.2, 5.0, None),
        ("smaller-epsilon-K", 0.05, 2.0, None),
        ("fixed-thresholds", None, 2.0, 0.05),
    ):
        for ell in (1, 2):
            for k in (4, 8, 16, 32, 64):
                mu = fixed_mu if fixed_mu is not None else paper_thresholds(k, epsilon, k_stripe)
                seed = 100 * k + ell
                part_w = sample_complex_sphere(n, k, seed=seed)
                part_z = sample_complex_sphere(n, k, seed=seed + 1000)
                report = mechanism_report(part_w, part_z, [], p=P, ell=ell, mu=mu, k_stripe=k_stripe)
                rows.append(
                    {
                        "regime": regime,
                        "k": k,
                        "ell": ell,
                        "n_per_part": n,
                        "seed": seed,
                        "mu": mu,
                        "K": k_stripe,
                        "epsilon": epsilon,
                        "stripe_rate": report["stripe_rate"],
                        "arc_rate": report["arc_rate"],
                        "both_rate": report["both_rate"],
                        "target_cross_density": report["target_cross_density"],
                        "internal_edge_rate_W": report["internal_edge_rate_W"],
                        "internal_edge_rate_Z": report["internal_edge_rate_Z"],
                    }
                )
    return {
        "guarantees": "none; finite sample",
        "n_per_part": n,
        "p": P,
        "note": (
            "both_rate is the fraction of W×Z pairs accepted by rule B2. "
            "The horizontal targets are ℓ/p. Section 3.1 reaches those targets "
            "only after a fine partition of a very high-dimensional sphere, which "
            "these uniform samples are not. The section-3.1-scale series uses "
            "μ = ε/√(2k) with ε = 0.2 and K = 5. The fixed-thresholds series "
            "keeps μ = 0.05 and K = 2 so the rules stay visible in small dimension. "
            "The smaller-epsilon-K series uses ε = 0.05 and K = 2, so εK is smaller "
            "and the stripe deletion is less severe."
        ),
        "rows": rows,
    }


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
    mu: float = MU,
    k_stripe: float = K_STRIPE,
    store_cloud: bool = False,
) -> dict:
    graph = build_graph(part_w, part_z, p=P, ell=ell, mu=mu, k_stripe=k_stripe)
    graph["id"] = experiment_id
    graph["title"] = title
    graph["description"] = description
    graph["sampler"] = sampler
    graph["seed"] = seed
    graph["z_seed"] = None if seed is None else seed + 1000
    graph["statistics"] = analyse(graph, p=P)
    graph["statistics"].update(mechanism_report(part_w, part_z, graph["edges"], p=P, ell=ell, mu=mu, k_stripe=k_stripe))
    if store_cloud:
        graph["cross_cloud"] = cross_cloud(part_w, part_z, p=P, ell=ell, mu=mu, k_stripe=k_stripe)
        graph["arc_upper"] = 2.0 * math.pi * ell / P
        graph["im_threshold"] = k_stripe * mu
    graph["notes"] = [
        "Edge rules are B1 and B2 from Section 3.1.",
        "target_cross_density is the ℓ/p of Theorem 1.1, not a fitted constant.",
        "guarantees is intentionally empty of theorems.",
    ]
    return graph


if __name__ == "__main__":
    main()
