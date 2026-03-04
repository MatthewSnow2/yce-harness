"""Main FastAPI application"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .core.config import get_settings
from .core.database import init_db, get_db, engine
from .api import conversations, testing
from .models.conversation import ScenarioModel

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup: Initialize database
    init_db()

    # Create sample scenarios if database is empty
    from sqlalchemy.orm import Session
    db = Session(bind=engine)
    try:
        scenario_count = db.query(ScenarioModel).count()
        if scenario_count == 0:
            from datetime import datetime

            # Create sample scenarios
            sample_scenarios = [
                ScenarioModel(
                    scenario_id="scenario-sample-001",
                    name="Customer Support Escalation",
                    description="Test scenario where a frustrated customer needs escalation to management",
                    user_persona="frustrated_customer",
                    expected_turns=15,
                    success_criteria=[
                        "Agent correctly identifies escalation intent",
                        "Context maintained throughout conversation",
                        "Escalation occurs around turn 12",
                        "Context score above 85%"
                    ],
                    conversation_flow=[
                        {
                            "turn": "turn_1",
                            "user_input": "Hello, I've been having a terrible experience with your service",
                            "expected_intent": "express_frustration"
                        },
                        {
                            "turn": "turn_12",
                            "user_input": "This is unacceptable! I need to speak to a manager immediately!",
                            "expected_intent": "request_escalation"
                        }
                    ],
                    created_at=datetime.utcnow()
                ),
                ScenarioModel(
                    scenario_id="scenario-sample-002",
                    name="Technical Support Query",
                    description="Technical user asking detailed questions about API integration",
                    user_persona="technical_user",
                    expected_turns=20,
                    success_criteria=[
                        "Agent provides technical details",
                        "Context maintained across multiple technical questions",
                        "Average confidence score above 80%"
                    ],
                    conversation_flow=[],
                    created_at=datetime.utcnow()
                ),
                ScenarioModel(
                    scenario_id="scenario-sample-003",
                    name="New User Onboarding",
                    description="First-time user needs guidance on getting started",
                    user_persona="new_user",
                    expected_turns=10,
                    success_criteria=[
                        "Agent provides step-by-step guidance",
                        "User feels supported and welcomed",
                        "No confusion or repeated questions"
                    ],
                    conversation_flow=[],
                    created_at=datetime.utcnow()
                )
            ]

            for scenario in sample_scenarios:
                db.add(scenario)

            db.commit()
            print(f"Created {len(sample_scenarios)} sample scenarios")
    finally:
        db.close()

    yield

    # Shutdown
    pass


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(conversations.router)
app.include_router(testing.router)


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
