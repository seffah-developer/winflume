from fastapi import FastAPI, HTTPException,  Response
from fastapi.middleware.cors import CORSMiddleware
from catalog_loader import load_catalog
from recommender import recommend
from diagram_generator import generate_plan_view_svg


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "WinFlume Pro Max backend is alive"}

@app.get("/flumes")
def list_flumes():
    return load_catalog()

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