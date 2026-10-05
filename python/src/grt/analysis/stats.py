"""Counts on a concrete graph produced by `build_graph`."""

from __future__ import annotations

from itertools import combinations


def analyse(graph: dict, p: int) -> dict:
    """Return measured counts. Missing keys were omitted because of a size cap."""
    points = graph["points"]
    edges = graph["edges"]
    n = len(points)
    ids = [point["id"] for point in points]
    index = {point_id: position for position, point_id in enumerate(ids)}
    parts = {point["id"]: point["part"] for point in points}
    adjacency = {point_id: set() for point_id in ids}
    internal = {"W": 0, "Z": 0}
    cross = 0
    for edge in edges:
        adjacency[edge["source"]].add(edge["target"])
        adjacency[edge["target"]].add(edge["source"])
        if edge["kind"] == "cross":
            cross += 1
        else:
            internal[parts[edge["source"]]] += 1

    degrees = [len(adjacency[point_id]) for point_id in ids]
    w_count = sum(1 for point in points if point["part"] == "W")
    z_count = sum(1 for point in points if point["part"] == "Z")
    stats: dict = {
        "vertex_count": n,
        "edge_count": len(edges),
        "edge_density": _pair_density(len(edges), n),
        "internal_density_W": _pair_density(internal["W"], w_count),
        "internal_density_Z": _pair_density(internal["Z"], z_count),
        "cross_density": (cross / (w_count * z_count)) if w_count and z_count else None,
        "cross_edge_count": cross,
        "internal_edge_count_W": internal["W"],
        "internal_edge_count_Z": internal["Z"],
        "degree_min": min(degrees) if degrees else 0,
        "degree_mean": (sum(degrees) / n) if n else 0.0,
        "degree_max": max(degrees) if degrees else 0,
        "component_count": _components(ids, adjacency),
        "label": "measured on this finite sample",
    }
    if n <= 80:
        stats["triangle_count"] = _triangles(ids, adjacency)
    else:
        stats["triangle_count_omitted"] = "vertex cap 80"
    if n <= 40:
        cap = min(p + 2, n)
        stats["max_clique_size_at_most"] = _max_clique(ids, adjacency, cap)
        stats["clique_search_cap"] = cap
    else:
        stats["clique_search_omitted"] = "vertex cap 40"
    if n <= 20:
        stats["independence_number"] = _independence_number(ids, adjacency)
    else:
        stats["independence_omitted"] = "vertex cap 20"
    if n <= 12:
        stats["p_independence_number"] = _p_independence(ids, adjacency, p)
    else:
        stats["p_independence_omitted"] = "vertex cap 12"
    return stats


def _pair_density(edges: int, vertices: int) -> float | None:
    if vertices < 2:
        return None
    return 2.0 * edges / (vertices * (vertices - 1))


def _components(ids: list[str], adjacency: dict[str, set[str]]) -> int:
    seen: set[str] = set()
    count = 0
    for start in ids:
        if start in seen:
            continue
        count += 1
        stack = [start]
        seen.add(start)
        while stack:
            current = stack.pop()
            for neighbour in adjacency[current]:
                if neighbour not in seen:
                    seen.add(neighbour)
                    stack.append(neighbour)
    return count


def _triangles(ids: list[str], adjacency: dict[str, set[str]]) -> int:
    count = 0
    for a, b, c in combinations(ids, 3):
        if b in adjacency[a] and c in adjacency[a] and c in adjacency[b]:
            count += 1
    return count


def _max_clique(ids: list[str], adjacency: dict[str, set[str]], cap: int) -> int:
    best = 1 if ids else 0
    for size in range(2, cap + 1):
        found = False
        for group in combinations(ids, size):
            if _is_clique(group, adjacency):
                found = True
                best = size
                break
        if not found:
            break
    return best


def _is_clique(group: tuple[str, ...], adjacency: dict[str, set[str]]) -> bool:
    for left, right in combinations(group, 2):
        if right not in adjacency[left]:
            return False
    return True


def _independence_number(ids: list[str], adjacency: dict[str, set[str]]) -> int:
    edge_bits = _edge_bits(ids, adjacency)
    best = 0
    n = len(ids)
    for mask in range(1 << n):
        if (mask.bit_count() if hasattr(mask, "bit_count") else bin(mask).count("1")) <= best:
            continue
        if any(mask & left and mask & right for left, right in edge_bits):
            continue
        best = mask.bit_count()
    return best


def _p_independence(ids: list[str], adjacency: dict[str, set[str]], p: int) -> int:
    """Size of a largest set containing no clique of order p."""
    if p <= 1:
        return 0
    n = len(ids)
    clique_masks = []
    if p <= n:
        for group in combinations(range(n), p):
            if _is_clique(tuple(ids[i] for i in group), adjacency):
                mask = 0
                for i in group:
                    mask |= 1 << i
                clique_masks.append(mask)
    best = 0
    for mask in range(1 << n):
        size = mask.bit_count()
        if size <= best:
            continue
        if any((mask & clique) == clique for clique in clique_masks):
            continue
        best = size
    return best


def _edge_bits(ids: list[str], adjacency: dict[str, set[str]]) -> list[tuple[int, int]]:
    index = {point_id: bit for bit, point_id in enumerate(ids)}
    pairs = []
    for left, neighbours in adjacency.items():
        for right in neighbours:
            if index[left] < index[right]:
                pairs.append((1 << index[left], 1 << index[right]))
    return pairs
