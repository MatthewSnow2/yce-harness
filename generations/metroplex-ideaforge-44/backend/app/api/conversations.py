"""API endpoints for conversation testing"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid
from datetime import datetime

from ..core.database import get_db
from ..models.conversation import (
    TestScenario,
    TestScenarioCreate,
    ConversationExecution,
    ConversationExecuteRequest,
    ScenarioModel,
    ConversationModel,
    TurnModel
)
from ..services.conversation_simulator import ConversationSimulator

router = APIRouter(prefix="/api", tags=["conversations"])
simulator = ConversationSimulator()


@router.post("/scenarios", response_model=TestScenario)
def create_scenario(scenario: TestScenarioCreate, db: Session = Depends(get_db)):
    """Create a new test scenario"""

    scenario_id = f"scenario-{uuid.uuid4().hex[:8]}"

    db_scenario = ScenarioModel(
        scenario_id=scenario_id,
        name=scenario.name,
        description=scenario.description,
        user_persona=scenario.user_persona,
        expected_turns=scenario.expected_turns,
        success_criteria=scenario.success_criteria,
        conversation_flow=scenario.conversation_flow,
        created_at=datetime.utcnow()
    )

    db.add(db_scenario)
    db.commit()
    db.refresh(db_scenario)

    return TestScenario.model_validate(db_scenario)


@router.get("/scenarios", response_model=List[TestScenario])
def list_scenarios(db: Session = Depends(get_db)):
    """List all test scenarios"""
    scenarios = db.query(ScenarioModel).order_by(ScenarioModel.created_at.desc()).all()
    return [TestScenario.model_validate(s) for s in scenarios]


@router.get("/scenarios/{scenario_id}", response_model=TestScenario)
def get_scenario(scenario_id: str, db: Session = Depends(get_db)):
    """Get a specific test scenario"""
    scenario = db.query(ScenarioModel).filter(
        ScenarioModel.scenario_id == scenario_id
    ).first()

    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    return TestScenario.model_validate(scenario)


@router.post("/scenarios/{scenario_id}/execute", response_model=ConversationExecution)
def execute_scenario(
    scenario_id: str,
    request: ConversationExecuteRequest,
    db: Session = Depends(get_db)
):
    """Execute a conversation test for a scenario"""

    # Get the scenario
    scenario = db.query(ScenarioModel).filter(
        ScenarioModel.scenario_id == scenario_id
    ).first()

    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    # Determine number of turns
    num_turns = request.num_turns if request.num_turns else scenario.expected_turns

    # Create conversation record
    conversation_id = f"conv-{uuid.uuid4().hex[:8]}"
    db_conversation = ConversationModel(
        conversation_id=conversation_id,
        scenario_id=scenario_id,
        status="running",
        started_at=datetime.utcnow()
    )

    db.add(db_conversation)
    db.commit()

    try:
        # Simulate the conversation
        turns = simulator.simulate_conversation(
            scenario_name=scenario.name,
            persona_id=scenario.user_persona,
            num_turns=num_turns,
            scenario_flow=scenario.conversation_flow
        )

        # Save turns to database
        for turn in turns:
            db_turn = TurnModel(
                conversation_id=conversation_id,
                turn_id=turn.turn_id,
                user_input=turn.user_input,
                agent_response=turn.agent_response,
                intent_detected=turn.intent_detected,
                confidence_score=turn.confidence_score,
                response_time_ms=turn.response_time_ms,
                timestamp=turn.timestamp,
                context_maintained=turn.context_maintained
            )
            db.add(db_turn)

        # Calculate scores
        context_score = simulator.calculate_context_score(turns)
        avg_confidence = sum(t.confidence_score for t in turns) / len(turns)
        overall_score = (context_score + (avg_confidence * 100)) / 2

        # Check success criteria
        success = context_score >= 85.0 and avg_confidence >= 0.80

        # Update conversation with results
        db_conversation.status = "completed"
        db_conversation.completed_at = datetime.utcnow()
        db_conversation.overall_score = round(overall_score, 2)
        db_conversation.context_score = context_score
        db_conversation.success = success

        db.commit()
        db.refresh(db_conversation)

        # Return execution result
        return ConversationExecution(
            conversation_id=conversation_id,
            scenario_id=scenario_id,
            status="completed",
            started_at=db_conversation.started_at,
            completed_at=db_conversation.completed_at,
            overall_score=overall_score,
            context_score=context_score,
            success=success,
            turns=turns
        )

    except Exception as e:
        # Mark conversation as failed
        db_conversation.status = "failed"
        db_conversation.completed_at = datetime.utcnow()
        db.commit()
        raise HTTPException(status_code=500, detail=f"Conversation simulation failed: {str(e)}")


@router.get("/conversations/{conversation_id}", response_model=ConversationExecution)
def get_conversation(conversation_id: str, db: Session = Depends(get_db)):
    """Get conversation results with all turns"""

    conversation = db.query(ConversationModel).filter(
        ConversationModel.conversation_id == conversation_id
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Get all turns
    turns_data = db.query(TurnModel).filter(
        TurnModel.conversation_id == conversation_id
    ).order_by(TurnModel.turn_id).all()

    from ..models.conversation import ConversationTurn
    turns = [ConversationTurn.model_validate(t) for t in turns_data]

    return ConversationExecution(
        conversation_id=conversation.conversation_id,
        scenario_id=conversation.scenario_id,
        status=conversation.status,
        started_at=conversation.started_at,
        completed_at=conversation.completed_at,
        overall_score=conversation.overall_score,
        context_score=conversation.context_score,
        success=conversation.success,
        turns=turns
    )


@router.get("/conversations", response_model=List[ConversationExecution])
def list_conversations(db: Session = Depends(get_db)):
    """List all conversation executions"""

    conversations = db.query(ConversationModel).order_by(
        ConversationModel.started_at.desc()
    ).limit(50).all()

    results = []
    for conv in conversations:
        turns_data = db.query(TurnModel).filter(
            TurnModel.conversation_id == conv.conversation_id
        ).order_by(TurnModel.turn_id).all()

        from ..models.conversation import ConversationTurn
        turns = [ConversationTurn.model_validate(t) for t in turns_data]

        results.append(ConversationExecution(
            conversation_id=conv.conversation_id,
            scenario_id=conv.scenario_id,
            status=conv.status,
            started_at=conv.started_at,
            completed_at=conv.completed_at,
            overall_score=conv.overall_score,
            context_score=conv.context_score,
            success=conv.success,
            turns=turns
        ))

    return results
