"""
WinFlume Pro Max - Custom RBC Flume Designer (v2)

Adds two real design constraints on top of the base max-flow solver:
  - max_channel_width_cm: caps the solvable throat width (entrance width = 2 x throat width)
  - target_min_flow_gpm: checks whether the max-flow-sized design can ALSO accurately
    measure the stated minimum flow, and reports honestly when it can't (a single flume
    sized for peak flow is not always sensitive enough at the low end - a real tradeoff,
    not a bug).
"""

import numpy as np

KNOWN_SIZES_MM = np.array([50, 75, 100, 150, 200])
KNOWN_COEFF = np.array([0.001035, 0.001347, 0.001514, 0.001929, 0.002189])
KNOWN_OFFSET_MM = np.array([0.75, 1.313, 2.214, 3.603, 5.457])
KNOWN_EXPONENT = np.array([1.853, 1.853, 1.867, 1.870, 1.879])

# Real minimum-head data from the 5 known calibrated sizes (ft). Note: the 200mm value
# (0.31) is a clear outlier vs the others (~0.02-0.06) - interpolation near 150-200mm
# should be treated with extra caution as a result.
KNOWN_MIN_HEAD_FT = np.array([0.02, 0.03, 0.06, 0.06, 0.31])

GEOMETRY_RATIOS = {
    "wing_wall": 0.5,
    "approach_section": 2.2,
    "converging_section": 2.0,
    "diverging_section": 3.0,
    "exit_section": 1.7,
    "wall_height": 1.7,
    "overall_length": 6.0,
}
SIDE_WALL_ANGLE_DEG = 63.43
FT_PER_MM = 1 / 304.8
LS_TO_GPM = 15.8503

_K_AT_KNOWN_SIZES = None


def _compute_K_values():
    global _K_AT_KNOWN_SIZES
    if _K_AT_KNOWN_SIZES is None:
        Q_at_Hb = KNOWN_COEFF * (KNOWN_SIZES_MM + KNOWN_OFFSET_MM) ** KNOWN_EXPONENT
        _K_AT_KNOWN_SIZES = Q_at_Hb / (KNOWN_SIZES_MM ** 2.5)
    return _K_AT_KNOWN_SIZES


def _interpolate(b_mm, known_x, known_y):
    return float(np.interp(b_mm, known_x, known_y))


def _in_confirmed_range(b_mm):
    return bool(KNOWN_SIZES_MM.min() <= b_mm <= KNOWN_SIZES_MM.max())


def _rating_params(b_mm):
    """Returns (coefficient, offset_mm, exponent) for the L/S(H_mm) equation at this throat width."""
    K_vals = _compute_K_values()
    K = _interpolate(b_mm, KNOWN_SIZES_MM, K_vals)
    exponent = _interpolate(b_mm, KNOWN_SIZES_MM, KNOWN_EXPONENT)
    offset_ratio = _interpolate(b_mm, KNOWN_SIZES_MM, KNOWN_OFFSET_MM / KNOWN_SIZES_MM)
    offset_mm = offset_ratio * b_mm
    Q_at_Hb = K * (b_mm ** 2.5)
    coefficient = Q_at_Hb / (b_mm + offset_mm) ** exponent
    return coefficient, offset_mm, exponent


def _flow_at_head(b_mm, head_mm):
    coeff, offset_mm, exponent = _rating_params(b_mm)
    ls = coeff * (head_mm + offset_mm) ** exponent
    return ls * LS_TO_GPM


def _min_head_ft(b_mm):
    return _interpolate(b_mm, KNOWN_SIZES_MM, KNOWN_MIN_HEAD_FT)


def _build_geometry(b_mm):
    b_cm = b_mm / 10.0
    return {
        "units": "cm",
        "throat_width": round(b_cm, 3),
        "entrance_wing_wall": round(b_cm * GEOMETRY_RATIOS["wing_wall"], 3),
        "exit_wing_wall": round(b_cm * GEOMETRY_RATIOS["wing_wall"], 3),
        "approach_section_length": round(b_cm * GEOMETRY_RATIOS["approach_section"], 3),
        "converging_section_length": round(b_cm * GEOMETRY_RATIOS["converging_section"], 3),
        "diverging_section_length": round(b_cm * GEOMETRY_RATIOS["diverging_section"], 3),
        "exit_section_length": round(b_cm * GEOMETRY_RATIOS["exit_section"], 3),
        "overall_length": round(b_cm * GEOMETRY_RATIOS["overall_length"], 3),
        "wall_height": round(b_cm * GEOMETRY_RATIOS["wall_height"], 3),
        "side_wall_angle_deg": SIDE_WALL_ANGLE_DEG,
        "side_slope_ratio": "1:2 (H:V)",
    }


