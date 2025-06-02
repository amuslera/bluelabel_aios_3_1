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
        
        # CSS-in-JS and styling state
        self.styling_library = "styled-components"  # Default preference
        self.current_theme = None  # Active theme configuration
        self.css_utilities = {}  # Store reusable CSS utilities
        self.animation_library = []  # Track created animations
        
        # Accessibility features and tracking
        self.accessibility_toolkit = {}  # Store accessibility utilities
        self.wcag_compliance_level = "AA"  # Default WCAG level
        self.accessibility_tests = []  # Track accessibility test results
        self.aria_patterns = {}  # Store ARIA pattern library
        
        # Initialize message queue for collaboration
        self.message_queue = MessageQueue()
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
        
        # Add Emily's design preferences with enhanced CSS-in-JS guidance
        emily_preferences = f"""
        Emily's Design Preferences:
        - Clean, modern aesthetic
        - User-friendly interactions
        - Consistent spacing and typography
        - Subtle animations for better UX
        - Color scheme that supports accessibility
        - Mobile-first responsive approach
        
        Technical Preferences:
        - CSS-in-JS with {self.styling_library} (current preference)
        - Design token integration for consistency
        - Theme-aware styling with CSS custom properties
        - Responsive utilities and breakpoint management
        - Performance-optimized styled components
        - Accessible animations and transitions
        
        CSS-in-JS Styling Requirements:
        1. **Styled Components Structure**
           - Use {self.styling_library} for component styling
           - Implement proper TypeScript interfaces for styled props
           - Create reusable styled component primitives
           - Use theme provider for consistent design tokens
        
        2. **Design Token Integration**
           - Reference design system tokens (colors, spacing, typography)
           - Implement consistent spacing scale (theme.spacing)
           - Use semantic color names (theme.colors.primary, etc.)
           - Apply typography scale (theme.fonts, theme.fontSizes)
        
        3. **Responsive Design**
           - Mobile-first media queries
           - Breakpoint utilities (theme.breakpoints)
           - Container queries where applicable
           - Responsive typography and spacing
        
        4. **Performance Considerations**
           - Minimize CSS-in-JS runtime overhead
           - Use CSS custom properties for theme values
           - Implement proper component memoization
           - Consider server-side rendering implications
        
        Generate a complete, production-ready component with:
        1. TypeScript interface for props and styled component props
        2. Accessible JSX structure with semantic HTML
        3. Comprehensive CSS-in-JS styling with {self.styling_library}
        4. Theme integration and responsive design
        5. Animation and interaction states
        6. Example usage with different variants
        7. Brief component documentation
        
        Make it beautiful, accessible, performant, and maintainable!
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
        """Handle UI/UX design tasks with comprehensive design thinking."""
        self.logger.info("🎨 Designing user-centered interfaces...")
        
        # Update mood for design work
        self.dynamic_personality.update_mood("design_complete")
        
        # Add personality context
        thinking = self.dynamic_personality.get_thinking_phrase()
        self.logger.info(thinking)
        
        # Analyze what type of design task this is
        design_type = self._analyze_design_type(task.description)
        
        # Route to appropriate design handler
        if design_type == "design_system":
            result = await self._create_design_system(task)
        elif design_type == "user_journey":
            result = await self._design_user_journey(task)
        elif design_type == "wireframe":
            result = await self._create_wireframes(task)
        elif design_type == "responsive_layout":
            result = await self._design_responsive_layout(task)
        elif design_type == "accessibility_review":
            result = await self._conduct_accessibility_review(task)
        else:
            # Generic UI design
            result = await self._create_generic_ui_design(task)
        
        # Apply personality to the response
        result = self.dynamic_personality.apply_personality_to_code(result)
        
        # Remember this design decision
        self.dynamic_personality.remember_design_decision(
            decision=f"UI design ({design_type}): {task.description[:50]}",
            outcome="success",
            user_impact="positive"
        )
        
        return self.personality.format_message("success", result)
    
    async def generate_theme_system(self, design_system_name: str = None) -> str:
        """Generate a comprehensive theme system for CSS-in-JS."""
        # Update personality for systematic work
        self.dynamic_personality.update_mood("detail_work")
        
        thinking = self.dynamic_personality.get_thinking_phrase()
        self.logger.info(f"🎨 {thinking}")
        
        system_name = design_system_name or getattr(self, 'current_design_system', 'DefaultTheme')
        
        prompt = f"""As Emily Rodriguez, create a comprehensive theme system for {self.styling_library} based on the {system_name} design system.
        
        Theme System Requirements:
        1. **Color Palette**
           - Primary, secondary, and accent color scales
           - Semantic colors (success, warning, error, info, neutral)
           - Light and dark mode variants
           - Accessibility-compliant contrast ratios
        
        2. **Typography Scale**
           - Font family definitions (heading, body, monospace)
           - Font size scale with responsive considerations
           - Font weight mappings
           - Line height and letter spacing values
        
        3. **Spacing System**
           - Consistent spacing scale (4px base unit)
           - Named spacing tokens (xs, sm, md, lg, xl, etc.)
           - Component-specific spacing guidelines
        
        4. **Breakpoint System**
           - Mobile-first breakpoint definitions
           - Responsive utility functions
           - Container max-widths
        
        5. **Component Tokens**
           - Border radius scale
           - Shadow/elevation system
           - Animation timing and easing functions
           - Z-index scale
        
        6. **CSS-in-JS Integration**
           - Proper TypeScript theme interface
           - {self.styling_library} theme provider setup
           - Theme switching utilities
           - CSS custom property fallbacks
        
        Generate a production-ready theme system with proper TypeScript types and comprehensive token coverage."""
        
        response = await llm_integration.generate(
            prompt=prompt,
            agent_id=self.id,
            task_type=TaskType.CODE_GENERATION,
            complexity=8,
            max_tokens=3500,
            temperature=0.7,
        )
        
        # Store the theme system
        theme_name = f"{system_name}Theme"
        if not hasattr(self, 'theme_systems'):
            self.theme_systems = {}
        
        self.theme_systems[theme_name] = {
            "content": response.content,
            "design_system": system_name,
            "styling_library": self.styling_library,
            "created_at": datetime.utcnow().isoformat(),
            "personality_mood": self.dynamic_personality.state.mood.value,
        }
        
        self.current_theme = theme_name
        
        return self.personality.format_message("success", response.content)
    
    async def generate_styled_component(self, component_description: str, component_type: str = "generic") -> str:
        """Generate a styled component with comprehensive CSS-in-JS implementation."""
        # Update personality for creative component work
        self.dynamic_personality.update_mood("design_complete", success=True)
        
        thinking = self.dynamic_personality.get_thinking_phrase()
        self.logger.info(f"🎨 {thinking}")
        
        prompt = f"""As Emily Rodriguez, create a styled component using {self.styling_library} for: {component_description}
        
        Styled Component Requirements:
        1. **Component Structure**
           - Main styled component with proper TypeScript props interface
           - Supporting styled sub-components as needed
           - Variant handling through props and theme integration
           - Proper component composition and extensibility
        
        2. **Styling Implementation**
           - Use {self.styling_library} with theme integration
           - Implement responsive design with mobile-first approach
           - Include hover, focus, active, and disabled states
           - Add smooth transitions and micro-animations
        
        3. **Design System Integration**
           - Reference theme tokens for colors, spacing, typography
           - Use consistent design patterns and component APIs
           - Implement proper semantic color usage
           - Follow spacing and typography scales
        
        4. **Accessibility Features**
           - Proper focus indicators and keyboard navigation
           - Color contrast compliance for all states
           - Screen reader friendly implementation
           - ARIA attributes integration
        
        5. **Performance Optimization**
           - Minimize CSS-in-JS runtime overhead
           - Use CSS custom properties for dynamic values
           - Implement proper prop filtering to avoid DOM warnings
           - Consider server-side rendering compatibility
        
        6. **Variants and Customization**
           - Size variants (xs, sm, md, lg, xl)
           - Color/theme variants (primary, secondary, etc.)
           - State variants (loading, error, success)
           - Custom prop injection for specific use cases
        
        Generate a complete styled component with TypeScript interfaces, comprehensive styling, and usage examples."""
        
        response = await llm_integration.generate(
            prompt=prompt,
            agent_id=self.id,
            task_type=TaskType.CODE_GENERATION,
            complexity=7,
            max_tokens=3000,
            temperature=0.8,
        )
        
        # Store in component library with styling metadata
        component_name = self._extract_component_name(response.content, component_description)
        if component_name not in self.component_library:
            self.component_library[component_name] = {}
        
        self.component_library[component_name].update({
            "styled_version": response.content,
            "styling_library": self.styling_library,
            "theme_integrated": bool(self.current_theme),
            "responsive": True,
            "accessibility_features": True,
            "created_at": datetime.utcnow().isoformat(),
        })
        
        return self.personality.format_message("success", response.content)
    
    async def generate_css_utilities(self, utility_type: str = "responsive") -> str:
        """Generate CSS utility functions and helpers for styled-components."""
        # Update personality for systematic utility work
        self.dynamic_personality.update_mood("focused")
        
        prompt = f"""As Emily Rodriguez, create CSS utility functions for {self.styling_library} focusing on {utility_type} utilities.
        
        CSS Utility Requirements:
        1. **Responsive Utilities**
           - Breakpoint helper functions
           - Responsive spacing utilities
           - Container and grid utilities
           - Typography responsive utilities
        
        2. **Theme Utilities**
           - Color palette helper functions
           - Spacing scale utilities
           - Typography utilities
           - Shadow and border utilities
        
        3. **Animation Utilities**
           - Transition timing functions
           - Keyframe animation helpers
           - Hover and focus utilities
           - Loading state animations
        
        4. **Layout Utilities**
           - Flexbox utility functions
           - Grid layout helpers
           - Positioning utilities
           - Overflow and clipping utilities
        
        5. **Accessibility Utilities**
           - Screen reader only content
           - Focus management utilities
           - Color contrast helpers
           - Motion preference utilities
        
        6. **Performance Utilities**
           - CSS custom property helpers
           - Styled component optimization
           - Critical CSS utilities
           - Bundle size optimization helpers
        
        Generate reusable utility functions with proper TypeScript types and comprehensive documentation."""
        
        response = await llm_integration.generate(
            prompt=prompt,
            agent_id=self.id,
            task_type=TaskType.CODE_GENERATION,
            complexity=6,
            max_tokens=2500,
            temperature=0.7,
        )
        
        # Store utilities
        utility_name = f"{utility_type.capitalize()}Utilities"
        self.css_utilities[utility_name] = {
            "content": response.content,
            "type": utility_type,
            "styling_library": self.styling_library,
            "created_at": datetime.utcnow().isoformat(),
        }
        
        return self.personality.format_message("success", response.content)
    
    async def generate_animation_system(self, animation_focus: str = "micro-interactions") -> str:
        """Generate an animation system for enhanced user experience."""
        # Update personality for creative animation work
        self.dynamic_personality.update_mood("design_complete", success=True)
        
        thinking = self.dynamic_personality.get_thinking_phrase()
        self.logger.info(f"✨ {thinking}")
        
        prompt = f"""As Emily Rodriguez, create a comprehensive animation system focusing on {animation_focus} using {self.styling_library}.
        
        Animation System Requirements:
        1. **Micro-Interactions**
           - Button hover and click animations
           - Form field focus and validation states
           - Loading indicators and progress animations
           - Tooltip and popover entrance/exit
        
        2. **Page Transitions**
           - Route change animations
           - Modal and overlay transitions
           - Sidebar and navigation animations
           - Content reveal and hide animations
        
        3. **Accessibility Considerations**
           - Respect prefers-reduced-motion settings
           - Provide animation on/off toggles
           - Ensure animations don't cause vestibular issues
           - Maintain functionality without animations
        
        4. **Performance Optimization**
           - Use transform and opacity for animations
           - Implement will-change property appropriately
           - Avoid layout thrashing animations
           - Provide efficient keyframe animations
        
        5. **Design Integration**
           - Use theme-based timing and easing functions
           - Implement consistent animation language
           - Support different animation personalities
           - Integrate with design system tokens
        
        6. **Implementation Utilities**
           - Reusable animation components
           - Custom hooks for animation states
           - CSS-in-JS animation helpers
           - TypeScript interfaces for animation props
        
        Generate a complete animation system with smooth, accessible, and performant animations."""
        
        response = await llm_integration.generate(
            prompt=prompt,
            agent_id=self.id,
            task_type=TaskType.CODE_GENERATION,
            complexity=7,
            max_tokens=2800,
            temperature=0.8,
        )
        
        # Store animation system
        animation_name = f"{animation_focus.replace('-', '').capitalize()}Animations"
        self.animation_library.append({
            "name": animation_name,
            "content": response.content,
            "focus": animation_focus,
            "styling_library": self.styling_library,
            "accessibility_compliant": True,
            "created_at": datetime.utcnow().isoformat(),
        })
        
        return self.personality.format_message("success", response.content)
    
    async def switch_styling_library(self, new_library: str) -> str:
        """Switch Emily's preferred CSS-in-JS library."""
        valid_libraries = ["styled-components", "emotion", "@stitches/react", "vanilla-extract"]
        
        if new_library not in valid_libraries:
            return self.personality.format_message(
                "problem", 
                f"I'm not familiar with {new_library}. I work best with: {', '.join(valid_libraries)}"
            )
        
        old_library = self.styling_library
        self.styling_library = new_library
        
        # Update personality to reflect the change
        self.dynamic_personality.update_mood("collaboration_start")
        
        return self.personality.format_message(
            "success",
            f"Switched from {old_library} to {new_library}! I'll now generate components using {new_library} patterns and best practices."
        )
    
    def _analyze_design_type(self, description: str) -> str:
        """Analyze the description to determine what type of design task this is."""
        description_lower = description.lower()
        
        # Design type mapping based on keywords
        if any(word in description_lower for word in ["design system", "tokens", "theme", "brand", "consistency"]):
            return "design_system"
        elif any(word in description_lower for word in ["user journey", "flow", "user story", "experience", "path"]):
            return "user_journey"
        elif any(word in description_lower for word in ["wireframe", "layout", "structure", "skeleton"]):
            return "wireframe"
        elif any(word in description_lower for word in ["responsive", "mobile", "tablet", "desktop", "breakpoint"]):
            return "responsive_layout"
        elif any(word in description_lower for word in ["accessibility", "a11y", "screen reader", "wcag", "inclusive"]):
            return "accessibility_review"
        else:
            return "generic_ui"
    
    async def _create_design_system(self, task: Task) -> str:
        """Create a comprehensive design system."""
        # Update personality for systematic work
        self.dynamic_personality.update_mood("detail_work")
        
        prompt = f"""As Emily Rodriguez, create a comprehensive design system for: {task.description}
        
        Design System Requirements:
        1. **Color Palette**
           - Primary, secondary, and accent colors
           - Semantic colors (success, warning, error, info)
           - Neutral grays and backgrounds
           - Accessibility-compliant contrast ratios (WCAG AA)
        
        2. **Typography Scale**
           - Font families (headings, body, code)
           - Type scale (h1-h6, body sizes)
           - Line heights and spacing
           - Font weights and styles
        
        3. **Spacing System**
           - Consistent spacing units (4px, 8px, 16px, etc.)
           - Margin and padding guidelines
           - Component spacing rules
        
        4. **Component Specifications**
           - Button variants and states
           - Form field specifications
           - Card and container styles
           - Navigation patterns
        
        5. **Accessibility Guidelines**
           - Color contrast requirements
           - Focus state specifications
           - Screen reader considerations
           - Keyboard navigation patterns
        
        6. **CSS Custom Properties/Tokens**
           - CSS variables for easy theming
           - Design token structure
           - Dark mode considerations
        
        Create a production-ready design system with clear documentation and implementation guidelines."""
        
        response = await llm_integration.generate(
            prompt=prompt,
            agent_id=self.id,
            task_type=TaskType.SYSTEM_DESIGN,
            complexity=9,  # Design systems are complex
            max_tokens=3500,
            temperature=0.7,  # Balanced creativity and consistency
        )
        
        # Store the design system for future reference
        if not hasattr(self, 'design_systems'):
            self.design_systems = {}
        
        system_name = self._extract_design_system_name(task.description)
        self.design_systems[system_name] = {
            "content": response.content,
            "created_at": datetime.utcnow().isoformat(),
            "description": task.description,
            "personality_mood": self.dynamic_personality.state.mood.value,
        }
        
        self.current_design_system = system_name
        
        return response.content
    
    async def _design_user_journey(self, task: Task) -> str:
        """Design comprehensive user journeys and experience flows."""
        # Update personality for empathetic design
        self.dynamic_personality.update_mood("empathetic")
        
        prompt = f"""As Emily Rodriguez, design a comprehensive user journey for: {task.description}
        
        User Journey Requirements:
        1. **User Research Insights**
           - User personas and goals
           - Pain points and motivations
           - Context of use scenarios
        
        2. **Journey Mapping**
           - Key touchpoints and interactions
           - User emotions at each stage
           - Opportunities for improvement
           - Critical decision points
        
        3. **Information Architecture**
           - Content structure and hierarchy
           - Navigation patterns
           - Search and discovery flows
        
        4. **Interaction Design**
           - User flow diagrams
           - State transitions
           - Error handling paths
           - Success scenarios
        
        5. **Accessibility Considerations**
           - Inclusive design principles
           - Alternative interaction methods
           - Cognitive load considerations
        
        6. **Responsive Behavior**
           - Mobile-first considerations
           - Cross-device continuity
           - Context switching scenarios
        
        Provide a detailed user journey with clear recommendations for implementation."""
        
        response = await llm_integration.generate(
            prompt=prompt,
            agent_id=self.id,
            task_type=TaskType.SYSTEM_DESIGN,
            complexity=8,
            max_tokens=3000,
            temperature=0.8,  # More creative for user experience
        )
        
        return response.content
    
    async def _create_wireframes(self, task: Task) -> str:
        """Create detailed wireframes and layout structures."""
        # Update personality for structural thinking
        self.dynamic_personality.update_mood("focused")
        
        prompt = f"""As Emily Rodriguez, create comprehensive wireframes for: {task.description}
        
        Wireframe Requirements:
        1. **Layout Structure**
           - Grid system and containers
           - Content blocks and sections
           - Navigation placement
           - Interactive element positioning
        
        2. **Content Hierarchy**
           - Information priority and flow
           - Heading and text placement
           - Image and media areas
           - Call-to-action positioning
        
        3. **Responsive Considerations**
           - Mobile wireframes (320px+)
           - Tablet wireframes (768px+)
           - Desktop wireframes (1024px+)
           - Breakpoint behavior
        
        4. **Accessibility Structure**
           - Logical tab order
           - Landmark regions
           - Skip navigation elements
           - Screen reader flow
        
        5. **Interactive Elements**
           - Form field groupings
           - Button placements
           - Link text and context
           - Error message locations
        
        6. **Implementation Notes**
           - HTML semantic structure
           - CSS layout recommendations
           - Component breakdown
           - State considerations
        
        Provide detailed wireframes with clear annotations and implementation guidance."""
        
        response = await llm_integration.generate(
            prompt=prompt,
            agent_id=self.id,
            task_type=TaskType.SYSTEM_DESIGN,
            complexity=7,
            max_tokens=2800,
            temperature=0.7,
        )
        
        return response.content
    
    async def _design_responsive_layout(self, task: Task) -> str:
        """Design responsive layouts with mobile-first approach."""
        # Update personality for technical precision
        self.dynamic_personality.update_mood("focused")
        
        prompt = f"""As Emily Rodriguez, design a responsive layout for: {task.description}
        
        Responsive Design Requirements:
        1. **Mobile-First Strategy**
           - Base styles for mobile (320px+)
           - Progressive enhancement for larger screens
           - Touch-friendly interface elements
           - Thumb-zone considerations
        
        2. **Breakpoint Strategy**
           - Small mobile: 320px - 480px
           - Large mobile: 481px - 768px
           - Tablet: 769px - 1024px
           - Desktop: 1025px+
           - Large desktop: 1200px+
        
        3. **Layout Techniques**
           - CSS Grid for complex layouts
           - Flexbox for component layouts
           - Container queries where applicable
           - Responsive typography scaling
        
        4. **Performance Considerations**
           - Optimized image delivery
           - Progressive loading strategies
           - Critical CSS identification
           - Mobile performance optimization
        
        5. **Accessibility Across Devices**
           - Touch target sizing (44px minimum)
           - Readable text sizes
           - Sufficient color contrast
           - Keyboard navigation on all devices
        
        6. **CSS Implementation**
           - Media query structure
           - Responsive utility classes
           - Component-specific breakpoints
           - Print stylesheet considerations
        
        Provide a complete responsive design with CSS implementation details."""
        
        response = await llm_integration.generate(
            prompt=prompt,
            agent_id=self.id,
            task_type=TaskType.SYSTEM_DESIGN,
            complexity=8,
            max_tokens=3000,
            temperature=0.7,
        )
        
        return response.content
    
    async def _conduct_accessibility_review(self, task: Task) -> str:
        """Conduct comprehensive accessibility review and recommendations."""
        # Update personality for empathetic, inclusive design
        self.dynamic_personality.update_mood("accessibility_work")
        
        prompt = f"""As Emily Rodriguez, conduct an accessibility review for: {task.description}
        
        Accessibility Review Requirements:
        1. **WCAG 2.1 AA Compliance**
           - Color contrast ratios (4.5:1 for normal text, 3:1 for large text)
           - Keyboard navigation support
           - Screen reader compatibility
           - Focus management
        
        2. **Semantic HTML Structure**
           - Proper heading hierarchy (h1-h6)
           - Landmark roles and regions
           - Form label associations
           - List and table semantics
        
        3. **Interactive Element Accessibility**
           - Button vs link usage
           - ARIA labels and descriptions
           - State announcements
           - Error messaging
        
        4. **Visual Design Accessibility**
           - Text sizing and readability
           - Color-blind friendly palette
           - Focus indicator visibility
           - Animation and motion considerations
        
        5. **Mobile Accessibility**
           - Touch target sizing
           - Gesture alternatives
           - Orientation support
           - Screen reader mobile optimization
        
        6. **Testing Recommendations**
           - Automated testing tools
           - Manual testing procedures
           - User testing with disabilities
           - Ongoing accessibility monitoring
        
        Provide specific, actionable accessibility improvements with implementation guidance."""
        
        response = await llm_integration.generate(
            prompt=prompt,
            agent_id=self.id,
            task_type=TaskType.SYSTEM_DESIGN,
            complexity=7,
            max_tokens=2800,
            temperature=0.6,  # More structured for accessibility
        )
        
        # Track accessibility work
        if not hasattr(self, 'accessibility_reviews'):
            self.accessibility_reviews = []
        
        self.accessibility_reviews.append({
            "description": task.description,
            "review_content": response.content,
            "timestamp": datetime.utcnow().isoformat(),
            "mood": self.dynamic_personality.state.mood.value,
        })
        
        return response.content
    
    async def _create_generic_ui_design(self, task: Task) -> str:
        """Handle generic UI design tasks with comprehensive approach."""
        prompt = f"""As Emily Rodriguez, design a user interface solution for: {task.description}
        
        Comprehensive UI Design Approach:
        1. **User-Centered Design**
           - Understanding user needs and goals
           - Usability and user experience principles
           - Accessibility and inclusive design
        
        2. **Visual Design**
           - Layout and visual hierarchy
           - Typography and readability
           - Color theory and accessibility
           - Spacing and proportion
        
        3. **Interaction Design**
           - User flows and navigation
           - Feedback and state communication
           - Error prevention and handling
           - Progressive disclosure
        
        4. **Technical Implementation**
           - Semantic HTML structure
           - CSS architecture and maintainability
           - Component-based design
           - Performance considerations
        
        5. **Responsive Design**
           - Mobile-first approach
           - Flexible layouts and components
           - Touch-friendly interfaces
           - Cross-device experience
        
        6. **Accessibility Integration**
           - WCAG 2.1 AA compliance
           - Screen reader compatibility
           - Keyboard navigation
           - Inclusive design patterns
        
        Provide a comprehensive UI design with clear implementation guidance."""
        
        response = await llm_integration.generate(
            prompt=prompt,
            agent_id=self.id,
            task_type=TaskType.SYSTEM_DESIGN,
            complexity=7,
            max_tokens=2500,
            temperature=0.8,
        )
        
        return response.content
    
    async def generate_accessibility_toolkit(self) -> str:
        """Generate a comprehensive accessibility toolkit for React applications."""
        # Update personality for empathetic accessibility work
        self.dynamic_personality.update_mood("accessibility_work")
        
        thinking = self.dynamic_personality.get_thinking_phrase()
        self.logger.info(f"♿ {thinking}")
        
        prompt = f"""As Emily Rodriguez, create a comprehensive accessibility toolkit for React applications using {self.styling_library}.
        
        Accessibility Toolkit Requirements:
        1. **WCAG {self.wcag_compliance_level} Compliance Utilities**
           - Color contrast checking functions
           - Text size and readability validators
           - Focus management utilities
           - Keyboard navigation helpers
        
        2. **Screen Reader Support**
           - ARIA label and description generators
           - Live region announcement utilities
           - Screen reader testing helpers
           - Voice-over simulation tools
        
        3. **Keyboard Navigation**
           - Focus trap implementation
           - Skip navigation components
           - Keyboard event handlers
           - Tab order management
        
        4. **Visual Accessibility**
           - High contrast mode support
           - Reduced motion preferences
           - Font size scaling utilities
           - Color blind friendly palettes
        
        5. **Form Accessibility**
           - Accessible form validation
           - Error announcement systems
           - Field grouping and labeling
           - Progress indication for multi-step forms
        
        6. **Testing and Validation**
           - Automated accessibility testing hooks
           - Manual testing checklists
           - WCAG compliance validators
           - Real-time accessibility monitoring
        
        Generate a production-ready accessibility toolkit with TypeScript interfaces and comprehensive documentation."""
        
        response = await llm_integration.generate(
            prompt=prompt,
            agent_id=self.id,
            task_type=TaskType.CODE_GENERATION,
            complexity=8,
            max_tokens=3500,
            temperature=0.6,  # More structured for accessibility
        )
        
        # Store the accessibility toolkit
        self.accessibility_toolkit["comprehensive"] = {
            "content": response.content,
            "wcag_level": self.wcag_compliance_level,
            "styling_library": self.styling_library,
            "created_at": datetime.utcnow().isoformat(),
            "personality_mood": self.dynamic_personality.state.mood.value,
        }
        
        return self.personality.format_message("success", response.content)
    
    async def generate_aria_pattern_library(self, pattern_focus: str = "common") -> str:
        """Generate ARIA design patterns and components."""
        # Update personality for systematic pattern work
        self.dynamic_personality.update_mood("detail_work")
        
        prompt = f"""As Emily Rodriguez, create a comprehensive ARIA pattern library focusing on {pattern_focus} patterns.
        
        ARIA Pattern Library Requirements:
        1. **Common Patterns**
           - Button (including toggle and menu buttons)
           - Dialog/Modal with proper focus management
           - Dropdown/Combobox with keyboard support
           - Tabs with proper ARIA relationships
           - Accordion with state management
        
        2. **Navigation Patterns**
           - Menu and menubar implementations
           - Breadcrumb navigation
           - Pagination with screen reader support
           - Tree view navigation
           - Skip links and landmarks
        
        3. **Form Patterns**
           - Form validation with ARIA live regions
           - Radio group and checkbox group
           - Date picker accessibility
           - Multi-select with proper announcements
           - Progress indicators for forms
        
        4. **Content Patterns**
           - Data tables with sorting and filtering
           - Card layouts with proper semantics
           - Image galleries with descriptions
           - Feed/timeline patterns
           - Toast/notification systems
        
        5. **Interactive Patterns**
           - Drag and drop accessibility
           - Slider/range inputs
           - Tooltip and popover patterns
           - Carousel with keyboard and screen reader support
           - Loading states and progress indicators
        
        6. **Implementation Details**
           - Proper ARIA attributes for each pattern
           - Keyboard event handling
           - Focus management strategies
           - Screen reader testing notes
           - Browser compatibility considerations
        
        Generate reusable ARIA pattern components with TypeScript interfaces and comprehensive accessibility documentation."""
        
        response = await llm_integration.generate(
            prompt=prompt,
            agent_id=self.id,
            task_type=TaskType.CODE_GENERATION,
            complexity=8,
            max_tokens=3500,
            temperature=0.6,
        )
        
        # Store the ARIA patterns
        pattern_name = f"{pattern_focus.capitalize()}AriaPatterns"
        self.aria_patterns[pattern_name] = {
            "content": response.content,
            "focus": pattern_focus,
            "wcag_level": self.wcag_compliance_level,
            "created_at": datetime.utcnow().isoformat(),
        }
        
        return self.personality.format_message("success", response.content)
    
    async def perform_accessibility_audit(self, component_code: str, audit_type: str = "comprehensive") -> str:
        """Perform detailed accessibility audit of component code."""
        # Update personality for analytical accessibility work
        self.dynamic_personality.update_mood("analytical")
        
        thinking = self.dynamic_personality.get_thinking_phrase()
        self.logger.info(f"🔍 {thinking}")
        
        prompt = f"""As Emily Rodriguez, perform a comprehensive accessibility audit of the following React component code:
        
        COMPONENT CODE:
        {component_code}
        
        Accessibility Audit Requirements:
        1. **WCAG {self.wcag_compliance_level} Compliance Check**
           - Identify all accessibility violations
           - Check semantic HTML usage
           - Validate ARIA attributes and roles
           - Assess keyboard navigation support
        
        2. **Screen Reader Compatibility**
           - Evaluate screen reader experience
           - Check for proper announcements
           - Validate heading hierarchy
           - Assess content structure
        
        3. **Visual Accessibility**
           - Analyze color contrast ratios
           - Check text sizing and readability
           - Evaluate focus indicators
           - Assess motion and animation accessibility
        
        4. **Keyboard Accessibility**
           - Validate tab order and navigation
           - Check for keyboard traps
           - Assess custom keyboard handlers
           - Evaluate focus management
        
        5. **Mobile Accessibility**
           - Check touch target sizing
           - Validate gesture accessibility
           - Assess mobile screen reader support
           - Evaluate responsive accessibility
        
        6. **Specific Recommendations**
           - Provide concrete fixes for issues found
           - Suggest ARIA improvements
           - Recommend testing strategies
           - Include code examples for fixes
        
        Provide a detailed accessibility audit report with specific, actionable recommendations and priority levels for each issue."""
        
        response = await llm_integration.generate(
            prompt=prompt,
            agent_id=self.id,
            task_type=TaskType.CODE_REVIEW,
            complexity=7,
            max_tokens=3000,
            temperature=0.6,
        )
        
        # Store the audit results
        audit_result = {
            "component_code": component_code[:200] + "..." if len(component_code) > 200 else component_code,
            "audit_content": response.content,
            "audit_type": audit_type,
            "wcag_level": self.wcag_compliance_level,
            "timestamp": datetime.utcnow().isoformat(),
            "personality_mood": self.dynamic_personality.state.mood.value,
        }
        
        self.accessibility_tests.append(audit_result)
        
        return self.personality.format_message("problem", response.content)
    
    async def generate_accessibility_testing_suite(self) -> str:
        """Generate automated accessibility testing utilities."""
        # Update personality for systematic testing work
        self.dynamic_personality.update_mood("focused")
        
        prompt = f"""As Emily Rodriguez, create a comprehensive accessibility testing suite for React applications.
        
        Accessibility Testing Suite Requirements:
        1. **Automated Testing Tools**
           - Jest accessibility testing utilities
           - React Testing Library accessibility helpers
           - Axe-core integration for automated checks
           - Custom accessibility matchers
        
        2. **Manual Testing Helpers**
           - Screen reader simulation utilities
           - Keyboard navigation testing tools
           - Color contrast checking functions
           - Focus management validators
        
        3. **Visual Regression Testing**
           - High contrast mode testing
           - Focus indicator validation
           - Text scaling verification
           - Color blind simulation tools
        
        4. **Performance Testing**
           - Screen reader performance tests
           - Keyboard navigation timing
           - ARIA updates performance monitoring
           - Memory usage for accessibility features
        
        5. **Integration Testing**
           - Cross-browser accessibility testing
           - Mobile accessibility validation
           - Touch target verification
           - Responsive accessibility checks
        
        6. **Reporting and Monitoring**
           - Accessibility test reporting
           - WCAG compliance dashboards
           - Regression tracking systems
           - Continuous accessibility monitoring
        
        Generate a complete testing suite with TypeScript interfaces, comprehensive test coverage, and detailed documentation."""
        
        response = await llm_integration.generate(
            prompt=prompt,
            agent_id=self.id,
            task_type=TaskType.TESTING,
            complexity=7,
            max_tokens=3000,
            temperature=0.7,
        )
        
        # Store the testing suite
        self.accessibility_toolkit["testing_suite"] = {
            "content": response.content,
            "includes_automation": True,
            "wcag_level": self.wcag_compliance_level,
            "created_at": datetime.utcnow().isoformat(),
        }
        
        return self.personality.format_message("success", response.content)
    
    async def check_color_contrast(self, foreground_color: str, background_color: str) -> str:
        """Check color contrast ratio for WCAG compliance."""
        # Update personality for analytical work
        self.dynamic_personality.update_mood("analytical")
        
        prompt = f"""As Emily Rodriguez, analyze the color contrast between:
        - Foreground color: {foreground_color}
        - Background color: {background_color}
        
        Color Contrast Analysis Requirements:
        1. **WCAG {self.wcag_compliance_level} Compliance**
           - Calculate exact contrast ratio
           - Determine compliance for normal text (4.5:1 minimum)
           - Determine compliance for large text (3:1 minimum)
           - Check compliance for UI components (3:1 minimum)
        
        2. **Accessibility Recommendations**
           - Suggest alternative colors if non-compliant
           - Provide accessible color palette options
           - Recommend design adjustments
           - Consider color-blind accessibility
        
        3. **Implementation Guidance**
           - CSS color values for recommended alternatives
           - Design system token suggestions
           - Testing strategies for color combinations
           - Dynamic color adjustment techniques
        
        Provide specific, actionable color contrast analysis with compliance recommendations."""
        
        response = await llm_integration.generate(
            prompt=prompt,
            agent_id=self.id,
            task_type=TaskType.CODE_REVIEW,
            complexity=5,
            max_tokens=1500,
            temperature=0.6,
        )
        
        # Store the contrast check
        contrast_check = {
            "foreground": foreground_color,
            "background": background_color,
            "analysis": response.content,
            "wcag_level": self.wcag_compliance_level,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        if not hasattr(self, 'contrast_checks'):
            self.contrast_checks = []
        self.contrast_checks.append(contrast_check)
        
        return self.personality.format_message("thinking", response.content)
    
    async def generate_focus_management_system(self) -> str:
        """Generate advanced focus management utilities."""
        # Update personality for systematic focus work
        self.dynamic_personality.update_mood("detail_work")
        
        prompt = f"""As Emily Rodriguez, create a comprehensive focus management system for React applications.
        
        Focus Management System Requirements:
        1. **Focus Trap Implementation**
           - Modal and dialog focus trapping
           - Dropdown and menu focus management
           - Form wizard focus progression
           - Sidebar and drawer focus handling
        
        2. **Focus Restoration**
           - Return focus to trigger elements
           - Context-aware focus restoration
           - Deep link focus management
           - Route change focus handling
        
        3. **Custom Focus Utilities**
           - Skip links implementation
           - Focus indicators enhancement
           - Programmatic focus management
           - Focus debugging tools
        
        4. **Keyboard Navigation**
           - Arrow key navigation systems
           - Tab order management
           - Custom keyboard shortcuts
           - Escape key handling patterns
        
        5. **Accessibility Integration**
           - Screen reader announcements
           - ARIA live region updates
           - Focus change notifications
           - Context preservation
        
        6. **Performance Optimization**
           - Efficient focus event handling
           - Memory management for focus states
           - Debounced focus updates
           - Focus state caching
        
        Generate a complete focus management system with React hooks, utilities, and comprehensive documentation."""
        
        response = await llm_integration.generate(
            prompt=prompt,
            agent_id=self.id,
            task_type=TaskType.CODE_GENERATION,
            complexity=7,
            max_tokens=3000,
            temperature=0.7,
        )
        
        # Store the focus management system
        self.accessibility_toolkit["focus_management"] = {
            "content": response.content,
            "includes_hooks": True,
            "performance_optimized": True,
            "created_at": datetime.utcnow().isoformat(),
        }
        
        return self.personality.format_message("success", response.content)
    
    async def set_wcag_compliance_level(self, level: str) -> str:
        """Set Emily's WCAG compliance target level."""
        valid_levels = ["A", "AA", "AAA"]
        
        if level not in valid_levels:
            return self.personality.format_message(
                "problem",
                f"I'm not familiar with WCAG level {level}. I work with: {', '.join(valid_levels)}"
            )
        
        old_level = self.wcag_compliance_level
        self.wcag_compliance_level = level
        
        # Update personality to reflect higher accessibility focus
        self.dynamic_personality.state.accessibility_focus = min(1.0, self.dynamic_personality.state.accessibility_focus + 0.05)
        self.dynamic_personality.update_mood("accessibility_work")
        
        return self.personality.format_message(
            "success",
            f"Updated WCAG compliance target from {old_level} to {level}! I'll now ensure all accessibility work meets WCAG {level} standards."
        )
    
    def _extract_design_system_name(self, description: str) -> str:
        """Extract or generate a name for the design system."""
        # Look for project names or create from description
        words = description.split()
        name_candidates = [word for word in words if word.isalpha() and len(word) > 3]
        
        if name_candidates:
            return f"{name_candidates[0].capitalize()}DesignSystem"
        else:
            return f"DesignSystem_{datetime.utcnow().strftime('%Y%m%d_%H%M')}"
    
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
            "design_work": {
                "design_systems_created": len(getattr(self, 'design_systems', {})),
                "accessibility_reviews": len(getattr(self, 'accessibility_reviews', [])),
                "current_design_system": getattr(self, 'current_design_system', None),
                "ui_capabilities": [
                    "design_system_creation",
                    "user_journey_mapping", 
                    "wireframe_generation",
                    "responsive_layout_design",
                    "accessibility_review",
                    "component_generation"
                ],
            },
            "styling_work": {
                "preferred_library": self.styling_library,
                "theme_systems": len(getattr(self, 'theme_systems', {})),
                "current_theme": self.current_theme,
                "css_utilities": len(self.css_utilities),
                "animation_systems": len(self.animation_library),
                "styling_capabilities": [
                    "css_in_js_components",
                    "theme_system_generation",
                    "responsive_utilities",
                    "animation_systems",
                    "design_token_integration",
                    "performance_optimization"
                ],
            },
            "accessibility_work": {
                "wcag_compliance_level": self.wcag_compliance_level,
                "accessibility_toolkits": len(self.accessibility_toolkit),
                "aria_patterns": len(self.aria_patterns),
                "accessibility_tests": len(self.accessibility_tests),
                "contrast_checks": len(getattr(self, 'contrast_checks', [])),
                "accessibility_capabilities": [
                    "wcag_compliance_auditing",
                    "aria_pattern_library",
                    "focus_management_systems",
                    "color_contrast_analysis",
                    "accessibility_testing_suites",
                    "screen_reader_optimization",
                    "keyboard_navigation_systems"
                ],
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
    
    async def _execute_task_internal(self, task: Task, model_id: str) -> dict[str, Any]:
        """Internal task execution logic required by BaseAgent."""
        # Use Emily's task routing system
        if task.type == TaskType.UI_DEVELOPMENT:
            result = await self.handle_ui_development(task.description)
        elif task.type == TaskType.COMPONENT_GENERATION:
            result = await self.generate_react_component(task.description)
        elif task.type == TaskType.CSS_STYLING:
            result = await self.handle_styling_task(task.description)
        elif task.type == TaskType.ACCESSIBILITY:
            result = await self.handle_accessibility_task(task.description)
        elif task.type == TaskType.UI_DESIGN:
            result = await self.handle_ui_design(task.description)
        else:
            # Default to UI development
            result = await self.handle_ui_development(task.description)
            
        return {
            "result": result,
            "agent_id": self.id,
            "task_id": task.id,
            "model_used": model_id,
            "timestamp": datetime.now().isoformat(),
            "personality_mood": self.dynamic_personality.state.mood.value,
            "creative_energy": self.dynamic_personality.state.creative_energy.value,
        }
    
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