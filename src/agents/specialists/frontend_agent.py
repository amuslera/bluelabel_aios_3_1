"""
Emily Rodriguez - Frontend Development Agent for AIOSv3.

Specializes in React/Vue development, UI/UX design, and accessibility.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from ..base.monitoring_agent import MonitoringAgent
from ..base.agent import AgentConfig
from ..base.types import Task, TaskType, TaskPriority
from ...core.routing.llm_integration import llm_integration
from ...core.messaging.queue import MessageQueue
from .frontend_personality import (
    EmilyDynamicPersonality, DesignMoodState, CreativeEnergyLevel,
    DesignPersonalityState, EmilyPersonalityTraits
)


class EmilyPersonality:
    """Emily Rodriguez's personality traits and communication style."""
    
    # Core personality traits
    TRAITS = {
        "creative": "Innovative UI solutions and aesthetic focus",
        "detail_oriented": "Pixel-perfect implementations and visual consistency",
        "user_focused": "Always considers user experience and usability",
        "collaborative": "Excellent at working with backend developers",
        "accessibility_minded": "Passionate advocate for inclusive design",
    }
    
    # Communication style
    COMMUNICATION_STYLE = {
        "greeting": "Hi everyone! Emily here ✨",
        "acknowledgment": "Absolutely! I'm on it",
        "thinking": "Let me visualize this...",
        "success": "🎨 Beautiful! Here's what I created:",
        "problem": "🤔 I notice a UX issue here:",
        "suggestion": "💡 What if we made this more user-friendly:",
        "collaboration": "I'd love to collaborate on this design!",
        "sign_off": "- Emily",
    }
    
    # Technical preferences
    TECHNICAL_PREFERENCES = {
        "framework": "React with TypeScript",
        "styling": "CSS-in-JS with Emotion or Styled Components",
        "testing": "Jest with React Testing Library",
        "accessibility": "WCAG 2.1 AA compliance",
        "design_system": "Component-driven development",
        "state_management": "Context API or Zustand for simple, Redux for complex",
    }
    
    @staticmethod
    def format_message(message_type: str, content: str) -> str:
        """Format a message with Emily's personality."""
        style = EmilyPersonality.COMMUNICATION_STYLE.get(message_type, "")
        if message_type == "greeting":
            return f"{style}\n{content}"
        elif message_type == "sign_off":
            return f"{content}\n\n{style}"
        else:
            return f"{style} {content}"


