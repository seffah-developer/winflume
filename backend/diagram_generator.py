"""
WinFlume Pro Max - Diagram Generator

Generates simple SVG diagrams of a flume from its catalog geometry data.
Handles the different geometry schemas present in the catalog:
  - "explicit" schema (small 60-deg-V): named segment fields
  - "rbc" / "rbc_custom" schema: wing wall / approach / converging / diverging / exit fields
  - "master_table" schema (large, extra_large, wsc_no4, srcrc_no2, 8inch): letter-coded
    segments (F,G,H,I,J) whose exact physical meaning per-segment isn't fully confirmed yet,
    so these render as a simplified linear taper rather than exact transition points.
  - "parshall" schema: individually-read or intelligently-estimated dimensions
"""

BG_COLOR = "#0B1E38"
GRID_COLOR = "#16304F"
SHAPE_FILL = "#1D4E7A66"
SHAPE_STROKE = "#7DD3FC"
TEXT_COLOR = "#E2E8F0"
TEXT_MUTED = "#8FA8C4"
FLOW_COLOR = "#38BDF8"
DIM_LINE_COLOR = "#4A6C8F"
WARNING_COLOR = "#FBBF24"


def _estimate_text_width(text, font_size=12):
    return len(text) * font_size * 0.62


def _grid_defs_and_bg(svg_width, svg_height):
    return f'''<defs>
    <pattern id="bp-grid" width="24" height="24" patternUnits="userSpaceOnUse">
      <path d="M 24 0 L 0 0 0 24" fill="none" stroke="{GRID_COLOR}" stroke-width="1"/>
    </pattern>
  </defs>
  <rect width="{svg_width}" height="{svg_height}" fill="{BG_COLOR}"/>
  <rect width="{svg_width}" height="{svg_height}" fill="url(#bp-grid)"/>'''


def _get_profile(flume):
    geo = flume.get("geometry")
    if not geo:
        return None

    ftype = flume.get("flume_type")

    # --- RBC schema (including custom-designed RBC flumes, same geometry shape) ---
    if ftype in ("rbc", "rbc_custom"):
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
            "simplified": True,
        }

    # --- Parshall schema ---
    if "converging_axial_length" in geo or "converging_axial_length_B" in geo:
        converging_length = geo.get("converging_axial_length_B", geo.get("converging_axial_length"))
        throat_length = geo.get("throat_length", 0)
        diverging_length = geo.get("diverging_length")
        if diverging_length is None:
            diverging_length = throat_length if throat_length else converging_length * 0.3
        overall_length = geo.get("overall_length", converging_length + throat_length + diverging_length)
        return {
            "entrance_width": geo["entrance_width"],
            "throat_width": geo["throat_width"],
            "exit_width": geo.get("exit_width", geo["throat_width"]),
            "converging_length": converging_length,
            "throat_length": throat_length,
            "diverging_length": diverging_length,
            "overall_length": overall_length,
            "simplified": True,
        }

    return None


