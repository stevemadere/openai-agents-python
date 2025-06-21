
from __future__ import annotations

from typing import Literal, TypedDict

class TextContentPart(TypedDict):
    type: Literal["input_text"]
    text: str

class ImageContentPart(TypedDict):
    type: Literal["input_image"]
    image_url: str

class HoistedFunctionCallOutputArtifact(TypedDict):
    role: Literal["user"]
    content: list[TextContentPart | ImageContentPart]
    # Reference to the original tool call id
    tool_call_id: str

__all__ = ["HoistedFunctionCallOutputArtifact", "TextContentPart", "ImageContentPart"]