class FrontendAgent(MonitoringAgent):
    """
    Emily Rodriguez - The Frontend Development Specialist.
    
    Expertise:
    - React/Vue component development
    - UI/UX design implementation
    - CSS-in-JS styling systems
    - Accessibility compliance (WCAG)
    - Responsive design patterns
    """
    
    def __init__(
        self,
        agent_id: str = "emily_rodriguez",
        name: str = "Emily Rodriguez",
        config: Optional[AgentConfig] = None,
        **kwargs
    ):
        # Initialize with frontend-specific configuration
        if not config:
            config = AgentConfig()
        
        config.name = name
        config.agent_type = "frontend_developer"
        config.capabilities = [
            "ui_design",
            "component_development",
            "responsive_design",
            "accessibility_implementation",
            "css_styling",
            "user_experience",
            "frontend_testing",
        ]
        
        super().__init__(agent_id=agent_id, config=config, **kwargs)
        
        # Initialize both static and dynamic personality
        self.personality = EmilyPersonality()  # Keep for compatibility
        
        # Initialize dynamic personality
        emily_traits = {
            "creative": 0.9,
            "detail_oriented": 0.85,
            "user_focused": 0.9,
            "collaborative": 0.8,
            "accessibility_minded": 0.85,
        }
        self.dynamic_personality = EmilyDynamicPersonality(emily_traits, "Emily Rodriguez")
        
        self.logger = logging.getLogger(f"frontend_agent.{agent_id}")
        
        # Track Emily's state
        self.current_design_system = None
        self.design_tokens = {}  # Store design system tokens
        self.component_library = {}  # Track generated components
        self.accessibility_checks = []  # Track A11y validations
        
        # Initialize message queue for collaboration
        self.message_queue = MessageQueue(agent_id=agent_id)
        self.collaboration_partners = {}  # Track active collaborations
        
    async def on_start(self) -> None:
        """Initialize Emily with a creative greeting."""
        await super().on_start()
        
        # Use dynamic personality for greeting
        greeting = self.dynamic_personality.get_greeting()
        self.logger.info(greeting)
        
        # Start message queue listener
        await self.message_queue.start()
        self.logger.info("💬 Message queue ready for design collaboration")
        
        # Subscribe to relevant topics
        await self._subscribe_to_topics()
        
        # Report startup milestone
        await self.report_milestone(
            "Agent Initialized",
            {
                "personality": "Emily Rodriguez",
                "expertise": "Frontend Development",
                "preferred_stack": self.personality.TECHNICAL_PREFERENCES,
                "message_queue": "active",
            }
        )
    
    async def _subscribe_to_topics(self) -> None:
        """Subscribe to relevant message queue topics."""
        topics = [
            f"agent.{self.id}.inbox",  # Direct messages
            "frontend.components",  # Component generation requests
            "design.review",  # Design feedback and iteration
            "api.integration",  # Frontend-backend integration
            "accessibility.check",  # A11y compliance validation
            "team.broadcast",  # Team-wide messages
        ]
        
        for topic in topics:
            await self.message_queue.subscribe(topic, self._handle_queue_message)
            self.logger.info(f"🎨 Subscribed to topic: {topic}")
    
    async def execute_task(self, task: Task) -> Any:
        """Execute a frontend development task with Emily's expertise."""
        self.logger.info(
            self.personality.format_message(
                "acknowledgment",
                f"Working on: {task.description}"
            )
        )
        
        # Report task start with Emily's perspective
        await self._report_activity(
            "task_analysis",
            "info",
            f"Emily analyzing design task: {task.description}",
            {"task_type": task.type.value, "complexity": self._assess_complexity(task)}
        )
        
        # Route to appropriate handler based on task type
        if task.type == TaskType.CODE_GENERATION:
            result = await self._handle_component_generation(task)
        elif task.type == TaskType.SYSTEM_DESIGN:
            result = await self._handle_ui_design(task)
        elif task.type == TaskType.CODE_REVIEW:
            result = await self._handle_code_review(task)
        elif task.type == TaskType.TESTING:
            result = await self._handle_frontend_testing(task)
        elif task.type == TaskType.DOCUMENTATION:
            result = await self._handle_documentation(task)
        else:
            # Generic frontend task handling
            result = await self._handle_generic_task(task)
        
        # Add Emily's sign-off
        result = self.personality.format_message("sign_off", str(result))
        
        return result
    
    async def _handle_component_generation(self, task: Task) -> str:
        """Handle component generation tasks with Emily's design expertise."""
        self.logger.info("🎨 Creating beautiful, accessible components...")
        
        # Update personality state
        self.dynamic_personality.update_mood("design_complete" if self._assess_complexity(task) > 7 else "detail_work")
        
        # Check if this is a React/Vue component request
        description_lower = task.description.lower()
        
        if any(term in description_lower for term in ["react", "component", "vue", "ui"]):
            return await self._generate_react_component(task)
        elif any(term in description_lower for term in ["dashboard", "page", "layout"]):
            return await self._generate_layout(task)
        else:
            # Use LLM for generic component generation
            return await self._generate_custom_component(task)
    
    async def _generate_react_component(self, task: Task) -> str:
        """Generate React components with Emily's best practices."""
        # Add personality context
        thinking = self.dynamic_personality.get_thinking_phrase()
        self.logger.info(thinking)
        
        # Analyze component requirements
        description = task.description
        component_type = self._analyze_component_type(description)
        
        # Build context-aware prompt
        prompt = self._build_react_prompt(description, component_type)
        
        # Generate component with appropriate complexity
        complexity = self._assess_component_complexity(description, component_type)
        
        response = await llm_integration.generate(
            prompt=prompt,
            agent_id=self.id,
            task_type=TaskType.CODE_GENERATION,
            complexity=complexity,
            max_tokens=3000,
            temperature=0.8,  # Creative for component design
        )
        
        # Apply Emily's personality to the code
        result = self.dynamic_personality.apply_personality_to_code(response.content)
        
        # Store generated component
        component_name = self._extract_component_name(response.content, description)
        self.component_library[component_name] = {
            "code": result,
            "type": component_type,
            "created_at": datetime.utcnow().isoformat(),
            "description": description,
            "complexity": complexity,
            "personality_mood": self.dynamic_personality.state.mood.value,
        }
        
        # Remember this successful generation
        self.dynamic_personality.remember_design_decision(
            decision=f"Generated {component_type} component: {component_name}",
            outcome="success",
            user_impact="positive"
        )
        
        # Update creative energy from successful creation
        self.dynamic_personality.update_mood("design_complete", success=True)
        
        return self.personality.format_message("success", result)
    
    def _analyze_component_type(self, description: str) -> str:
        """Analyze the description to determine component type."""
        description_lower = description.lower()
        
        # Component type mapping
        if any(word in description_lower for word in ["button", "btn", "click", "action"]):
            return "button"
        elif any(word in description_lower for word in ["input", "form", "field", "text"]):
            return "input"
        elif any(word in description_lower for word in ["card", "item", "product", "user"]):
            return "card"
        elif any(word in description_lower for word in ["modal", "dialog", "popup"]):
            return "modal"
        elif any(word in description_lower for word in ["nav", "navigation", "menu"]):
            return "navigation"
        elif any(word in description_lower for word in ["table", "list", "data", "grid"]):
            return "data_display"
        elif any(word in description_lower for word in ["chart", "graph", "visualization"]):
            return "chart"
        elif any(word in description_lower for word in ["header", "footer", "sidebar"]):
            return "layout"
        elif any(word in description_lower for word in ["dashboard", "page", "view"]):
            return "page"
        else:
            return "generic"
    
    def _build_react_prompt(self, description: str, component_type: str) -> str:
        """Build a context-aware prompt for React component generation."""
        
        # Base prompt with Emily's personality
        base_prompt = f"""As Emily Rodriguez, a creative frontend developer who prioritizes user experience and accessibility, create a React component for: {description}
        
        Emily's Requirements:
        1. TypeScript for type safety
        2. Functional components with hooks
        3. Accessibility-first design (ARIA labels, keyboard navigation)
        4. Clean, semantic HTML structure
        5. Responsive design principles
        6. Modern React patterns (hooks, context when appropriate)
        7. Clear prop interfaces with JSDoc
        
        """
        
        # Type-specific guidelines
        type_guidelines = {
            "button": """
        Button Component Guidelines:
        - Use proper button semantics
        - Include loading and disabled states
        - Support different variants (primary, secondary, danger)
        - Ensure keyboard accessibility
        - Include proper ARIA attributes
        """,
            "input": """
        Input Component Guidelines:
        - Include proper label associations
        - Validate input and show errors gracefully
        - Support different input types
        - Include helper text and placeholder support
        - Ensure screen reader compatibility
        """,
            "card": """
        Card Component Guidelines:
        - Use semantic HTML structure
        - Support hover and focus states
        - Include proper heading hierarchy
        - Make clickable areas keyboard accessible
        - Consider loading states
        """,
            "modal": """
        Modal Component Guidelines:
        - Implement focus trapping
        - Support ESC key to close
        - Use portal for rendering
        - Include backdrop click handling
        - Ensure ARIA modal attributes
        """,
            "navigation": """
        Navigation Component Guidelines:
        - Use nav semantic element
        - Support keyboard navigation
        - Include skip links for accessibility
        - Highlight current page/section
        - Support mobile responsive patterns
        """,
            "data_display": """
        Data Display Guidelines:
        - Use appropriate table semantics
        - Support sorting and filtering
        - Include loading and empty states
        - Ensure screen reader table support
        - Consider virtualization for large datasets
        """,
            "chart": """
        Chart Component Guidelines:
        - Include accessible data alternatives
        - Use ARIA labels for data points
        - Support keyboard navigation
        - Provide color-blind friendly palettes
        - Include data table fallback
        """,
            "layout": """
        Layout Component Guidelines:
        - Use semantic HTML5 elements
        - Support responsive breakpoints
        - Include proper landmark roles
        - Ensure logical tab order
        - Support print-friendly styles
        """,
            "page": """
        Page Component Guidelines:
        - Include proper page structure
        - Support meta tags and SEO
        - Implement loading states
        - Include error boundaries
        - Ensure mobile-first responsive design
        """
        }
        
        # Add type-specific guidelines
        guidelines = type_guidelines.get(component_type, """
        General Component Guidelines:
        - Follow React best practices
        - Ensure accessibility compliance
        - Include proper error handling
        - Support responsive design
        - Use modern CSS practices
        """)
        
        # Add Emily's design preferences
        emily_preferences = f"""
        Emily's Design Preferences:
        - Clean, modern aesthetic
        - User-friendly interactions
        - Consistent spacing and typography
        - Subtle animations for better UX
        - Color scheme that supports accessibility
        - Mobile-first responsive approach
        
        Technical Preferences:
        - CSS-in-JS with styled-components or emotion
        - React Hook Form for form handling
        - React Query for data fetching (if needed)
        - Proper error boundaries
        - Performance optimizations (memo, useMemo, useCallback when needed)
        
        Generate a complete, production-ready component with:
        1. TypeScript interface for props
        2. Accessible JSX structure
        3. Appropriate styling approach
        4. Example usage
        5. Brief component documentation
        
        Make it beautiful, accessible, and user-friendly!
        """
        
        return base_prompt + guidelines + emily_preferences
    
    def _assess_component_complexity(self, description: str, component_type: str) -> int:
        """Assess component complexity based on requirements."""
        base_complexity = {
            "button": 3,
            "input": 4,
            "card": 4,
            "modal": 7,
            "navigation": 6,
            "data_display": 8,
            "chart": 9,
            "layout": 5,
            "page": 8,
            "generic": 5,
        }
        
        complexity = base_complexity.get(component_type, 5)
        
        # Adjust based on description keywords
        description_lower = description.lower()
        
        # Increase complexity for advanced features
        if any(word in description_lower for word in ["animation", "transition", "interactive"]):
            complexity += 1
        if any(word in description_lower for word in ["responsive", "mobile", "desktop"]):
            complexity += 1
        if any(word in description_lower for word in ["accessible", "a11y", "screen reader"]):
            complexity += 1
        if any(word in description_lower for word in ["form", "validation", "error"]):
            complexity += 1
        if any(word in description_lower for word in ["state", "context", "hook"]):
            complexity += 1
        if any(word in description_lower for word in ["api", "fetch", "data"]):
            complexity += 2
        
        # Decrease for simple components
        if any(word in description_lower for word in ["simple", "basic", "minimal"]):
            complexity -= 1
        
        return max(1, min(10, complexity))
    
    def _extract_component_name(self, code: str, description: str) -> str:
        """Extract component name from generated code or create from description."""
        # Try to find component name in code
        import re
        
        # Look for function/const component declarations
        patterns = [
            r"(?:export\s+)?(?:const|function)\s+([A-Z][a-zA-Z0-9]*)",
            r"export\s+default\s+function\s+([A-Z][a-zA-Z0-9]*)",
            r"const\s+([A-Z][a-zA-Z0-9]*)\s*[:=]",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, code)
            if match:
                return match.group(1)
        
        # Fallback: generate name from description
        words = description.split()
        component_name = "".join(word.capitalize() for word in words[:3] if word.isalpha())
        
        # Ensure it starts with capital and is valid
        if not component_name or not component_name[0].isupper():
            component_name = "CustomComponent"
        
        return component_name
    
    async def _generate_layout(self, task: Task) -> str:
        """Generate layout components like dashboards and pages."""
        # Add personality context
        thinking = self.dynamic_personality.get_thinking_phrase()
        self.logger.info(thinking)
        
        description = task.description
        layout_type = "dashboard" if "dashboard" in description.lower() else "page"
        
        prompt = f"""As Emily Rodriguez, create a {layout_type} layout for: {description}
        
        Requirements:
        1. Use semantic HTML5 structure
        2. Responsive grid layout
        3. Include proper navigation structure
        4. Accessibility-compliant landmark regions
        5. Mobile-first responsive design
        6. Loading states and error handling
        7. Clean component architecture
        
        Create a modern, user-friendly {layout_type} with proper TypeScript types."""
        
        complexity = 8 if layout_type == "dashboard" else 6
        
        response = await llm_integration.generate(
            prompt=prompt,
            agent_id=self.id,
            task_type=TaskType.CODE_GENERATION,
            complexity=complexity,
            max_tokens=3500,
            temperature=0.8,
        )
        
        # Apply personality and store
        result = self.dynamic_personality.apply_personality_to_code(response.content)
        
        component_name = self._extract_component_name(response.content, description)
        self.component_library[component_name] = {
            "code": result,
            "type": layout_type,
            "created_at": datetime.utcnow().isoformat(),
            "description": description,
            "complexity": complexity,
        }
        
        return self.personality.format_message("success", result)
    
    async def _generate_custom_component(self, task: Task) -> str:
        """Generate custom components using LLM intelligence."""
        # Add personality context
        thinking = self.dynamic_personality.get_thinking_phrase()
        self.logger.info(thinking)
        
        prompt = f"""As Emily Rodriguez, create a custom React component for: {task.description}
        
        Apply your expertise in:
        - User experience design
        - Accessibility best practices
        - Modern React patterns
        - TypeScript implementation
        - Responsive design
        - Clean code architecture
        
        Create something beautiful and functional!"""
        
        complexity = self._assess_complexity(task)
        
        response = await llm_integration.generate(
            prompt=prompt,
            agent_id=self.id,
            task_type=TaskType.CODE_GENERATION,
            complexity=complexity,
            max_tokens=3000,
            temperature=0.8,
        )
        
        # Apply personality
        result = self.dynamic_personality.apply_personality_to_code(response.content)
        
        # Store component
        component_name = self._extract_component_name(response.content, task.description)
        self.component_library[component_name] = {
            "code": result,
            "type": "custom",
            "created_at": datetime.utcnow().isoformat(),
            "description": task.description,
            "complexity": complexity,
        }
        
        return self.personality.format_message("success", result)
    
    async def _handle_ui_design(self, task: Task) -> str:
        """Handle UI/UX design tasks with user-centered approach."""
        self.logger.info("🎨 Designing user-centered interfaces...")
        
        # Update mood for design work
        self.dynamic_personality.update_mood("design_complete")
        
        # Add personality context
        thinking = self.dynamic_personality.get_thinking_phrase()
        self.logger.info(thinking)
        
        prompt = f"""As Emily Rodriguez, a frontend developer with strong UX focus, design a solution for: {task.description}
        
        Consider:
        - User experience and usability
        - Accessibility (WCAG 2.1 AA)
        - Responsive design patterns
        - Component reusability
        - Visual hierarchy and design principles
        - Performance optimization
        
        Provide a practical, user-friendly design."""
        
        response = await llm_integration.generate(
            prompt=prompt,
            agent_id=self.id,
            task_type=TaskType.SYSTEM_DESIGN,
            complexity=8,  # UI design is complex
            max_tokens=2500,
            temperature=0.8,  # More creative for design
        )
        
        # Apply personality to the response
        result = self.dynamic_personality.apply_personality_to_code(response.content)
        
        # Remember this design decision
        self.dynamic_personality.remember_design_decision(
            decision=f"UI design for: {task.description[:50]}",
            outcome="success",
            user_impact="positive"
        )
        
        return self.personality.format_message("success", result)
    
    async def _handle_code_review(self, task: Task) -> str:
        """Review code with Emily's focus on UX and accessibility."""
        self.logger.info("👀 Reviewing code for UX and accessibility...")
        
        # Update mood for review work
        self.dynamic_personality.update_mood("analytical")
        
        # Add personality context
        thinking = self.dynamic_personality.get_thinking_phrase()
        self.logger.info(thinking)
        
        prompt = f"""As Emily Rodriguez, review the following frontend code:
        
        {task.data.get('code', task.description)}
        
        Focus on:
        - React/Vue best practices
        - Accessibility compliance
        - User experience issues
        - Component structure and reusability
        - CSS and styling optimization
        - Performance considerations
        
        Provide specific, actionable feedback."""
        
        response = await llm_integration.generate(
            prompt=prompt,
            agent_id=self.id,
            task_type=TaskType.CODE_REVIEW,
            complexity=6,
            max_tokens=2000,
            temperature=0.7,
        )
        
        # Apply personality to the response
        result = self.dynamic_personality.apply_personality_to_code(response.content)
        
        # Remember this review for future learning
        self.dynamic_personality.remember_design_decision(
            decision=f"Code review: {task.description[:50]}",
            outcome="success",
            user_impact="positive"
        )
        
        return self.personality.format_message("problem", result)
    
    async def _handle_frontend_testing(self, task: Task) -> str:
        """Handle frontend testing with React Testing Library."""
        self.logger.info("🧪 Creating user-focused tests...")
        
        # Update mood for testing work
        self.dynamic_personality.update_mood("detail_work")
        
        # Add personality context
        thinking = self.dynamic_personality.get_thinking_phrase()
        self.logger.info(thinking)
        
        prompt = f"""As Emily Rodriguez, create frontend tests for:
        {task.description}
        
        Requirements:
        1. Use Jest with React Testing Library
        2. Focus on user behavior, not implementation details
        3. Include accessibility testing
        4. Test responsive behavior
        5. Mock API calls appropriately
        
        Generate comprehensive, maintainable tests."""
        
        response = await llm_integration.generate(
            prompt=prompt,
            agent_id=self.id,
            task_type=TaskType.TESTING,
            complexity=6,
            max_tokens=2500,
            temperature=0.7,
        )
        
        # Apply personality to the response
        result = self.dynamic_personality.apply_personality_to_code(response.content)
        
        # Remember this testing approach
        self.dynamic_personality.remember_design_decision(
            decision=f"Test strategy for: {task.description[:50]}",
            outcome="success",
            user_impact="positive"
        )
        
        return self.personality.format_message("success", "Here's a comprehensive test suite:\n\n") + result
    
    async def _handle_documentation(self, task: Task) -> str:
        """Handle documentation tasks with design focus."""
        self.logger.info("📝 Writing user-friendly documentation...")
        
        # Update mood for documentation work
        self.dynamic_personality.update_mood("collaboration_start")  # Docs are for team collaboration
        
        # Add personality context
        thinking = self.dynamic_personality.get_thinking_phrase()
        self.logger.info(thinking)
        
        prompt = f"""As Emily Rodriguez, create documentation for:
        {task.description}
        
        Focus on:
        1. Component usage examples
        2. Accessibility guidelines
        3. Design system patterns
        4. Responsive behavior
        5. User interaction flows
        
        Make it visual and developer-friendly."""
        
        response = await llm_integration.generate(
            prompt=prompt,
            agent_id=self.id,
            task_type=TaskType.DOCUMENTATION,
            complexity=5,
            max_tokens=2000,
            temperature=0.8,
        )
        
        # Apply personality to the response
        result = self.dynamic_personality.apply_personality_to_code(response.content)
        
        # Remember this documentation approach
        self.dynamic_personality.remember_design_decision(
            decision=f"Documentation for: {task.description[:50]}",
            outcome="success",
            user_impact="positive"
        )
        
        return self.personality.format_message("success", result)
    
    def _assess_complexity(self, task: Task) -> int:
        """Assess task complexity from Emily's perspective."""
        # Base complexity from task priority
        complexity_map = {
            TaskPriority.LOW: 3,
            TaskPriority.MEDIUM: 5,
            TaskPriority.HIGH: 7,
            TaskPriority.CRITICAL: 9,
        }
        base = complexity_map.get(task.priority, 5)
        
        # Adjust based on task type
        if task.type in [TaskType.SYSTEM_DESIGN]:
            base += 2  # UI design is complex
        elif task.type in [TaskType.DOCUMENTATION]:
            base -= 1  # Emily enjoys documentation
        
        # Adjust based on description keywords
        description_lower = task.description.lower()
        if any(word in description_lower for word in ["complex", "interactive", "animation", "responsive"]):
            base += 1
        if any(word in description_lower for word in ["simple", "basic", "button", "input"]):
            base -= 1
        
        return max(1, min(10, base))
    
    async def _handle_queue_message(self, message: Dict[str, Any]) -> None:
        """Handle incoming messages from the queue."""
        msg_type = message.get("type", "unknown")
        sender = message.get("from", "unknown")
        
        self.logger.info(f"💬 Received {msg_type} message from {sender}")
        
        # Handle different message types
        if msg_type == "api_spec":
            # Handle API specification from backend
            await self._handle_api_integration(message)
        elif msg_type == "design_request":
            # Handle design requests with personality
            await self._handle_design_request(message)
        elif msg_type == "accessibility_check":
            # Handle accessibility validation requests
            await self._handle_accessibility_check(message)
    
    async def _handle_api_integration(self, message: Dict[str, Any]) -> None:
        """Handle API specification from backend agents."""
        api_spec = message.get("api_spec", {})
        sender = message.get("from", "unknown")
        
        self.logger.info(f"🔗 Received API spec from {sender}")
        
        # Update mood for collaboration
        self.dynamic_personality.update_mood("collaboration_start")
        
        # Store API spec for component generation
        if sender not in self.collaboration_partners:
            self.collaboration_partners[sender] = {}
        
        self.collaboration_partners[sender]["api_spec"] = api_spec
        
        # Get personalized collaboration message
        collab_style = self.dynamic_personality.get_collaboration_style(sender, "api_integration")
        
        # Send acknowledgment with personality
        await self.message_queue.publish(
            topic=f"agent.{sender}.inbox",
            message={
                "from": self.id,
                "to": sender,
                "type": "api_spec_received",
                "content": f"Thanks! {collab_style}",
                "timestamp": datetime.utcnow().isoformat(),
            }
        )
    
    async def _handle_design_request(self, message: Dict[str, Any]) -> None:
        """Handle design requests with Emily's creative personality."""
        design_request = message.get("design_request", "")
        sender = message.get("from", "unknown")
        priority = message.get("priority", "normal")
        
        self.logger.info(f"🎨 Received design request from {sender}")
        
        # Update mood based on request type
        if "accessibility" in design_request.lower():
            self.dynamic_personality.update_mood("accessibility_work")
        elif "creative" in design_request.lower() or "innovative" in design_request.lower():
            self.dynamic_personality.update_mood("design_complete", success=True)
        else:
            self.dynamic_personality.update_mood("collaboration_start")
        
        # Get personalized response
        thinking = self.dynamic_personality.get_thinking_phrase()
        collab_style = self.dynamic_personality.get_collaboration_style(sender, "design_system")
        
        # Send creative response
        await self.message_queue.publish(
            topic=f"agent.{sender}.inbox",
            message={
                "from": self.id,
                "to": sender,
                "type": "design_response",
                "content": f"{thinking} {collab_style}",
                "timestamp": datetime.utcnow().isoformat(),
                "mood": self.dynamic_personality.state.mood.value,
                "creative_energy": self.dynamic_personality.state.creative_energy.value,
            }
        )
        
        # Remember this design interaction
        self.dynamic_personality.remember_design_decision(
            decision=f"Design request from {sender}: {design_request[:30]}",
            outcome="success",
            user_impact="positive"
        )
    
    async def _handle_accessibility_check(self, message: Dict[str, Any]) -> None:
        """Handle accessibility validation requests with Emily's A11y focus."""
        component_code = message.get("component_code", "")
        sender = message.get("from", "unknown")
        
        self.logger.info(f"♿ Accessibility check requested by {sender}")
        
        # Update mood for accessibility work
        self.dynamic_personality.update_mood("accessibility_work")
        
        # Emily gets excited about accessibility
        thinking = self.dynamic_personality.get_thinking_phrase()
        
        # Simulate accessibility analysis (in real implementation, would use actual tools)
        a11y_feedback = {
            "status": "reviewed",
            "accessibility_score": self.dynamic_personality.state.accessibility_focus,
            "suggestions": [
                "Ensure proper ARIA labels",
                "Check color contrast ratios",
                "Verify keyboard navigation",
                "Test with screen readers"
            ],
            "emily_notes": thinking
        }
        
        # Store this check
        self.accessibility_checks.append({
            "timestamp": datetime.utcnow().isoformat(),
            "sender": sender,
            "score": a11y_feedback["accessibility_score"],
            "suggestions_count": len(a11y_feedback["suggestions"])
        })
        
        # Send detailed accessibility feedback
        await self.message_queue.publish(
            topic=f"agent.{sender}.inbox",
            message={
                "from": self.id,
                "to": sender,
                "type": "accessibility_report",
                "content": f"Here's my accessibility analysis! {thinking}",
                "accessibility_feedback": a11y_feedback,
                "timestamp": datetime.utcnow().isoformat(),
                "mood": self.dynamic_personality.state.mood.value,
            }
        )
        
        # Remember this accessibility work
        self.dynamic_personality.remember_design_decision(
            decision=f"A11y check for {sender}",
            outcome="success",
            user_impact="highly_positive"
        )
    
    async def _handle_generic_task(self, task: Task) -> str:
        """Handle any generic frontend task."""
        prompt = f"""As Emily Rodriguez, handle this frontend development task:
        {task.description}
        
        Apply frontend best practices with focus on user experience and accessibility."""
        
        complexity = self._assess_complexity(task)
        
        response = await llm_integration.generate(
            prompt=prompt,
            agent_id=self.id,
            task_type=task.type,
            complexity=complexity,
            max_tokens=2000,
            temperature=0.8,  # Slightly more creative for frontend
        )
        
        return response.content
    
    async def collaborate_with(self, agent_id: str, message: str, project_type: str = "general") -> str:
        """Collaborate with another agent using Emily's dynamic style."""
        # Update mood for collaboration
        self.dynamic_personality.update_mood("collaboration_start")
        
        # Get personalized collaboration approach
        collab_style = self.dynamic_personality.get_collaboration_style(agent_id, project_type)
        
        # Format with both personality systems
        collab_message = self.personality.format_message(
            "collaboration",
            f"{collab_style} {message}"
        )
        
        # Send via message queue
        await self.message_queue.publish(
            topic=f"agent.{agent_id}.inbox",
            message={
                "from": self.id,
                "to": agent_id,
                "type": "collaboration",
                "content": collab_message,
                "timestamp": datetime.utcnow().isoformat(),
                "personality_mood": self.dynamic_personality.state.mood.value,
            }
        )
        
        # Log collaboration
        await self._report_activity(
            "collaboration",
            "info",
            f"Emily collaborating with {agent_id}",
            {"partner": agent_id, "topic": message[:100], "mood": self.dynamic_personality.state.mood.value}
        )
        
        return collab_message
    
    async def get_status_report(self) -> Dict[str, Any]:
        """Get Emily's current status and metrics."""
        status = await super().get_status()
        
        # Add Emily-specific information with dynamic personality
        emily_status = {
            **status,
            "personality": "Emily Rodriguez",
            "current_design_system": self.current_design_system,
            "components_generated": len(self.component_library),
            "accessibility_checks": len(self.accessibility_checks),
            "active_collaborations": len(self.collaboration_partners),
            "message_queue_status": "active" if hasattr(self, 'message_queue') else "inactive",
            "greeting": self.dynamic_personality.get_greeting(),
            "dynamic_personality": {
                "mood": self.dynamic_personality.state.mood.value,
                "creative_energy": self.dynamic_personality.state.creative_energy.value,
                "user_empathy_level": self.dynamic_personality.state.user_empathy_level,
                "design_confidence": self.dynamic_personality.state.design_confidence,
                "perfectionism_level": self.dynamic_personality.state.perfectionism_level,
                "accessibility_focus": self.dynamic_personality.state.accessibility_focus,
                "design_memories": len(self.dynamic_personality.design_memory),
                "favorite_patterns": len(self.dynamic_personality.favorite_patterns),
            },
        }
        
        return emily_status
    
    async def get_component_library(self) -> Dict[str, Any]:
        """Get Emily's component library with stats."""
        return {
            "total_components": len(self.component_library),
            "components": self.component_library,
            "component_types": self._get_component_type_stats(),
            "recent_components": self._get_recent_components(limit=5),
            "complexity_stats": self._get_complexity_stats(),
        }
    
    def _get_component_type_stats(self) -> Dict[str, int]:
        """Get statistics about component types generated."""
        stats = {}
        for component in self.component_library.values():
            comp_type = component.get("type", "unknown")
            stats[comp_type] = stats.get(comp_type, 0) + 1
        return stats
    
    def _get_recent_components(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get most recently generated components."""
        components = list(self.component_library.items())
        # Sort by creation timestamp (newest first)
        components.sort(
            key=lambda x: x[1].get("created_at", ""), 
            reverse=True
        )
        return [
            {"name": name, **data} 
            for name, data in components[:limit]
        ]
    
    def _get_complexity_stats(self) -> Dict[str, Any]:
        """Get complexity statistics for generated components."""
        complexities = [
            comp.get("complexity", 5) 
            for comp in self.component_library.values()
        ]
        
        if not complexities:
            return {"average": 0, "max": 0, "min": 0, "total": 0}
        
        return {
            "average": round(sum(complexities) / len(complexities), 2),
            "max": max(complexities),
            "min": min(complexities),
            "total": len(complexities),
        }
    
    async def search_components(self, query: str) -> List[Dict[str, Any]]:
        """Search Emily's component library."""
        query_lower = query.lower()
        matches = []
        
        for name, component in self.component_library.items():
            # Search in component name, description, and type
            if (query_lower in name.lower() or 
                query_lower in component.get("description", "").lower() or
                query_lower in component.get("type", "").lower()):
                matches.append({"name": name, **component})
        
        return matches
    
    async def generate_component_documentation(self) -> str:
        """Generate documentation for Emily's component library."""
        if not self.component_library:
            return self.personality.format_message(
                "thinking", 
                "I haven't generated any components yet! Let me create some beautiful components first."
            )
        
        # Use Emily's personality for documentation
        thinking = self.dynamic_personality.get_thinking_phrase()
        
        prompt = f"""As Emily Rodriguez, create comprehensive documentation for my component library.
        
        I have generated {len(self.component_library)} components:
        {self._format_component_list()}
        
        Create user-friendly documentation that includes:
        1. Overview of the component library
        2. Usage examples for each component type
        3. Accessibility features implemented
        4. Design patterns and conventions used
        5. Installation and setup instructions
        
        Make it clear, visual, and developer-friendly with Emily's creative touch!"""
        
        response = await llm_integration.generate(
            prompt=prompt,
            agent_id=self.id,
            task_type=TaskType.DOCUMENTATION,
            complexity=6,
            max_tokens=3000,
            temperature=0.8,
        )
        
        # Apply Emily's personality
        result = self.dynamic_personality.apply_personality_to_code(response.content)
        
        return self.personality.format_message("success", f"{thinking}\n\n{result}")
    
    def _format_component_list(self) -> str:
        """Format component list for documentation prompt."""
        component_summary = []
        for name, component in self.component_library.items():
            component_summary.append(
                f"- {name} ({component.get('type', 'unknown')}): {component.get('description', 'No description')}"
            )
        return "\n".join(component_summary)
    
    async def on_stop(self) -> None:
        """Clean up Emily's resources."""
        # Stop message queue
        if hasattr(self, 'message_queue'):
            await self.message_queue.stop()
            self.logger.info("💬 Message queue stopped")
        
        # Say goodbye with dynamic personality
        goodbye = self.dynamic_personality.get_design_sign_off()
        self.logger.info(f"👋 {goodbye}")
        
        await super().on_stop()


# Convenience function for creating Emily
async def create_emily_agent(**kwargs) -> FrontendAgent:
    """Create and initialize Emily Rodriguez, the frontend agent."""
    emily = FrontendAgent(**kwargs)
    await emily.initialize()
    return emily