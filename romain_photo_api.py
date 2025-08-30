
import os, json
from urllib.parse import quote
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="Private Photo Catalog API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

with open("romain_manifest.json") as f:
    DATA = json.load(f)

BASE = os.environ.get("IMAGE_BASE_URL", "https://YOUR-R2-PUBLIC-DOMAIN")  # e.g. https://cdn.yourdomain.com

def match(rec, q=None, photographer=None, vibe=None, composition=None, place=None, subject=None, color=None, orientation=None):
    ok = True
    if q:
        ql = q.lower()
        ok = ql in rec["photographer"].lower() or ql in rec["filename"].lower()
    if ok and photographer:
        ok = photographer.lower() in rec["photographer"].lower()
    if ok and vibe:
        ok = (rec.get("vibe") or "").lower().find(vibe.lower()) >= 0
    if ok and composition:
        ok = (rec.get("composition") or "").lower().find(composition.lower()) >= 0
    if ok and place:
        ok = (rec.get("place") or "").lower().find(place.lower()) >= 0
    if ok and subject:
        ok = (rec.get("subject") or "").lower().find(subject.lower()) >= 0
    if ok and color:
        ok = (rec.get("color_family") or "").lower() == color.lower()
    if ok and orientation:
        ok = (rec.get("orientation") or "") == orientation
    return ok

@app.get("/search")
def search(q: str | None = None,
           photographer: str | None = None,
           vibe: str | None = None,
           composition: str | None = None,
           place: str | None = None,
           subject: str | None = None,
           color: str | None = None,
           orientation: str | None = None,
           limit: int = 24):
    results = []
    for rec in DATA:
        if match(rec, q, photographer, vibe, composition, place, subject, color, orientation):
            url = BASE.rstrip("/") + "/" + quote(rec["r2_key"])
            results.append({
                "photographer": rec["photographer"],
                "filename": rec["filename"],
                "url": url,
                "width": rec.get("width"),
                "height": rec.get("height"),
                "orientation": rec.get("orientation"),
                "color_family": rec.get("color_family"),
                "dominant_color": rec.get("dominant_color"),
                "vibe": rec.get("vibe"),
                "composition": rec.get("composition"),
                "place": rec.get("place"),
                "subject": rec.get("subject"),
            })
            if len(results) >= limit:
                break
    return {"results": results}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
