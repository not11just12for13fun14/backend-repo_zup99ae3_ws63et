from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import httpx
import os
from schemas import Project, Script, MediaAsset, RenderJob

app = FastAPI(title="AI Shorts Studio")

# CORS
frontend_url = os.getenv("FRONTEND_URL", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory demo store for MVP endpoints that don't persist assets
# DB helpers are available (Mongo), but for this scaffold we keep minimal state.
PROJECTS: dict[str, Project] = {}
SCRIPTS: dict[str, Script] = {}
ASSETS: dict[str, List[MediaAsset]] = {}
RENDERS: dict[str, RenderJob] = {}

class CreateProjectBody(BaseModel):
    title: str
    topic: str
    mode: str  # auto or step
    brand_name: Optional[str] = None
    fandom: Optional[str] = None  # e.g., "harry_potter" or "game_of_thrones"

class GenerateScriptBody(BaseModel):
    project_id: str
    topic: Optional[str] = None

class ProvideScriptBody(BaseModel):
    project_id: str
    text: str

class GenerateAIImagesBody(BaseModel):
    project_id: str
    prompts: Optional[List[str]] = None
    fandom: Optional[str] = None

@app.get("/health")
async def health():
    return {"ok": True}

@app.post("/project")
async def create_project(body: CreateProjectBody):
    pid = f"proj_{len(PROJECTS)+1}"
    project = Project(
        title=body.title,
        topic=body.topic,
        mode=body.mode,
        brand_name=body.brand_name,
        use_ai_images=True,
    )
    PROJECTS[pid] = project
    return {"project_id": pid, "project": project}

@app.post("/script/generate")
async def generate_script(body: GenerateScriptBody):
    if body.project_id not in PROJECTS:
        raise HTTPException(404, "Project not found")
    topic = body.topic or PROJECTS[body.project_id].topic
    # Placeholder script generator for MVP without external API keys
    # Structure: Hook → 3 bullets → CTA
    hook = f"What if I told you {topic} hides a secret you missed?"
    bullets = [
        f"Hidden detail #1 about {topic}",
        f"Hidden detail #2 that changes everything",
        f"A fan theory that actually makes sense",
    ]
    cta = "Follow for more bite-sized lore!"
    segments = [hook] + bullets + [cta]
    text = "\n".join(segments)
    script = Script(project_id=body.project_id, text=text, segments=segments)
    SCRIPTS[body.project_id] = script
    return {"script": script}

@app.post("/script/provide")
async def provide_script(body: ProvideScriptBody):
    if body.project_id not in PROJECTS:
        raise HTTPException(404, "Project not found")
    # naive segmentation: split by newline or sentences
    segs = [s.strip() for s in body.text.replace("\r","\n").split("\n") if s.strip()]
    if not segs:
        segs = [body.text]
    script = Script(project_id=body.project_id, text=body.text, segments=segs)
    SCRIPTS[body.project_id] = script
    return {"script": script}

@app.post("/assets/ai-images")
async def generate_ai_images(body: GenerateAIImagesBody):
    if body.project_id not in PROJECTS:
        raise HTTPException(404, "Project not found")
    fandom = body.fandom or "generic"
    prompts = body.prompts or [
        f"cinematic portrait, {fandom} style, magical particles, ultra detail, 9:16",
        f"dynamic action shot, {fandom} vibes, volumetric light, 9:16",
        f"mystical landscape, {fandom} world, fog, depth, 9:16",
    ]
    # For MVP without image API keys, return placeholder animated image URLs (licensed free loops)
    # In production, integrate Stable Diffusion or Flux API and return generated URLs from storage
    sample_gifs = [
        "https://media.tenor.com/9v0Yw6Z0v2cAAAAC/magic-loop.gif",
        "https://media.tenor.com/tk2b8h7VJ24AAAAC/fantasy-landscape.gif",
        "https://media.tenor.com/7xgq6sVJ0bUAAAAC/smoke-magic.gif",
    ]
    assets = [
        MediaAsset(project_id=body.project_id, kind="image", url=url, meta={"prompt": p})
        for url, p in zip(sample_gifs, prompts)
    ]
    ASSETS.setdefault(body.project_id, []).extend(assets)
    return {"assets": assets}

class TTSBody(BaseModel):
    project_id: str
    voice: Optional[str] = "female_neutral"

@app.post("/assets/voice")
async def generate_voiceover(body: TTSBody):
    if body.project_id not in PROJECTS:
        raise HTTPException(404, "Project not found")
    if body.project_id not in SCRIPTS:
        raise HTTPException(400, "Script missing")
    # Placeholder TTS URL; integrate ElevenLabs or AWS Polly in production
    url = "https://files.freemusicarchive.org/storage-freemusicarchive-org/music/no_curator/Scott_Holmes_Music/Happy_Music/Scott_Holmes_Music_-_05_-_Upbeat_Party.mp3"
    asset = MediaAsset(project_id=body.project_id, kind="voice", url=url)
    ASSETS.setdefault(body.project_id, []).append(asset)
    return {"asset": asset}

@app.get("/project/{project_id}")
async def get_project(project_id: str):
    project = PROJECTS.get(project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    return {
        "project": project,
        "script": SCRIPTS.get(project_id),
        "assets": ASSETS.get(project_id, []),
        "render": RENDERS.get(project_id),
    }
