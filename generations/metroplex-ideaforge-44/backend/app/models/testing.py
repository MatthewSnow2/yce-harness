"""Testing related data models"""

from pydantic import BaseModel
from typing import Dict, List


class UserPersona(BaseModel):
    """User persona template"""
    persona_id: str
    name: str
    description: str
    traits: List[str]
    communication_style: str
    example_phrases: List[str]


class IntentRecognition(BaseModel):
    """Intent recognition result"""
    intent: str
    confidence: float
    entities: Dict[str, str] = {}
