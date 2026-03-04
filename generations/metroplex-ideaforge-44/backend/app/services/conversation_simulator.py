"""Conversation simulation service"""

import random
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from ..models.conversation import ConversationTurn
from ..models.testing import UserPersona, IntentRecognition


# User persona templates
USER_PERSONAS = {
    "frustrated_customer": UserPersona(
        persona_id="frustrated_customer",
        name="Frustrated Customer",
        description="A customer who is upset about a service issue and seeking resolution",
        traits=["impatient", "demanding", "emotional", "detail-oriented"],
        communication_style="Direct, emotional, uses exclamation marks, may escalate quickly",
        example_phrases=[
            "This is unacceptable!",
            "I've been waiting for hours!",
            "I need to speak to a manager",
            "This is the third time I'm calling about this"
        ]
    ),
    "technical_user": UserPersona(
        persona_id="technical_user",
        name="Technical User",
        description="A technically savvy user who understands the product details",
        traits=["analytical", "precise", "knowledgeable", "solution-oriented"],
        communication_style="Uses technical terminology, asks specific questions, seeks detailed information",
        example_phrases=[
            "What's the API rate limit?",
            "Can you explain the authentication flow?",
            "I'm getting a 403 error when I try to access the endpoint",
            "Is this compatible with WebSocket protocol?"
        ]
    ),
    "casual_user": UserPersona(
        persona_id="casual_user",
        name="Casual User",
        description="A friendly, easy-going user with basic needs",
        traits=["friendly", "patient", "appreciative", "straightforward"],
        communication_style="Polite, conversational, uses simple language",
        example_phrases=[
            "Hi there! I need some help",
            "Thanks so much for your help!",
            "That makes sense, thanks",
            "Could you explain that in simpler terms?"
        ]
    ),
    "confused_customer": UserPersona(
        persona_id="confused_customer",
        name="Confused Customer",
        description="A customer who is uncertain and needs guidance",
        traits=["uncertain", "seeking clarification", "hesitant", "needs reassurance"],
        communication_style="Asks many questions, seeks confirmation, may repeat questions",
        example_phrases=[
            "I'm not sure I understand",
            "Wait, can you explain that again?",
            "So does that mean...?",
            "I'm confused about how this works"
        ]
    ),
    "business_professional": UserPersona(
        persona_id="business_professional",
        name="Business Professional",
        description="A professional user focused on ROI and business value",
        traits=["results-oriented", "time-conscious", "strategic", "professional"],
        communication_style="Formal, concise, focuses on outcomes and metrics",
        example_phrases=[
            "What's the ROI on this feature?",
            "How does this integrate with our existing systems?",
            "I need this resolved quickly for our Q4 goals",
            "Can you provide metrics on performance improvements?"
        ]
    ),
    "elderly_user": UserPersona(
        persona_id="elderly_user",
        name="Elderly User",
        description="An older user who may need extra patience and clarity",
        traits=["patient", "cautious", "needs step-by-step guidance", "appreciative"],
        communication_style="Slower paced, needs clear instructions, may ask for repetition",
        example_phrases=[
            "I'm not very good with technology",
            "Can you walk me through this step by step?",
            "I want to make sure I do this correctly",
            "You're being very helpful, thank you"
        ]
    ),
    "power_user": UserPersona(
        persona_id="power_user",
        name="Power User",
        description="An advanced user who knows the product well and has high expectations",
        traits=["experienced", "demanding", "efficiency-focused", "feature-aware"],
        communication_style="Fast-paced, expects quick solutions, references advanced features",
        example_phrases=[
            "Is there a keyboard shortcut for this?",
            "I already tried the usual troubleshooting steps",
            "Can I customize this workflow?",
            "I need access to the advanced settings"
        ]
    ),
    "new_user": UserPersona(
        persona_id="new_user",
        name="New User",
        description="A first-time user exploring the product",
        traits=["curious", "exploratory", "needs onboarding", "open to learning"],
        communication_style="Asks basic questions, needs guidance on getting started",
        example_phrases=[
            "I'm new to this, where do I start?",
            "How do I create an account?",
            "What can I do with this product?",
            "Is there a tutorial I can follow?"
        ]
    ),
    "price_sensitive": UserPersona(
        persona_id="price_sensitive",
        name="Price Sensitive Customer",
        description="A customer focused on cost and value",
        traits=["budget-conscious", "comparison-shopping", "negotiating", "value-seeking"],
        communication_style="Asks about pricing, discounts, and alternatives",
        example_phrases=[
            "Is there a cheaper option?",
            "Do you have any discounts available?",
            "What's included in the basic plan?",
            "How does your pricing compare to competitors?"
        ]
    ),
    "urgent_requester": UserPersona(
        persona_id="urgent_requester",
        name="Urgent Requester",
        description="A user with time-sensitive needs",
        traits=["time-pressured", "stressed", "focused", "needs immediate help"],
        communication_style="Emphasizes urgency, needs quick resolution",
        example_phrases=[
            "This is urgent, I need help now",
            "I have a deadline in an hour",
            "Can you expedite this?",
            "Time is critical here"
        ]
    ),
    "skeptical_user": UserPersona(
        persona_id="skeptical_user",
        name="Skeptical User",
        description="A user who needs convincing and proof",
        traits=["questioning", "trust-seeking", "requires evidence", "cautious"],
        communication_style="Asks for proof, references, and guarantees",
        example_phrases=[
            "How do I know this will work?",
            "Do you have any customer testimonials?",
            "What's your success rate?",
            "Can you guarantee this solution?"
        ]
    )
}


