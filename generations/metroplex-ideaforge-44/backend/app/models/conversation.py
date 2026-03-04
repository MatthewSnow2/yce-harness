"""Conversation data models"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from ..core.database import Base


# SQLAlchemy ORM Models
class ScenarioModel(Base):
    """Database model for test scenarios"""
    __tablename__ = "scenarios"

    id = Column(Integer, primary_key=True, index=True)
    scenario_id = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    user_persona = Column(String)
    expected_turns = Column(Integer)
    success_criteria = Column(JSON)
    conversation_flow = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    conversations = relationship("ConversationModel", back_populates="scenario")


class ConversationModel(Base):
    """Database model for conversation executions"""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String, unique=True, index=True)
    scenario_id = Column(String, ForeignKey("scenarios.scenario_id"))
    status = Column(String)  # "running", "completed", "failed"
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    overall_score = Column(Float, nullable=True)
    context_score = Column(Float, nullable=True)
    success = Column(Boolean, default=False)

    # Relationships
    scenario = relationship("ScenarioModel", back_populates="conversations")
    turns = relationship("TurnModel", back_populates="conversation")


class TurnModel(Base):
    """Database model for conversation turns"""
    __tablename__ = "turns"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String, ForeignKey("conversations.conversation_id"))
    turn_id = Column(Integer)
    user_input = Column(Text)
    agent_response = Column(Text)
    intent_detected = Column(String, nullable=True)
    confidence_score = Column(Float)
    response_time_ms = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)
    context_maintained = Column(Boolean)

    # Relationships
    conversation = relationship("ConversationModel", back_populates="turns")


# Pydantic Models for API
class ConversationTurn(BaseModel):
    """Individual conversation turn"""
    turn_id: int
    user_input: str
    agent_response: str
    intent_detected: Optional[str] = None
    confidence_score: float
    response_time_ms: int
    timestamp: datetime
    context_maintained: bool

    class Config:
        from_attributes = True


class TestScenario(BaseModel):
    """Test scenario configuration"""
    scenario_id: str
    name: str
    description: str
    user_persona: str
    expected_turns: int
    success_criteria: List[str]
    conversation_flow: List[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True


class TestScenarioCreate(BaseModel):
    """Create test scenario request"""
    name: str
    description: str
    user_persona: str
    expected_turns: int = 15
    success_criteria: List[str] = Field(default_factory=list)
    conversation_flow: List[Dict[str, Any]] = Field(default_factory=list)


class ConversationExecution(BaseModel):
    """Conversation execution details"""
    conversation_id: str
    scenario_id: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    overall_score: Optional[float] = None
    context_score: Optional[float] = None
    success: bool = False
    turns: List[ConversationTurn] = Field(default_factory=list)

    class Config:
        from_attributes = True


class ConversationExecuteRequest(BaseModel):
    """Request to execute a conversation test"""
    scenario_id: str
    num_turns: Optional[int] = None
