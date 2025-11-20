from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field

# App Schemas for MVP

Mode = Literal["auto", "step"]
Fandom = Literal["harry_potter", "game_of_thrones", "generic"]
AssetKind = Literal["image", "voice", "music", "clip"]

class Project(BaseModel):
    title: str
    topic: str
    mode: Mode = "auto"
    fandom: Fandom = "generic"
    use_ai_images: bool = True
    use_stock_media: bool = False
    use_ai_voice: bool = True
    brand_primary: str = "#FACC15"  # yellow-400
    brand_secondary: str = "#18181B"  # zinc-900
    fps: int = 30
    max_seconds: int = 60

class ScriptSegment(BaseModel):
    start: float
    end: float
    text: str

class Script(BaseModel):
    project_id: str
    text: str
    segments: List[ScriptSegment] = Field(default_factory=list)

class MediaAsset(BaseModel):
    project_id: str
    kind: AssetKind
    url: str
    meta: Dict[str, Any] = Field(default_factory=dict)

class RenderJob(BaseModel):
    project_id: str
    status: Literal["queued", "processing", "done", "error"] = "queued"
    output_url: Optional[str] = None
    error: Optional[str] = None