def generate_plan_view_svg(flume):
    profile = _get_profile(flume)
    if profile is None:
        return None

    PADDING = 60
    DRAW_WIDTH = 600
    max_width_cm = max(profile["entrance_width"], profile["exit_width"], profile["throat_width"])
    scale_x = DRAW_WIDTH / profile["overall_length"]
    scale_y = min(4.0, 150 / max_width_cm)

    label = f"{flume.get('flume_type', '')} - {flume.get('size_label', '')}"
    min_width_for_label = _estimate_text_width(label, 14) + 2 * PADDING

    svg_width = max(DRAW_WIDTH + 2 * PADDING, min_width_for_label)
    svg_height = max_width_cm * scale_y + 2 * PADDING + 80

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

    top_points = [
        (x0, center_y - ew), (x1, center_y - tw),
        (x2, center_y - tw), (x3, center_y - xw),
    ]
    bottom_points = [
        (x3, center_y + xw), (x2, center_y + tw),
        (x1, center_y + tw), (x0, center_y + ew),
    ]
    all_points = top_points + bottom_points
    points_str = " ".join(f"{x:.1f},{y:.1f}" for x, y in all_points)

    simplified_note = (
        '<text x="{}" y="20" font-size="12" fill="{}" font-style="italic">'
        "Simplified diagram - exact transition points pending geometry verification</text>".format(PADDING, WARNING_COLOR)
        if profile["simplified"]
        else ""
    )

    svg = f'''<svg viewBox="0 0 {svg_width} {svg_height}" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif">
  {_grid_defs_and_bg(svg_width, svg_height)}
  <text x="{PADDING}" y="{svg_height - 15}" font-size="14" fill="{TEXT_COLOR}">{label}</text>
  {simplified_note}

  <line x1="{PADDING - 40}" y1="{center_y}" x2="{PADDING - 10}" y2="{center_y}" stroke="{FLOW_COLOR}" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="{PADDING - 40}" y="{center_y - 10}" font-size="11" fill="{FLOW_COLOR}">FLOW</text>

  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L0,6 L9,3 z" fill="{FLOW_COLOR}"/>
    </marker>
  </defs>

  <polygon points="{points_str}" fill="{SHAPE_FILL}" stroke="{SHAPE_STROKE}" stroke-width="2"/>

  <line x1="{x0}" y1="{center_y}" x2="{x3}" y2="{center_y}" stroke="{DIM_LINE_COLOR}" stroke-width="1" stroke-dasharray="4,4"/>

  <line x1="{x0}" y1="{center_y + xw + 30}" x2="{x3}" y2="{center_y + xw + 30}" stroke="{TEXT_MUTED}" stroke-width="1"/>
  <text x="{(x0 + x3) / 2 - 30}" y="{center_y + xw + 45}" font-size="12" fill="{TEXT_COLOR}">
    Overall: {profile['overall_length']:.1f} cm
  </text>

  <text x="{x1 - 10}" y="{center_y - tw - 8}" font-size="12" fill="{TEXT_COLOR}">
    Throat: {profile['throat_width']:.2f} cm
  </text>

  <text x="{x0 - 10}" y="{center_y - ew - 8}" font-size="12" fill="{TEXT_COLOR}">
    Entrance: {profile['entrance_width']:.2f} cm
  </text>
</svg>'''

    return svg


def generate_elevation_view_svg(flume):
    profile = _get_profile(flume)
    geo = flume.get("geometry")
    if profile is None or geo is None or "wall_height" not in geo:
        return None

    PADDING = 60
    DRAW_WIDTH = 600
    wall_height = geo["wall_height"]
    scale_x = DRAW_WIDTH / profile["overall_length"]
    scale_y = min(6.0, 120 / wall_height)

    label = f"{flume.get('flume_type', '')} - {flume.get('size_label', '')} (Elevation View)"
    min_width_for_label = _estimate_text_width(label, 14) + 2 * PADDING

    svg_width = max(DRAW_WIDTH + 2 * PADDING, min_width_for_label)
    svg_height = wall_height * scale_y + 2 * PADDING + 60

    base_y = svg_height - PADDING - 40
    top_y = base_y - wall_height * scale_y
    x0 = PADDING
    x1 = x0 + DRAW_WIDTH

    is_rbc = flume.get("flume_type") in ("rbc", "rbc_custom")
    if is_rbc:
        ramp_end_x = x0 + (x1 - x0) * 0.55
        outline = (
            f"{x0},{base_y} {x0},{top_y} {x1},{top_y} {x1},{base_y} "
            f"{ramp_end_x},{base_y} {x0},{base_y}"
        )
    else:
        outline = f"{x0},{base_y} {x0},{top_y} {x1},{top_y} {x1},{base_y}"

    svg = f'''<svg viewBox="0 0 {svg_width} {svg_height}" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif">
  {_grid_defs_and_bg(svg_width, svg_height)}
  <text x="{PADDING}" y="{svg_height - 15}" font-size="14" fill="{TEXT_COLOR}">{label}</text>

  <line x1="{x0 - 40}" y1="{(top_y + base_y) / 2}" x2="{x0 - 10}" y2="{(top_y + base_y) / 2}" stroke="{FLOW_COLOR}" stroke-width="2" marker-end="url(#arrow2)"/>
  <text x="{x0 - 40}" y="{(top_y + base_y) / 2 - 10}" font-size="11" fill="{FLOW_COLOR}">FLOW</text>
  <defs>
    <marker id="arrow2" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L0,6 L9,3 z" fill="{FLOW_COLOR}"/>
    </marker>
  </defs>

  <polygon points="{outline}" fill="{SHAPE_FILL}" stroke="{SHAPE_STROKE}" stroke-width="2"/>

  <line x1="{x0 - 20}" y1="{base_y}" x2="{x0 - 20}" y2="{top_y}" stroke="{TEXT_MUTED}" stroke-width="1"/>
  <text x="{x0 - 55}" y="{(top_y + base_y) / 2}" font-size="12" fill="{TEXT_COLOR}" transform="rotate(-90 {x0 - 55} {(top_y + base_y) / 2})">
    Height: {wall_height:.2f} cm
  </text>

  <line x1="{x0}" y1="{base_y + 25}" x2="{x1}" y2="{base_y + 25}" stroke="{TEXT_MUTED}" stroke-width="1"/>
  <text x="{(x0 + x1) / 2 - 40}" y="{base_y + 40}" font-size="12" fill="{TEXT_COLOR}">
    Overall: {profile['overall_length']:.1f} cm
  </text>
</svg>'''

    return svg


