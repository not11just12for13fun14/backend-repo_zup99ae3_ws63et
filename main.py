import os
import random
import uuid
from typing import Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from schemas import Project, Script, ScriptSegment, MediaAsset, RenderJob

app = FastAPI(title="AI Shorts Studio API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory MVP stores
PROJECTS: Dict[str, Project] = {}
SCRIPTS: Dict[str, Script] = {}
ASSETS: Dict[str, List[MediaAsset]] = {}
RENDERS: Dict[str, RenderJob] = {}

class CreateProjectReq(BaseModel):
    title: str
    topic: str
    mode: str = "auto"
    fandom: str = "generic"

class ScriptGenerateReq(BaseModel):
    project_id: str
    topic: str

class ScriptProvideReq(BaseModel):
    project_id: str
    text: str

class AIImagesReq(BaseModel):
    project_id: str
    fandom: str = "generic"

class VoiceReq(BaseModel):
    project_id: str

@app.get("/")
def root():
    return {"message": "AI Shorts Studio Backend running"}

@app.post("/project")
def create_project(req: CreateProjectReq):
    pid = str(uuid.uuid4())
    project = Project(title=req.title, topic=req.topic, mode=req.mode, fandom=req.fandom)
    PROJECTS[pid] = project
    return {"project_id": pid}

@app.get("/project/{project_id}")
def get_project(project_id: str):
    project = PROJECTS.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    script = SCRIPTS.get(project_id)
    assets = ASSETS.get(project_id, [])
    render = RENDERS.get(project_id)
    return {"project": project, "script": script, "assets": assets, "render": render}

@app.post("/script/generate")
def generate_script(req: ScriptGenerateReq):
    if req.project_id not in PROJECTS:
        raise HTTPException(status_code=404, detail="Project not found")
    # Simple templated script 45-60s
    bullets = [
        "Hook: a jaw-dropping reveal in 5 seconds",
        "Point 1: surprising lore detail",
        "Point 2: fan theory twist",
        "Point 3: what most fans miss",
        "CTA: follow for more in-universe secrets"
    ]
    text = (f"Topic: {req.topic}\n" + "\n".join(f"- {b}" for b in bullets))
    # Segments across ~55s
    segments = [
        ScriptSegment(start=0.0, end=5.0, text="Hook"),
        ScriptSegment(start=5.0, end=20.0, text="Point 1"),
        ScriptSegment(start=20.0, end=35.0, text="Point 2"),
        ScriptSegment(start=35.0, end=50.0, text="Point 3"),
        ScriptSegment(start=50.0, end=58.0, text="CTA"),
    ]
    script = Script(project_id=req.project_id, text=text, segments=segments)
    SCRIPTS[req.project_id] = script
    return {"ok": True}

@app.post("/script/provide")
def provide_script(req: ScriptProvideReq):
    if req.project_id not in PROJECTS:
        raise HTTPException(status_code=404, detail="Project not found")
    # naive segmentation: split by lines
    lines = [l.strip() for l in req.text.splitlines() if l.strip()]
    dur = 55
    per = max(1, dur // max(1, len(lines)))
    t = 0
    segs = []
    for l in lines:
        segs.append(ScriptSegment(start=float(t), end=float(min(dur, t+per)), text=l))
        t += per
    script = Script(project_id=req.project_id, text=req.text, segments=segs)
    SCRIPTS[req.project_id] = script
    return {"ok": True}

HP_GIFS = [
    "https://media.tenor.com/1.gif",
    "https://media.tenor.com/2.gif",
    "https://media.tenor.com/3.gif",
]
GOT_GIFS = [
    "https://media.tenor.com/a.gif",
    "https://media.tenor.com/b.gif",
    "https://media.tenor.com/c.gif",
]
GENERIC_GIFS = [
    "https://media.tenor.com/x.gif",
    "https://media.tenor.com/y.gif",
    "https://media.tenor.com/z.gif",
]

@app.post("/assets/ai-images")
def ai_images(req: AIImagesReq):
    if req.project_id not in PROJECTS:
        raise HTTPException(status_code=404, detail="Project not found")
    fandom = req.fandom
    pool = GENERIC_GIFS
    prompts = []
    if fandom == "harry_potter":
        pool = HP_GIFS
        prompts = ["wand sparks", "hogwarts castle night", "patronus mist"]
    elif fandom == "game_of_thrones":
        pool = GOT_GIFS
        prompts = ["dragon flight", "winterfell snow drift", "sword sparks"]
    else:
        prompts = ["magic particles", "fantasy landscape", "mystic smoke"]

    picked = random.sample(pool, k=min(3, len(pool)))
    assets = [
        MediaAsset(project_id=req.project_id, kind="image", url=url, meta={"prompt": p, "fandom": fandom})
        for url, p in zip(picked, prompts)
    ]
    ASSETS.setdefault(req.project_id, [])
    ASSETS[req.project_id].extend(assets)
    return {"count": len(assets)}

@app.post("/assets/voice")
def voice(req: VoiceReq):
    if req.project_id not in PROJECTS:
        raise HTTPException(status_code=404, detail="Project not found")
    # placeholder TTS
    tts_url = "https://cdn.pixabay.com/download/audio/2022/02/23/audio_6b3c.mp3?filename=neutral-female-voiceover-sample.mp3"
    asset = MediaAsset(project_id=req.project_id, kind="voice", url=tts_url, meta={"voice": "female_neutral", "lang": "en-US"})
    ASSETS.setdefault(req.project_id, [])
    ASSETS[req.project_id].append(asset)
    return {"ok": True}

@app.get("/health")
def health():
    return {"ok": True}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
