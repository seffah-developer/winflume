from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from catalog_loader import load_catalog
from recommender import recommend

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