def generate_end_view_svg(flume):
    geo = flume.get("geometry")
    profile = _get_profile(flume)
    if geo is None or profile is None or "wall_height" not in geo:
        return None

    PADDING = 60
    RIGHT_LABEL_SPACE = 170
    wall_height = geo["wall_height"]
    throat_width = profile["throat_width"]
    entrance_width = profile["entrance_width"]

    scale = min(8.0, 300 / max(entrance_width, wall_height * 2))

    label = f"{flume.get('flume_type', '')} - {flume.get('size_label', '')} (End View)"
    min_width_for_label = _estimate_text_width(label, 14) + 2 * PADDING

    drawing_width = entrance_width * scale
    svg_width = max(drawing_width + 2 * PADDING + RIGHT_LABEL_SPACE, min_width_for_label)
    svg_height = wall_height * scale + 2 * PADDING + 40

    base_y = svg_height - PADDING - 20
    top_y = base_y - wall_height * scale
    center_x = PADDING + drawing_width / 2

    half_top = (entrance_width * scale) / 2
    half_throat = (throat_width * scale) / 2

    points = (
        f"{center_x - half_top},{top_y} "
        f"{center_x - half_throat},{base_y} "
        f"{center_x + half_throat},{base_y} "
        f"{center_x + half_top},{top_y}"
    )

    angle_label = ""
    if "side_wall_angle_deg" in geo:
        angle_label = f'<text x="{center_x + half_top + 10}" y="{top_y + 15}" font-size="12" fill="{TEXT_COLOR}">{geo["side_wall_angle_deg"]}\u00b0</text>'
    elif "side_slope_angle_deg" in geo:
        angle_label = f'<text x="{center_x + half_top + 10}" y="{top_y + 15}" font-size="12" fill="{TEXT_COLOR}">{geo["side_slope_angle_deg"]}\u00b0</text>'

    svg = f'''<svg viewBox="0 0 {svg_width} {svg_height}" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif">
  {_grid_defs_and_bg(svg_width, svg_height)}
  <text x="{PADDING}" y="{svg_height - 10}" font-size="14" fill="{TEXT_COLOR}">{label}</text>

  <polygon points="{points}" fill="{SHAPE_FILL}" stroke="{SHAPE_STROKE}" stroke-width="2"/>
  {angle_label}

  <text x="{center_x - half_top}" y="{top_y - 10}" font-size="12" fill="{TEXT_COLOR}">
    Width: {entrance_width:.2f} cm
  </text>
  <text x="{center_x + half_throat + 5}" y="{base_y + 15}" font-size="12" fill="{TEXT_COLOR}">
    Throat: {throat_width:.2f} cm
  </text>
</svg>'''

    return svg
