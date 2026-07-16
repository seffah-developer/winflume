"""
WinFlume Pro Max - Diagram Generator

Generates a simple plan-view SVG diagram of a flume from its catalog geometry data.
Handles the different geometry schemas present in the catalog:
  - "explicit" schema (small 60-deg-V): named segment fields
  - "rbc" schema: wing wall / approach / converging / diverging / exit fields
  - "master_table" schema (large, extra_large, wsc_no4, srcrc_no2, 8inch): letter-coded
    segments (F,G,H,I,J) whose exact physical meaning per-segment isn't fully confirmed yet,
    so these render as a simplified linear taper rather than exact transition points.
"""


def _get_profile(flume):
    """
    Normalizes a flume's geometry into a common profile dict:
    {
      entrance_width, throat_width, exit_width,
      converging_length, throat_length, diverging_length,
      overall_length, simplified (bool)
    }
    Returns None if geometry is unavailable.
    """
    geo = flume.get("geometry")
    if not geo:
        return None

    ftype = flume.get("flume_type")

    # --- RBC schema ---
    if ftype == "rbc":
        b = geo["throat_width"]
        return {
            "entrance_width": b + 2 * geo["entrance_wing_wall"],
            "throat_width": b,
            "exit_width": b + 2 * geo["exit_wing_wall"],
            "converging_length": geo["converging_section_length"],
            "throat_length": 0,
            "diverging_length": geo["diverging_section_length"],
            "overall_length": geo["overall_length"],
            "simplified": False,
        }

    # --- Explicit schema (small 60-deg-V) ---
    if "approach_width" in geo and "converging_section_length" in geo:
        return {
            "entrance_width": geo["approach_width"],
            "throat_width": geo["throat_width"],
            "exit_width": geo.get("exit_width", geo["approach_width"]),
            "converging_length": geo["converging_section_length"],
            "throat_length": geo.get("throat_length", 0),
            "diverging_length": geo["diverging_section_length"],
            "overall_length": geo["overall_length"],
            "simplified": False,
        }

    # --- Master-table schema (large, extra_large, wsc_no4, srcrc_no2, 8inch) ---
    if "approach_exit_width" in geo and "segment_lengths" in geo:
        segs = geo["segment_lengths"]
        total_taper_length = geo["overall_length"] - 2 * segs["segment_J"]
        return {
            "entrance_width": geo["approach_exit_width"],
            "throat_width": geo["throat_width"],
            "exit_width": geo["approach_exit_width"],
            "converging_length": total_taper_length / 2,
            "throat_length": 0,
            "diverging_length": total_taper_length / 2,
            "overall_length": geo["overall_length"],
            "simplified": True,  # exact segment transitions not yet confirmed
        }

    return None


def generate_plan_view_svg(flume):
    """Returns an SVG string (plan view) for the given flume, or None if geometry unavailable."""
    profile = _get_profile(flume)
    if profile is None:
        return None

    # Layout constants
    PADDING = 60
    DRAW_WIDTH = 600
    max_width_cm = max(profile["entrance_width"], profile["exit_width"], profile["throat_width"])
    scale_x = DRAW_WIDTH / profile["overall_length"]
    scale_y = min(4.0, 150 / max_width_cm)  # cap vertical exaggeration so thin throats stay visible

    svg_width = DRAW_WIDTH + 2 * PADDING
    svg_height = max_width_cm * scale_y + 2 * PADDING + 80  # extra space for labels

    cx = svg_height / 2  # centerline y (will recompute below properly)
    center_y = PADDING + (max_width_cm * scale_y) / 2 + 40

    def half(w_cm):
        return (w_cm * scale_y) / 2

    x0 = PADDING
    x1 = x0 + profile["converging_length"] * scale_x
    x2 = x1 + profile["throat_length"] * scale_x
    x3 = x2 + profile["diverging_length"] * scale_x

    ew = half(profile["entrance_width"])
    tw = half(profile["throat_width"])
    xw = half(profile["exit_width"])

    # Outline points (top edge then bottom edge, forming closed trapezoid channel)
    top_points = [
        (x0, center_y - ew),
        (x1, center_y - tw),
        (x2, center_y - tw),
        (x3, center_y - xw),
    ]
    bottom_points = [
        (x3, center_y + xw),
        (x2, center_y + tw),
        (x1, center_y + tw),
        (x0, center_y + ew),
    ]
    all_points = top_points + bottom_points
    points_str = " ".join(f"{x:.1f},{y:.1f}" for x, y in all_points)

    simplified_note = (
        '<text x="{}" y="20" font-size="12" fill="#b45309" font-style="italic">'
        "Simplified diagram - exact transition points pending geometry verification</text>".format(PADDING)
        if profile["simplified"]
        else ""
    )

    label = f"{flume.get('flume_type', '')} - {flume.get('size_label', '')}"

    svg = f'''<svg viewBox="0 0 {svg_width} {svg_height}" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif">
  <rect width="100%" height="100%" fill="white"/>
  <text x="{PADDING}" y="{svg_height - 15}" font-size="14" fill="#111">{label}</text>
  {simplified_note}

  <!-- Flow arrow -->
  <line x1="{PADDING - 40}" y1="{center_y}" x2="{PADDING - 10}" y2="{center_y}" stroke="#2563eb" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="{PADDING - 40}" y="{center_y - 10}" font-size="11" fill="#2563eb">FLOW</text>

  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L0,6 L9,3 z" fill="#2563eb"/>
    </marker>
  </defs>

  <!-- Flume outline -->
  <polygon points="{points_str}" fill="#dbeafe" stroke="#1e3a8a" stroke-width="2"/>

  <!-- Centerline -->
  <line x1="{x0}" y1="{center_y}" x2="{x3}" y2="{center_y}" stroke="#94a3b8" stroke-width="1" stroke-dasharray="4,4"/>

  <!-- Dimension: overall length -->
  <line x1="{x0}" y1="{center_y + xw + 30}" x2="{x3}" y2="{center_y + xw + 30}" stroke="#111" stroke-width="1"/>
  <text x="{(x0 + x3) / 2 - 30}" y="{center_y + xw + 45}" font-size="12" fill="#111">
    Overall: {profile['overall_length']:.1f} cm
  </text>

  <!-- Dimension: throat width -->
  <text x="{x1 - 10}" y="{center_y - tw - 8}" font-size="12" fill="#111">
    Throat: {profile['throat_width']:.2f} cm
  </text>

  <!-- Dimension: entrance width -->
  <text x="{x0 - 10}" y="{center_y - ew - 8}" font-size="12" fill="#111">
    Entrance: {profile['entrance_width']:.2f} cm
  </text>
</svg>'''

    return svg