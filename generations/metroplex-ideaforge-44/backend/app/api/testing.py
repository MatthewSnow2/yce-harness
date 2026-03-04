"""API endpoints for testing utilities"""

from fastapi import APIRouter
from typing import List

from ..models.testing import UserPersona
from ..services.conversation_simulator import ConversationSimulator

router = APIRouter(prefix="/api", tags=["testing"])
simulator = ConversationSimulator()


@router.get("/personas", response_model=List[UserPersona])
def list_personas():
    """List all available user personas"""
    return simulator.list_personas()


@router.get("/personas/{persona_id}", response_model=UserPersona)
def get_persona(persona_id: str):
    """Get a specific user persona"""
    persona = simulator.get_persona(persona_id)
    if not persona:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Persona not found")
    return persona
