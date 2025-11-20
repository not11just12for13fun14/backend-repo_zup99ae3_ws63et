from pydantic import BaseModel, Field
from typing import List, Optional

# Each class maps to a MongoDB collection named after the lowercased class

class Project(BaseModel):
    # a "project" is one generated video workflow
    title: str
    topic: str
    mode: str = Field(description="auto or step-by-step")
    status: str = Field(default="draft")
    # provider flags
    use_ai_script: bool = True
    use_ai_voice: bool = True
    use_stock_media: bool = True
    use_ai_images: bool = True
    # brand
    brand_name: Optional[str] = None
    color_primary: Optional[str] = "#FFD54A"
    color_secondary: Optional[str] = "#FFFFFF"
    # lengths
    fps: int = 30
    max_seconds: int = 60

class Script(BaseModel):
    project_id: str
    text: str
    segments: List[str]

class MediaAsset(BaseModel):
    project_id: str
    kind: str  # voice, music, clip, image
    url: str
    attribution: Optional[str] = None
    meta: Optional[dict] = None

class RenderJob(BaseModel):
    project_id: str
    status: str = "queued"
    output_url: Optional[str] = None
    error: Optional[str] = None
