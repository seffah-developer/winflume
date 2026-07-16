"""
WinFlume Pro Max - Discharge Calculator

Computes a head-vs-flow table from a flume's stored discharge equation(s),
and returns the equations themselves in human-readable form.
Handles both structured equations (coefficient/exponent/offset) and
plain formula-string equations (polynomial / multi-term forms).
"""

import math
import re


def _eval_formula_string(formula, head_value):
    """
    Safely evaluates a simple formula string like:
      "CFS = 2.22 * H_ft^1.5 + 1.467 * H_ft^2.5"
      "CFS = 0.107702 - 2.33095*H + 20.9685*H^2 - ..."
    by substituting the head variable and using a restricted eval.
    """
    rhs = formula.split("=", 1)[1].strip()
    # Normalize variable names to a single symbol H
    rhs = re.sub(r"H_ft|H_mm|H_m\b|H\b", "H", rhs)
    rhs = rhs.replace("^", "**")

    try:
        return eval(rhs, {"__builtins__": {}}, {"H": head_value, "math": math})
    except Exception:
        return None


def _compute_structured(eq, head_value):
    """Computes flow using coefficient/exponent/offset fields."""
    coeff = eq.get("coefficient")
    exponent = eq.get("exponent")
    offset = eq.get("offset_ft", eq.get("offset_mm", 0)) or 0
    if coeff is None or exponent is None:
        return None
    try:
        return coeff * (head_value + offset) ** exponent
    except Exception:
        return None


def get_primary_equation(flume):
    """
    Returns the best available discharge equation block for a flume,
    handling the different schema variants in the catalog.
    """
    hydraulics = flume.get("hydraulics", {})

    if "discharge_equation" in hydraulics:
        return hydraulics["discharge_equation"]
    if "discharge_equation_primary" in hydraulics:
        return hydraulics["discharge_equation_primary"]
    return None


def compute_discharge_table(flume, num_points=15):
    """
    Returns a list of {head_ft, flow_gpm} dicts computed across the flume's
    valid head range, plus the equation formulas used (for display).
    """
    hydraulics = flume.get("hydraulics", {})
    head_range = hydraulics.get("valid_head_range_ft", {})
    head_min = head_range.get("min")
    head_max = head_range.get("max")

    if head_min is None or head_max is None:
        return {"table": [], "equations": {}, "error": "No valid head range available"}

    eq_block = get_primary_equation(flume)
    if eq_block is None:
        return {"table": [], "equations": {}, "error": "No discharge equation available"}

    # Prefer GPM if available (structured), else fall back to formula string (usually CFS)
    gpm_eq = eq_block.get("gpm")
    cfs_eq = eq_block.get("cfs")

    table = []
    step = (head_max - head_min) / (num_points - 1) if num_points > 1 else 0

    for i in range(num_points):
        h = head_min + step * i
        flow_gpm = None

        if gpm_eq and "coefficient" in gpm_eq:
            flow_gpm = _compute_structured(gpm_eq, h)
        elif cfs_eq and "coefficient" in cfs_eq:
            flow_cfs = _compute_structured(cfs_eq, h)
            flow_gpm = flow_cfs * 448.831 if flow_cfs is not None else None
        elif cfs_eq and "formula" in cfs_eq:
            flow_cfs = _eval_formula_string(cfs_eq["formula"], h)
            flow_gpm = flow_cfs * 448.831 if flow_cfs is not None else None
        elif gpm_eq and "formula" in gpm_eq:
            flow_gpm = _eval_formula_string(gpm_eq["formula"], h)

        table.append({
            "head_ft": round(h, 4),
            "flow_gpm": round(flow_gpm, 3) if flow_gpm is not None else None,
        })

    formulas = {}
    for key in ("cfs", "gpm", "l_s_metric", "mgd", "m3hr_metric"):
        if key in eq_block and "formula" in eq_block[key]:
            formulas[key] = eq_block[key]["formula"]

    return {
        "table": table,
        "equations": formulas,
        "valid_head_range_ft": head_range,
        "error": None,
    }