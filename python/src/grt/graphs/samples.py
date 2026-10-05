"""Deterministic finite point sets on the complex unit sphere.

`sample_complex_sphere` draws i.i.d. uniform points by normalising real
Gaussian vectors. That is the uniform measure on the sphere. It is not the
equal-measure small-diameter partition asserted by Lemma 2.4.
"""

from __future__ import annotations

import numpy as np


def sample_complex_sphere(n: int, k: int, seed: int) -> list[np.ndarray]:
    """Return n unit vectors in C^k.

    The generator is `numpy.random.Generator(PCG64(seed))`. Coordinates are
    2k independent standard normals, read as k complex numbers via
    x_j + i y_j, then divided by the Euclidean norm.
    """
    if n < 0 or k < 1:
        raise ValueError("n must be nonnegative and k must be at least 1")
    generator = np.random.Generator(np.random.PCG64(seed))
    raw = generator.standard_normal((n, k, 2))
    complex_points = raw[:, :, 0] + 1j * raw[:, :, 1]
    norms = np.linalg.norm(complex_points, axis=1, keepdims=True)
    unit = complex_points / norms
    return [unit[index].astype(np.complex128) for index in range(n)]