# Simulated intents
INTENTS = [
    "greeting",
    "question_general",
    "question_technical",
    "request_help",
    "request_escalation",
    "express_frustration",
    "provide_information",
    "confirm_understanding",
    "express_satisfaction",
    "request_cancellation",
    "report_issue",
    "request_feature",
    "thank_you",
    "goodbye"
]


class ConversationSimulator:
    """Simulates multi-turn conversations with AI agents"""

    def __init__(self):
        self.personas = USER_PERSONAS

    def get_persona(self, persona_id: str) -> Optional[UserPersona]:
        """Get a user persona by ID"""
        return self.personas.get(persona_id)

    def list_personas(self) -> List[UserPersona]:
        """List all available personas"""
        return list(self.personas.values())

    def detect_intent(self, user_input: str, turn_number: int) -> IntentRecognition:
        """Simulate intent detection (mock implementation)"""
        # Simple keyword-based intent detection for simulation
        input_lower = user_input.lower()

        if turn_number == 1 or any(word in input_lower for word in ["hi", "hello", "hey"]):
            intent = "greeting"
            confidence = 0.95
        elif any(word in input_lower for word in ["manager", "escalate", "supervisor"]):
            intent = "request_escalation"
            confidence = 0.92
        elif any(word in input_lower for word in ["frustrated", "upset", "unacceptable", "terrible"]):
            intent = "express_frustration"
            confidence = 0.88
        elif any(word in input_lower for word in ["thank", "thanks", "appreciate"]):
            intent = "thank_you"
            confidence = 0.94
        elif any(word in input_lower for word in ["help", "assist", "support"]):
            intent = "request_help"
            confidence = 0.90
        elif any(word in input_lower for word in ["how", "what", "when", "where", "why", "?"]):
            intent = "question_general"
            confidence = 0.85
        elif any(word in input_lower for word in ["cancel", "refund", "return"]):
            intent = "request_cancellation"
            confidence = 0.89
        elif any(word in input_lower for word in ["bye", "goodbye", "see you"]):
            intent = "goodbye"
            confidence = 0.93
        else:
            intent = random.choice(INTENTS)
            confidence = random.uniform(0.70, 0.85)

        return IntentRecognition(
            intent=intent,
            confidence=confidence,
            entities={}
        )

    def generate_agent_response(
        self,
        user_input: str,
        intent: str,
        turn_number: int,
        conversation_context: List[str]
    ) -> str:
        """Generate a simulated agent response based on intent and context"""

        # Simulate context-aware responses
        if intent == "greeting":
            responses = [
                "Hello! How can I assist you today?",
                "Hi there! Welcome to our support. What can I help you with?",
                "Good day! I'm here to help. What brings you here today?"
            ]
        elif intent == "request_escalation":
            responses = [
                "I understand you'd like to speak with a manager. Let me connect you with a supervisor right away.",
                "I'll escalate this to our senior support team immediately. Please hold for a moment.",
                "I can see this needs management attention. I'm transferring you to a supervisor now."
            ]
        elif intent == "express_frustration":
            responses = [
                "I sincerely apologize for the inconvenience. I understand your frustration and I'm here to make this right.",
                "I'm very sorry you're experiencing this issue. Let me do everything I can to resolve this for you.",
                "I completely understand your frustration. This is not the experience we want you to have. Let's fix this together."
            ]
        elif intent == "request_help":
            responses = [
                "I'd be happy to help you with that. Can you provide more details about what you need assistance with?",
                "Of course! I'm here to help. Could you tell me more about the specific issue?",
                "Absolutely, I can assist with that. What specifically would you like help with?"
            ]
        elif intent == "question_general":
            responses = [
                "That's a great question! Based on your inquiry, here's what I can tell you...",
                "Let me explain that for you. The answer depends on a few factors...",
                "I can help clarify that. Here's the information you're looking for..."
            ]
        elif intent == "thank_you":
            responses = [
                "You're very welcome! Is there anything else I can help you with today?",
                "Happy to help! Feel free to reach out if you need anything else.",
                "My pleasure! Don't hesitate to contact us again if you have more questions."
            ]
        elif intent == "goodbye":
            responses = [
                "Thank you for contacting us! Have a great day!",
                "Goodbye! Feel free to reach out anytime you need assistance.",
                "Take care! We're always here if you need help in the future."
            ]
        elif intent == "request_cancellation":
            responses = [
                "I understand you'd like to cancel. Let me help you with that process. Can I ask what prompted this decision?",
                "I'd be happy to assist with your cancellation. Before we proceed, is there anything we can do to address your concerns?",
                "I can process that cancellation for you. May I ask if there's a specific reason you're canceling?"
            ]
        else:
            responses = [
                f"I understand what you're saying. Let me address that for you based on our conversation.",
                f"Thank you for that information. Here's what I can do to help with your situation.",
                f"I've noted your concern. Based on what we've discussed, here's my recommendation."
            ]

        # Add context awareness for later turns
        if turn_number > 5 and len(conversation_context) > 0:
            context_phrases = [
                "As we discussed earlier, ",
                "Following up on your previous question, ",
                "Building on what you mentioned, "
            ]
            response = random.choice(context_phrases) + random.choice(responses)
        else:
            response = random.choice(responses)

        return response

    def generate_user_input(
        self,
        persona: UserPersona,
        turn_number: int,
        conversation_context: List[str],
        scenario_flow: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate user input based on persona and conversation context"""

        # If scenario flow is provided, use it
        if scenario_flow and f"turn_{turn_number}" in scenario_flow:
            return scenario_flow[f"turn_{turn_number}"].get("user_input", "")

        # Otherwise, generate based on persona and context
        if turn_number == 1:
            # Start with a greeting and problem statement
            return f"Hello, I need help with an issue I'm experiencing."

        # Generate contextual follow-up based on persona
        phrases = persona.example_phrases
        base_phrase = random.choice(phrases)

        # Add some variation
        if turn_number % 3 == 0:
            # Ask for clarification
            return f"{base_phrase} Can you explain more about how this works?"
        elif turn_number % 4 == 0:
            # Express emotion based on persona traits
            if "frustrated" in persona.traits:
                return f"I'm still not satisfied with this solution. {base_phrase}"
            elif "appreciative" in persona.traits:
                return f"Thank you for your help! {base_phrase}"
            else:
                return base_phrase
        else:
            return base_phrase

    def calculate_context_score(
        self,
        turns: List[ConversationTurn],
        expected_context_keywords: Optional[List[str]] = None
    ) -> float:
        """Calculate context retention score for a conversation"""

        if len(turns) < 2:
            return 100.0

        context_maintained_count = sum(1 for turn in turns if turn.context_maintained)
        total_turns = len(turns)

        # Base score on context maintained flags
        base_score = (context_maintained_count / total_turns) * 100

        # Adjust based on confidence scores
        avg_confidence = sum(turn.confidence_score for turn in turns) / len(turns)
        confidence_bonus = (avg_confidence - 0.75) * 20  # Scale confidence impact

        final_score = min(100.0, max(0.0, base_score + confidence_bonus))
        return round(final_score, 2)

    def simulate_conversation(
        self,
        scenario_name: str,
        persona_id: str,
        num_turns: int,
        scenario_flow: Optional[List[Dict[str, Any]]] = None
    ) -> List[ConversationTurn]:
        """Simulate a complete multi-turn conversation"""

        persona = self.get_persona(persona_id)
        if not persona:
            raise ValueError(f"Unknown persona: {persona_id}")

        turns = []
        conversation_context = []

        for turn_num in range(1, num_turns + 1):
            # Generate user input
            flow_dict = None
            if scenario_flow:
                flow_dict = {item["turn"]: item for item in scenario_flow if isinstance(item, dict) and "turn" in item}

            user_input = self.generate_user_input(
                persona, turn_num, conversation_context, flow_dict
            )

            # Detect intent
            intent_result = self.detect_intent(user_input, turn_num)

            # Generate agent response
            agent_response = self.generate_agent_response(
                user_input,
                intent_result.intent,
                turn_num,
                conversation_context
            )

            # Simulate response time (faster for simpler intents)
            if intent_result.confidence > 0.9:
                response_time = random.randint(800, 1500)
            else:
                response_time = random.randint(1500, 3000)

            # Context maintained if confidence is high and turn is not too early
            context_maintained = intent_result.confidence > 0.80 and turn_num > 2

            # Create turn
            turn = ConversationTurn(
                turn_id=turn_num,
                user_input=user_input,
                agent_response=agent_response,
                intent_detected=intent_result.intent,
                confidence_score=intent_result.confidence,
                response_time_ms=response_time,
                timestamp=datetime.utcnow(),
                context_maintained=context_maintained
            )

            turns.append(turn)
            conversation_context.append(user_input)
            conversation_context.append(agent_response)

            # Check for escalation scenario
            if "escalation" in scenario_name.lower() and turn_num == 12:
                # Force escalation intent at turn 12
                turn.intent_detected = "request_escalation"
                turn.agent_response = "I understand you'd like to speak with a manager. Let me connect you with a supervisor right away."

        return turns
