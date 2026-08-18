import json
from pathlib import Path
from flume_characteristics import get_characteristics

CATALOG_DIR = Path(__file__).parent / "catalog"

def load_catalog():
    """
    Scans the catalog/ directory recursively for .json files,
    loads each one, and returns a list of flume spec dicts.
    Each entry gets an added 'id' field derived from its file path,
    plus a 'characteristics' field with practical guidance for its family.
    """
    flumes = []
    for json_file in CATALOG_DIR.rglob("*.json"):
        with open(json_file, "r") as f:
            data = json.load(f)

        relative = json_file.relative_to(CATALOG_DIR)
        flume_id = "__".join(relative.with_suffix("").parts)
        data["id"] = flume_id
        data["characteristics"] = get_characteristics(data.get("flume_type"))

        flumes.append(data)

    return flumes
