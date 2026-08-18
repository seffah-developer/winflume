from typing import Optional

from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from catalog_loader import load_catalog
from recommender import recommend
from diagram_generator import generate_plan_view_svg, generate_elevation_view_svg, generate_end_view_svg
from discharge_calculator import compute_discharge_table
from rbc_custom_designer import design_for_requirements
from flume_characteristics import get_characteristics

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://winflume.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serves original manufacturer PDFs from backend/original_drawings/ at /drawings/<filename>
app.mount("/drawings", StaticFiles(directory="original_drawings"), name="drawings")


@app.get("/")
def read_root():
    return {"message": "WinFlume Pro Max backend is alive"}


@app.get("/flumes")
def list_flumes():
    return load_catalog()


@app.get("/flumes/{flume_id}")
def get_flume(flume_id: str):
    flumes = load_catalog()
    for flume in flumes:
        if flume["id"] == flume_id:
            return flume
    raise HTTPException(status_code=404, detail=f"Flume '{flume_id}' not found")


@app.get("/recommend")
def recommend_flume(
    min_flow_gpm: float,
    max_flow_gpm: float,
    available_head_ft: float,
    channel_width_cm: float,
):
    catalog = load_catalog()
    results = recommend(min_flow_gpm, max_flow_gpm, available_head_ft, channel_width_cm, catalog)
    return results


@app.get("/flumes/{flume_id}/diagram")
def get_flume_diagram(flume_id: str):
    flumes = load_catalog()
    flume = next((f for f in flumes if f["id"] == flume_id), None)
    if flume is None:
        raise HTTPException(status_code=404, detail=f"Flume '{flume_id}' not found")

    svg = generate_plan_view_svg(flume)
    if svg is None:
        raise HTTPException(status_code=422, detail="No geometry available to generate a diagram for this flume")

    return Response(content=svg, media_type="image/svg+xml")


@app.get("/flumes/{flume_id}/diagram/elevation")
def get_flume_elevation(flume_id: str):
    flumes = load_catalog()
    flume = next((f for f in flumes if f["id"] == flume_id), None)
    if flume is None:
        raise HTTPException(status_code=404, detail=f"Flume '{flume_id}' not found")

    svg = generate_elevation_view_svg(flume)
    if svg is None:
        raise HTTPException(status_code=422, detail="No elevation data available")

    return Response(content=svg, media_type="image/svg+xml")


@app.get("/flumes/{flume_id}/diagram/end")
def get_flume_end_view(flume_id: str):
    flumes = load_catalog()
    flume = next((f for f in flumes if f["id"] == flume_id), None)
    if flume is None:
        raise HTTPException(status_code=404, detail=f"Flume '{flume_id}' not found")

    svg = generate_end_view_svg(flume)
    if svg is None:
        raise HTTPException(status_code=422, detail="No end-view data available")

    return Response(content=svg, media_type="image/svg+xml")


@app.get("/flumes/{flume_id}/discharge")
def get_flume_discharge(flume_id: str):
    flumes = load_catalog()
    flume = next((f for f in flumes if f["id"] == flume_id), None)
    if flume is None:
        raise HTTPException(status_code=404, detail=f"Flume '{flume_id}' not found")
    return compute_discharge_table(flume)


# --- Custom RBC flume designer ---

@app.get("/design/rbc-custom")
def design_custom_rbc(
    target_max_flow_gpm: float,
    target_min_flow_gpm: Optional[float] = None,
    max_channel_width_cm: Optional[float] = None,
):
    design = design_for_requirements(target_max_flow_gpm, target_min_flow_gpm, max_channel_width_cm)
    design["id"] = "rbc_custom__preview"
    design["characteristics"] = get_characteristics("rbc")
    return design


@app.get("/design/rbc-custom/diagram")
def get_custom_rbc_diagram(
    target_max_flow_gpm: float,
    target_min_flow_gpm: Optional[float] = None,
    max_channel_width_cm: Optional[float] = None,
):
    design = design_for_requirements(target_max_flow_gpm, target_min_flow_gpm, max_channel_width_cm)
    design["id"] = "rbc_custom__preview"
    svg = generate_plan_view_svg(design)
    return Response(content=svg, media_type="image/svg+xml")


@app.get("/design/rbc-custom/diagram/elevation")
def get_custom_rbc_elevation(
    target_max_flow_gpm: float,
    target_min_flow_gpm: Optional[float] = None,
    max_channel_width_cm: Optional[float] = None,
):
    design = design_for_requirements(target_max_flow_gpm, target_min_flow_gpm, max_channel_width_cm)
    design["id"] = "rbc_custom__preview"
    svg = generate_elevation_view_svg(design)
    return Response(content=svg, media_type="image/svg+xml")


@app.get("/design/rbc-custom/diagram/end")
def get_custom_rbc_end(
    target_max_flow_gpm: float,
    target_min_flow_gpm: Optional[float] = None,
    max_channel_width_cm: Optional[float] = None,
):
    design = design_for_requirements(target_max_flow_gpm, target_min_flow_gpm, max_channel_width_cm)
    design["id"] = "rbc_custom__preview"
    svg = generate_end_view_svg(design)
    return Response(content=svg, media_type="image/svg+xml")
