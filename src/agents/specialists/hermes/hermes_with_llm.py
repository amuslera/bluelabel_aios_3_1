#!/usr/bin/env python3
"""
Hermes Agent with full LLM integration.
Connects to the LLMRouter for intelligent, context-aware conversations.
"""

import os
import asyncio
import logging
from typing import Optional, Dict, Any, List

from src.agents.specialists.hermes.hermes_agent_simple import (
    SimpleHermesAgent,
    PersonaConfig,
    ConversationState,
    IntentBucket
)
from src.core.routing.router import LLMRouter, RoutingContext, RoutingPolicy, RoutingStrategy
from src.core.routing.providers.base import LLMRequest, ModelCapability
from src.core.routing.providers.claude import ClaudeProvider
from src.core.routing.providers.openai import OpenAIProvider
from src.core.routing.providers.local import LocalProvider

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HermesWithLLM(SimpleHermesAgent):
    """Enhanced Hermes with real LLM capabilities."""
    
    def __init__(
        self,
        persona_config: Optional[PersonaConfig] = None,
        llm_router: Optional[LLMRouter] = None
    ):
        """Initialize Hermes with LLM support."""
        super().__init__(persona_config=persona_config)
        self.llm_router = llm_router
        self._complexity_threshold = 5  # Threshold for using cloud LLMs
    
    async def initialize_llm_router(self):
        """Initialize the LLM router with providers."""
        if self.llm_router:
            return  # Already initialized
        
        # Create providers
        providers = {}
        
        # Local provider (Ollama) - Primary
        try:
            from src.core.routing.providers.local import LocalConfig
            local_config = LocalConfig(
                provider_name="ollama",
                base_url="http://localhost:11434"
            )
            local_provider = LocalProvider(config=local_config)
            providers["ollama"] = local_provider
            logger.info("✓ Ollama provider configured")
        except Exception as e:
            logger.warning(f"Failed to configure Ollama: {e}")
        
        # OpenAI provider - Secondary
        if os.getenv("OPENAI_API_KEY"):
            try:
                from src.core.routing.providers.openai import OpenAIConfig
                openai_config = OpenAIConfig(
                    provider_name="openai",
                    api_key=os.getenv("OPENAI_API_KEY")
                )
                openai_provider = OpenAIProvider(config=openai_config)
                providers["openai"] = openai_provider
                logger.info("✓ OpenAI provider configured")
            except Exception as e:
                logger.warning(f"Failed to configure OpenAI: {e}")
        
        # Claude provider - For complex tasks
        if os.getenv("ANTHROPIC_API_KEY"):
            try:
                from src.core.routing.providers.claude import ClaudeConfig
                claude_config = ClaudeConfig(
                    provider_name="claude",
                    api_key=os.getenv("ANTHROPIC_API_KEY")
                )
                claude_provider = ClaudeProvider(config=claude_config)
                providers["claude"] = claude_provider
                logger.info("✓ Claude provider configured")
            except Exception as e:
                logger.warning(f"Failed to configure Claude: {e}")
        
        # Create router with cost-optimized policy
        self.llm_router = LLMRouter(
            default_policy=RoutingPolicy(
                strategy=RoutingStrategy.COST_OPTIMIZED,
                max_cost_per_request=0.01,  # 1 cent max
                enable_caching=True,
                cache_ttl_minutes=30
            )
        )
        
        # Register providers
        for name, provider in providers.items():
            self.llm_router.register_provider(name, provider)
        
        await self.llm_router.initialize()
        logger.info(f"LLM Router initialized with {len(providers)} providers")
    
    def _assess_complexity(self, user_input: str, state: ConversationState) -> int:
        """Assess the complexity of a user request (1-10 scale)."""
        complexity = 3  # Base complexity
        
        # Increase for longer inputs
        word_count = len(user_input.split())
        if word_count > 50:
            complexity += 2
        elif word_count > 20:
            complexity += 1
        
        # Increase for questions
        if "?" in user_input:
            complexity += 1
        
        # Increase for technical terms
        tech_terms = ["api", "database", "authentication", "deployment", "architecture"]
        if any(term in user_input.lower() for term in tech_terms):
            complexity += 2
        
        # Decrease for simple greetings
        greetings = ["hello", "hi", "hey", "thanks", "thank you", "bye"]
        if any(greeting in user_input.lower() for greeting in greetings):
            complexity = max(1, complexity - 2)
        
        # Increase if we need to extract requirements
        if state.intent_state.current_bucket == IntentBucket.BUILD and state.turn_count > 2:
            complexity += 1
        
        return min(10, complexity)
    
    async def _generate_llm_response(
        self,
        user_input: str,
        state: ConversationState
    ) -> str:
        """Generate response using LLM router."""
        if not self.llm_router:
            await self.initialize_llm_router()
        
        # Assess complexity
        complexity = self._assess_complexity(user_input, state)
        
        # Build conversation messages
        messages = [
            {"role": "system", "content": self._get_enhanced_system_prompt(state)}
        ]
        
        # Add conversation history (last 6 messages for context)
        for msg in state.messages[-6:]:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Add user's current message
        messages.append({"role": "user", "content": user_input})
        
        # Create LLM request
        request = LLMRequest(
            messages=messages,
            model_id="auto",  # Let router choose the best model
            temperature=0.7,
            max_tokens=500
        )
        
        # Create routing context
        context = RoutingContext(
            agent_id=self.name,
            complexity=complexity,
            privacy_sensitive=False  # Hermes doesn't handle sensitive data
        )
        
        # Adjust policy based on complexity
        policy = None
        if complexity <= 3:
            # Simple queries should use local
            policy = RoutingPolicy(
                strategy=RoutingStrategy.COST_OPTIMIZED,
                preferred_providers=["ollama"],
                max_cost_per_request=0.001
            )
        elif complexity >= 7:
            # Complex queries might need Claude
            policy = RoutingPolicy(
                strategy=RoutingStrategy.PERFORMANCE_OPTIMIZED,
                preferred_providers=["claude", "openai"],
                max_cost_per_request=0.05
            )
        
        try:
            # Route and execute request
            routing_decision = await self.llm_router.route_request(
                request=request,
                context=context,
                policy=policy
            )
            
            logger.info(
                f"Routed to {routing_decision.provider_name} "
                f"(complexity: {complexity}, cost: ${routing_decision.estimated_cost:.4f})"
            )
            
            # Update request with actual model ID
            request.model_id = routing_decision.model_id
            
            # Execute request
            provider = self.llm_router.providers[routing_decision.provider_name]
            response = await provider.generate(request)
            
            # Track metrics
            self._track_llm_usage(routing_decision, complexity)
            
            return response.content
            
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return self._get_fallback_response(state)
    
    def _get_enhanced_system_prompt(self, state: ConversationState) -> str:
        """Generate enhanced system prompt with context."""
        base_prompt = f"""You are Hermes, the friendly concierge for an AI software development platform.

Current conversation context:
- Intent: {state.intent_state.current_bucket.value}
- Confidence: {state.intent_state.confidence:.0%}
- Turn: {state.turn_count}
- Requirements gathered: {len(state.project_requirements)}

{self.persona.get_system_prompt_modifiers()}

Your responses should:
1. Be warm, helpful, and encouraging
2. Ask clarifying questions when needed
3. Use simple language for non-technical users
4. Guide users toward defining their project clearly
5. Track and acknowledge what you've learned about their needs

Remember: You're helping them communicate with our AI development team:
- Apollo (Backend): APIs, databases, system architecture
- Aphrodite (Frontend): UI/UX, web interfaces, design
- Athena (QA): Testing, quality assurance, security
- Hephaestus (DevOps): Deployment, CI/CD, infrastructure"""
        
        # Add specific context based on intent
        if state.intent_state.current_bucket == IntentBucket.BUILD:
            base_prompt += "\n\nFocus on understanding what they want to build and who will use it."
        elif state.intent_state.current_bucket == IntentBucket.AUTOMATE:
            base_prompt += "\n\nFocus on understanding their current workflow and pain points."
        
        return base_prompt
    
    async def process_conversation(
        self,
        user_input: str,
        session_id: Optional[str] = None
    ) -> tuple[str, ConversationState]:
        """Process conversation with LLM support."""
        # Get or create conversation state
        if session_id and session_id in self.conversations:
            state = self.conversations[session_id]
        else:
            state = ConversationState()
            self.conversations[state.session_id] = state
        
        # Add user message
        state.add_message("user", user_input)
        
        # Detect intent
        intent_bucket, specific_type, confidence = self._detect_intent(
            user_input, state
        )
        state.intent_state.update(
            turn=state.turn_count,
            bucket=intent_bucket,
            specific_type=specific_type,
            confidence=confidence,
            user_input=user_input
        )
        
        # Generate response with LLM
        response = await self._generate_llm_response(user_input, state)
        
        # Add assistant message
        state.add_message("assistant", response)
        
        # Extract any requirements (enhanced with context)
        if intent_bucket == IntentBucket.BUILD:
            self._extract_requirements(user_input, state)
            # Also extract from response context
            self._extract_from_conversation_context(state)
        
        # Check if ready for handoff
        state.ready_for_handoff = self._check_handoff_ready(state)
        
        self.logger.info(
            f"Turn {state.turn_count} - Intent: {intent_bucket.value} "
            f"({confidence:.0%}) - Type: {specific_type}"
        )
        
        return response, state
    
    def _extract_from_conversation_context(self, state: ConversationState):
        """Extract additional requirements from conversation context."""
        # This is a simplified version - could be enhanced with NLP
        recent_messages = " ".join([
            msg["content"] for msg in state.messages[-4:]
            if msg["role"] == "user"
        ]).lower()
        
        # Extract timeline mentions
        import re
        timeline_match = re.search(r'(\d+)\s*(week|month|day)', recent_messages)
        if timeline_match and "timeline" not in state.project_requirements:
            state.project_requirements["timeline"] = timeline_match.group(0)
        
        # Extract budget mentions
        budget_match = re.search(r'\$[\d,]+|\d+k|\d+\s*thousand', recent_messages)
        if budget_match and "budget" not in state.project_requirements:
            state.project_requirements["budget"] = budget_match.group(0)
    
    def _track_llm_usage(self, routing_decision, complexity: int):
        """Track LLM usage for metrics."""
        # This could be expanded to save to a database
        logger.info(
            f"LLM Usage - Provider: {routing_decision.provider_name}, "
            f"Model: {routing_decision.model_id}, "
            f"Cost: ${routing_decision.estimated_cost:.4f}, "
            f"Complexity: {complexity}"
        )


async def create_hermes_with_llm(persona_config: Optional[PersonaConfig] = None) -> HermesWithLLM:
    """Create and initialize Hermes with LLM support."""
    hermes = HermesWithLLM(persona_config=persona_config)
    await hermes.initialize_llm_router()
    return hermes