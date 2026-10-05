"""Complex-sphere arithmetic used by the Section 3 edge rules."""

from grt.geometry.complex import (
    ABS_TOL,
    REL_TOL,
    argument,
    argument_in_arc,
    hermitian_inner,
    imag_stripe_min,
    norm,
    require_unit,
    root_of_unity,
    rotation_distance,
    within_upper,
)
from grt.geometry.rhombus import find_rhombus

__all__ = [
    "ABS_TOL",
    "REL_TOL",
    "argument",
    "argument_in_arc",
    "find_rhombus",
    "hermitian_inner",
    "imag_stripe_min",
    "norm",
    "require_unit",
    "root_of_unity",
    "rotation_distance",
    "within_upper",
]