def design_for_throat_width(b_mm):
    coefficient, offset_mm, exponent = _rating_params(b_mm)
    geometry = _build_geometry(b_mm)

    valid_head_max_ft = b_mm * FT_PER_MM  # H_max = b (confirmed design ratio)
    valid_head_min_ft = _min_head_ft(b_mm)

    gpm_coefficient = LS_TO_GPM * coefficient * (304.8 ** exponent)
    gpm_offset_ft = offset_mm / 304.8

    hydraulics = {
        "discharge_equation": {
            "l_s_metric": {
                "coefficient": round(coefficient, 8),
                "offset_mm": round(offset_mm, 4),
                "exponent": round(exponent, 4),
                "formula": f"L/S = {coefficient:.8f} * (H_mm + {offset_mm:.4f})^{exponent:.4f}",
                "head_units": "mm",
            },
            "gpm": {
                "coefficient": round(gpm_coefficient, 6),
                "offset_ft": round(gpm_offset_ft, 6),
                "exponent": round(exponent, 4),
                "formula": f"GPM = {gpm_coefficient:.4f} * (H_ft + {gpm_offset_ft:.4f})^{exponent:.4f}",
                "head_units": "ft",
            },
        },
        "valid_head_range_ft": {
            "min": round(valid_head_min_ft, 4),
            "max": round(valid_head_max_ft, 4),
        },
    }

    max_flow_gpm = _flow_at_head(b_mm, b_mm)
    min_accurate_flow_gpm = _flow_at_head(b_mm, valid_head_min_ft * 304.8)

    return {
        "flume_type": "rbc_custom",
        "size_label": f"custom_{int(round(b_mm))}mm",
        "throat_width_mm": b_mm,
        "entrance_width_cm": round((b_mm / 10.0) * 2, 3),
        "in_confirmed_range": _in_confirmed_range(b_mm),
        "confidence_note": (
            "Interpolated within the range of real, physically-calibrated RBC flumes (50-200mm) - "
            "should be reliable." if _in_confirmed_range(b_mm) else
            "EXTRAPOLATED outside the range of real calibrated data (50-200mm) - treat with more "
            "caution, especially for very small or very large throat widths."
        ),
        "geometry": geometry,
        "hydraulics": hydraulics,
        "operating_range": {
            "max_flow_gpm": round(max_flow_gpm, 3),
            "min_accurate_flow_gpm": round(min_accurate_flow_gpm, 3),
        },
    }


def _solve_b_for_max_flow(target_max_flow_gpm, b_lo=5.0, b_hi=2000.0, tolerance=1e-4, max_iterations=60):
    target = target_max_flow_gpm
    lo, hi = b_lo, b_hi
    for _ in range(max_iterations):
        mid = (lo + hi) / 2
        q = _flow_at_head(mid, mid)  # H_max = b
        if abs(q - target) / target < tolerance:
            return mid
        if q < target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def design_for_requirements(target_max_flow_gpm, target_min_flow_gpm=None, max_channel_width_cm=None):
    """
    Solves for a custom RBC design meeting a target max flow, then checks it against
    optional secondary constraints (minimum accurate flow, max channel width) and
    reports clearly if there's a genuine conflict rather than silently picking one.
    """
    warnings = []

    b_mm = _solve_b_for_max_flow(target_max_flow_gpm)

    # --- Channel width constraint ---
    width_capped = False
    if max_channel_width_cm is not None:
        b_max_from_width = (max_channel_width_cm / 2) * 10  # entrance_width = 2*b (cm) -> mm
        if b_mm > b_max_from_width:
            width_capped = True
            b_mm = b_max_from_width
            achievable_max_flow = _flow_at_head(b_mm, b_mm)
            warnings.append(
                f"Your channel width limits the flume to a {b_mm:.1f}mm throat, which can only "
                f"reach {achievable_max_flow:.1f} GPM at its design head - short of your requested "
                f"{target_max_flow_gpm:.1f} GPM target. Showing the largest design that fits your "
                f"channel width instead."
            )

    design = design_for_throat_width(b_mm)

    # --- Minimum flow accuracy check ---
    if target_min_flow_gpm is not None:
        min_accurate = design["operating_range"]["min_accurate_flow_gpm"]
        if min_accurate > target_min_flow_gpm:
            # Find the (smaller) throat width that WOULD accurately measure the target min flow,
            # and report what max capacity that alternative design would have, so the user can
            # see the actual tradeoff rather than just a warning.
            alt_b = _solve_b_for_min_flow_accuracy(target_min_flow_gpm)
            alt_design = design_for_throat_width(alt_b)
            warnings.append(
                f"This design (sized for your max flow) can only accurately measure down to "
                f"about {min_accurate:.2f} GPM - higher than your stated minimum of "
                f"{target_min_flow_gpm} GPM. A flume small enough to accurately measure your "
                f"minimum flow (throat width {alt_b:.1f}mm) would only handle up to "
                f"{alt_design['operating_range']['max_flow_gpm']:.1f} GPM at its top end. "
                f"A single flume can't optimally cover both ends of this range - consider whether "
                f"your minimum flow estimate is truly a common operating condition, or a rare edge case."
            )

    design["warnings"] = warnings
    design["width_capped"] = width_capped
    return design


def _solve_b_for_min_flow_accuracy(target_min_flow_gpm, b_lo=5.0, b_hi=2000.0, tolerance=1e-4, max_iterations=60):
    """
    Finds the throat width whose min-accurate-flow exactly matches the target minimum flow.
    min_accurate_flow increases monotonically with throat width (bigger flumes are less
    sensitive at low flow), so this uses the same bisection direction as the max-flow solver.
    """
    lo, hi = b_lo, b_hi
    if target_min_flow_gpm == 0:
        return b_lo
    for _ in range(max_iterations):
        mid = (lo + hi) / 2
        min_head_ft = _min_head_ft(mid)
        q = _flow_at_head(mid, min_head_ft * 304.8)
        if abs(q - target_min_flow_gpm) / target_min_flow_gpm < tolerance:
            return mid
        if q < target_min_flow_gpm:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


# Backwards-compatible entry point (used by main.py's existing routes)
def design_for_max_flow(target_max_flow_gpm):
    return design_for_requirements(target_max_flow_gpm)
