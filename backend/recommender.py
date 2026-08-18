"""
WinFlume Pro Max - Flume Recommender

Given a user's expected flow range, available head loss, and channel width,
filters and ranks catalog flumes to find the best fit.
"""

CFS_TO_GPM = 448.831


def _get_flow_range_gpm(flume):
    """
    Returns (min_gpm, max_gpm) for a flume's operating range, normalizing
    across the different unit conventions used in the catalog.
    Returns (None, None) if no usable flow data exists.
    """
    op = flume.get("operating_range", {})

    min_gpm = op.get("min_flow_gpm")
    max_gpm = op.get("max_flow_gpm")

    if max_gpm is None and op.get("max_flow_cfs") is not None:
        max_gpm = op["max_flow_cfs"] * CFS_TO_GPM
    if min_gpm is None and op.get("min_flow_cfs") is not None:
        min_gpm = op["min_flow_cfs"] * CFS_TO_GPM

    return min_gpm, max_gpm


def _get_required_head_ft(flume):
    """Returns the head (ft) needed to measure this flume's max design flow."""
    hydraulics = flume.get("hydraulics", {})
    head_range = hydraulics.get("valid_head_range_ft", {})
    return head_range.get("max")


def _get_channel_width_cm(flume):
    """
    Returns the flume's outer footprint width (cm) - the minimum channel
    width it needs to fit in. Tries several field names since geometry
    schemas differ slightly by flume family. Where both an entrance and
    exit width exist, uses the wider of the two (conservative fit check).
    """
    geometry = flume.get("geometry")
    if not geometry:
        return None

    for key in ("approach_width", "approach_exit_width"):
        if key in geometry:
            return geometry[key]

    if "entrance_width" in geometry or "exit_width" in geometry:
        candidates = [geometry.get("entrance_width"), geometry.get("exit_width")]
        candidates = [c for c in candidates if c is not None]
        if candidates:
            return max(candidates)

    # RBC family: approximate outer width as throat + 2x entrance wing wall
    if "entrance_wing_wall" in geometry and "throat_width" in geometry:
        return geometry["throat_width"] + 2 * geometry["entrance_wing_wall"]

    return None


def recommend(min_flow_gpm, max_flow_gpm, available_head_ft, channel_width_cm, catalog):
    """
    Filters and ranks flumes from the catalog against user requirements.
    Returns a list of dicts: {flume, fits, reasons_excluded (if any)}
    """
    results = []

    for flume in catalog:
        reasons_excluded = []

        flume_min_gpm, flume_max_gpm = _get_flow_range_gpm(flume)
        if flume_min_gpm is None or flume_max_gpm is None:
            reasons_excluded.append("Flow range data unavailable for this flume")
        else:
            if max_flow_gpm > flume_max_gpm:
                reasons_excluded.append(
                    f"Max flow ({max_flow_gpm:.2f} GPM) exceeds flume capacity ({flume_max_gpm:.2f} GPM)"
                )
            if min_flow_gpm < flume_min_gpm:
                reasons_excluded.append(
                    f"Min flow ({min_flow_gpm:.2f} GPM) is below flume's minimum accurate range ({flume_min_gpm:.2f} GPM)"
                )

        required_head_ft = _get_required_head_ft(flume)
        if required_head_ft is None:
            reasons_excluded.append("Head requirement data unavailable for this flume")
        elif required_head_ft > available_head_ft:
            reasons_excluded.append(
                f"Requires {required_head_ft:.2f} ft of head, more than the {available_head_ft:.2f} ft available"
            )

        flume_width_cm = _get_channel_width_cm(flume)
        if flume_width_cm is None:
            reasons_excluded.append("Width data unavailable for this flume")
        elif flume_width_cm > channel_width_cm:
            reasons_excluded.append(
                f"Flume width ({flume_width_cm:.1f} cm) exceeds channel width ({channel_width_cm:.1f} cm)"
            )

        fits = len(reasons_excluded) == 0

        results.append({
            "id": flume.get("id"),
            "flume_type": flume.get("flume_type"),
            "size_label": flume.get("size_label"),
            "fits": fits,
            "reasons_excluded": reasons_excluded,
            "max_flow_gpm": flume_max_gpm,
            "min_flow_gpm": flume_min_gpm,
            "required_head_ft": required_head_ft,
            "flume_width_cm": flume_width_cm,
            "characteristics": flume.get("characteristics"),
        })

    # Sort: fitting flumes first (smallest max_flow_gpm = smallest flume that works),
    # then non-fitting flumes after
    def sort_key(r):
        return (not r["fits"], r["max_flow_gpm"] if r["max_flow_gpm"] is not None else float("inf"))

    results.sort(key=sort_key)
    return results
