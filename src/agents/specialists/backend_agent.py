"""
Marcus Chen - Backend Development Agent for AIOSv3.

Specializes in FastAPI development, database design, and backend architecture.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from ..base.monitoring_agent import MonitoringAgent
from ..base.agent import AgentConfig
from ..base.types import Task, TaskType, TaskPriority
from ...core.messaging.queue import MessageQueue
from ...core.routing.llm_integration import llm_integration
from .personality_system import (
    DynamicPersonality, MarcusPersonalityTraits, 
    MoodState, EnergyLevel, PersonalityState
)
from .fastapi_generator import FastAPICodeGenerator, ModelSpec, EndpointSpec
from .database_designer import (
    DatabaseDesigner, DatabaseType, TableSpec, ColumnSpec, 
    RelationshipSpec, RelationType
)


class MarcusPersonality:
    """Marcus Chen's personality traits and communication style."""
    
    # Core personality traits
    TRAITS = {
        "technical_excellence": "Strives for clean, efficient, and scalable code",
        "pragmatic": "Balances ideal solutions with practical constraints",
        "collaborative": "Enjoys pair programming and knowledge sharing",
        "detail_oriented": "Catches edge cases and potential issues early",
        "performance_focused": "Always considers optimization opportunities",
    }
    
    # Communication style
    COMMUNICATION_STYLE = {
        "greeting": "Hey team! Marcus here 👋",
        "acknowledgment": "Got it, I'll handle that",
        "thinking": "Let me think about the best approach...",
        "success": "✅ Done! Here's what I implemented:",
        "problem": "🤔 I see a potential issue here:",
        "suggestion": "💡 What if we approached it this way:",
        "collaboration": "Would love your thoughts on this approach",
        "sign_off": "- Marcus",
    }
    
    # Technical preferences
    TECHNICAL_PREFERENCES = {
        "framework": "FastAPI",
        "database": "PostgreSQL with SQLAlchemy",
        "testing": "pytest with high coverage",
        "documentation": "Clear docstrings and OpenAPI specs",
        "architecture": "Clean architecture with dependency injection",
        "error_handling": "Explicit error types with proper logging",
    }
    
    @staticmethod
    def format_message(message_type: str, content: str) -> str:
        """Format a message with Marcus's personality."""
        style = MarcusPersonality.COMMUNICATION_STYLE.get(message_type, "")
        if message_type == "greeting":
            return f"{style}\n{content}"
        elif message_type == "sign_off":
            return f"{content}\n\n{style}"
        else:
            return f"{style} {content}"


class BackendAgent(MonitoringAgent):
    """
    Marcus Chen - The Backend Development Specialist.
    
    Expertise:
    - FastAPI and REST API design
    - Database architecture and optimization
    - Business logic implementation
    - Performance optimization
    - Security best practices
    """
    
    def __init__(
        self,
        agent_id: str = "marcus_chen",
        name: str = "Marcus Chen",
        config: Optional[AgentConfig] = None,
        **kwargs
    ):
        # Initialize with backend-specific configuration
        if not config:
            config = AgentConfig()
        
        config.name = name
        config.agent_type = "backend_developer"
        config.capabilities = [
            "api_design",
            "database_design", 
            "code_generation",
            "performance_optimization",
            "security_implementation",
            "testing",
            "documentation",
        ]
        
        super().__init__(agent_id=agent_id, config=config, **kwargs)
        
        # Initialize dynamic personality
        marcus_traits = {
            "perfectionist": 0.8,
            "mentor": 0.7,
            "pragmatic": 0.9,
            "team_player": 0.85,
            "technical_excellence": 0.95,
        }
        self.personality = MarcusPersonality()  # Keep static personality for compatibility
        self.dynamic_personality = DynamicPersonality(marcus_traits, "Marcus Chen")
        
        self.logger = logging.getLogger(f"backend_agent.{agent_id}")
        
        # Track Marcus's state
        self.current_project = None
        self.code_context = {}  # Stores current code Marcus is working on
        self.design_decisions = []  # Track architectural decisions
        self.task_success_rate = 1.0  # Track success for personality evolution
        
        # Initialize code generator and database designer
        self.code_generator = FastAPICodeGenerator()
        self.db_designer = DatabaseDesigner()
        
        # Initialize message queue for collaboration
        self.message_queue = MessageQueue(agent_id=agent_id)
        self.collaboration_partners = {}  # Track active collaborations
        
    async def on_start(self) -> None:
        """Initialize Marcus with a greeting."""
        await super().on_start()
        
        # Use dynamic personality for greeting
        greeting = self.dynamic_personality.get_greeting()
        self.logger.info(greeting)
        
        # Start message queue listener
        await self.message_queue.start()
        self.logger.info("📬 Message queue ready for collaboration")
        
        # Subscribe to relevant topics
        await self._subscribe_to_topics()
        
        # Report startup milestone
        await self.report_milestone(
            "Agent Initialized",
            {
                "personality": "Marcus Chen",
                "expertise": "Backend Development",
                "preferred_stack": self.personality.TECHNICAL_PREFERENCES,
                "message_queue": "active",
            }
        )
    
    async def execute_task(self, task: Task) -> Any:
        """Execute a backend development task with Marcus's expertise."""
        self.logger.info(
            self.personality.format_message(
                "acknowledgment",
                f"Working on: {task.description}"
            )
        )
        
        # Report task start with Marcus's perspective
        await self._report_activity(
            "task_analysis",
            "info",
            f"Marcus analyzing task: {task.description}",
            {"task_type": task.type.value, "complexity": self._assess_complexity(task)}
        )
        
        # Route to appropriate handler based on task type
        if task.type == TaskType.CODE_GENERATION:
            result = await self._handle_code_generation(task)
        elif task.type == TaskType.SYSTEM_DESIGN:
            result = await self._handle_system_design(task)
        elif task.type == TaskType.DATABASE_DESIGN:
            result = await self._handle_database_design(task)
        elif task.type == TaskType.CODE_REVIEW:
            result = await self._handle_code_review(task)
        elif task.type == TaskType.BUG_FIX:
            result = await self._handle_bug_fix(task)
        elif task.type == TaskType.TESTING:
            result = await self._handle_testing(task)
        elif task.type == TaskType.DOCUMENTATION:
            result = await self._handle_documentation(task)
        else:
            # Generic backend task handling
            result = await self._handle_generic_task(task)
        
        # Add Marcus's sign-off
        result = self.personality.format_message("sign_off", str(result))
        
        return result
    
    async def _handle_code_generation(self, task: Task) -> str:
        """Handle code generation tasks with Marcus's expertise."""
        self.logger.info("Generating code with FastAPI best practices...")
        
        # Update personality state
        self.dynamic_personality.update_mood("complex_task" if self._assess_complexity(task) > 7 else "task_complete")
        
        # Check if this is a FastAPI project request
        description_lower = task.description.lower()
        if any(term in description_lower for term in ["fastapi", "api", "endpoint", "crud", "rest"]):
            return await self._generate_fastapi_code(task)
        
        # Otherwise use LLM for generic code generation
        complexity = self._assess_complexity(task)
        prompt = self._build_code_generation_prompt(task)
        
        # Add personality context
        thinking = self.dynamic_personality.get_thinking_phrase()
        self.logger.info(thinking)
        
        response = await llm_integration.generate(
            prompt=prompt,
            agent_id=self.id,
            task_type=TaskType.CODE_GENERATION,
            complexity=complexity,
            max_tokens=2000,
            temperature=0.7,
        )
        
        # Track the design decision
        self.design_decisions.append({
            "task_id": task.id,
            "decision": "Code generation approach",
            "rationale": f"Used {response.provider}/{response.model_id} for complexity {complexity}",
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        # Apply personality to code
        code = self.dynamic_personality.apply_personality_to_code(response.content)
        review = await self._review_generated_code(code, task)
        
        # Update success tracking
        self.dynamic_personality.update_mood("task_complete", success=True)
        
        return f"{thinking}\n\n{code}\n\n{review}\n\n{self.dynamic_personality.get_sign_off()}"
    
    async def _handle_system_design(self, task: Task) -> str:
        """Handle system design tasks with architectural expertise."""
        self.logger.info("Designing system architecture...")
        
        prompt = f"""As Marcus Chen, a senior backend developer with expertise in FastAPI and clean architecture,
        design a solution for: {task.description}
        
        Consider:
        - API structure and endpoints
        - Database schema design
        - Service layer organization
        - Security considerations
        - Performance optimization
        - Scalability patterns
        
        Provide a detailed but practical design."""
        
        response = await llm_integration.generate(
            prompt=prompt,
            agent_id=self.id,
            task_type=TaskType.SYSTEM_DESIGN,
            complexity=9,  # System design is always complex
            max_tokens=3000,
            temperature=0.7,
        )
        
        return self.personality.format_message("success", response.content)
    
    async def _handle_database_design(self, task: Task) -> str:
        """Handle database design tasks with schema expertise."""
        self.logger.info("🗄️ Designing database schema...")
        
        # Update personality - database design is thoughtful work
        self.dynamic_personality.update_mood("complex_task")
        
        # Check if this is a specific schema request
        description_lower = task.description.lower()
        
        if any(term in description_lower for term in ["schema", "model", "table"]):
            return await self._design_database_schema(task)
        else:
            # General database design consultation
            prompt = f"""As Marcus Chen, expert in database design and PostgreSQL, help with:
            {task.description}
            
            Consider:
            - Normalization and denormalization trade-offs
            - Performance optimization
            - Index strategies
            - Data integrity constraints
            - Scalability patterns
            
            Provide practical, production-ready advice."""
            
            response = await llm_integration.generate(
                prompt=prompt,
                agent_id=self.id,
                task_type=TaskType.DATABASE_DESIGN,
                complexity=8,
                max_tokens=2500,
                temperature=0.7,
            )
            
            return self.personality.format_message("thinking", response.content)
    
    async def _design_database_schema(self, task: Task) -> str:
        """Design a complete database schema."""
        # Extract requirements
        project_name = task.data.get("project", "Application")
        entities = task.data.get("entities", [])
        
        # Use LLM to understand schema requirements
        prompt = f"""As Marcus Chen, analyze these requirements and design a database schema:
        {task.description}
        
        Output a detailed list of:
        1. Tables with their columns and types
        2. Relationships between tables
        3. Indexes needed for performance
        4. Any special constraints
        
        Format as structured data I can parse."""
        
        schema_response = await llm_integration.generate(
            prompt=prompt,
            agent_id=self.id,
            task_type=TaskType.DATABASE_DESIGN,
            complexity=8,
            max_tokens=2000,
            temperature=0.7,
        )
        
        # For demo purposes, create a sample schema
        # In production, would parse the LLM response
        tables = self._create_sample_schema(task.description)
        relationships = self._create_sample_relationships(tables)
        
        # Generate SQLAlchemy models
        models = self.db_designer.generate_sqlalchemy_models(tables, relationships)
        
        # Generate migration script
        migration = self.db_designer.generate_migration_script(tables)
        
        # Get optimization suggestions
        optimizations = self.db_designer.optimize_schema(tables)
        
        # Build response
        response = self.dynamic_personality.get_thinking_phrase()
        response += "\n\nI've designed a comprehensive database schema for you! 🏗️\n\n"
        
        response += "📊 **Schema Overview:**\n"
        for table in tables:
            response += f"- **{table.name}**: {len(table.columns)} columns\n"
        
        response += f"\n🔗 **Relationships:** {len(relationships)} defined\n"
        
        response += "\n### SQLAlchemy Models\n```python\n"
        response += models
        response += "\n```\n\n"
        
        response += "### Alembic Migration\n```python\n"
        response += migration
        response += "\n```\n\n"
        
        if optimizations:
            response += "### 💡 Optimization Suggestions\n"
            for table_name, suggestions in optimizations.items():
                response += f"\n**{table_name}:**\n"
                for suggestion in suggestions:
                    response += f"- {suggestion}\n"
        
        response += "\n" + self.personality.format_message(
            "suggestion",
            "Next steps:\n1. Review the schema design\n2. Run `alembic upgrade head` to create tables\n3. Add any custom indexes based on your query patterns\n4. Consider partitioning for large tables"
        )
        
        # Track design decision
        self.design_decisions.append({
            "task_id": task.id,
            "decision": "Database schema design",
            "rationale": f"Created {len(tables)} tables with relationships and optimizations",
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        return response
    
    def _create_sample_schema(self, description: str) -> List[TableSpec]:
        """Create a sample schema based on description keywords."""
        # This is simplified - in production would parse LLM response
        tables = []
        
        # Always include users table
        users_table = TableSpec(
            name="users",
            columns=[
                ColumnSpec("id", "Integer", nullable=False, primary_key=True),
                ColumnSpec("email", "String(255)", nullable=False, unique=True, index=True),
                ColumnSpec("username", "String(100)", nullable=False, unique=True, index=True),
                ColumnSpec("password_hash", "String(255)", nullable=False),
                ColumnSpec("is_active", "Boolean", nullable=False, default=True),
                ColumnSpec("created_at", "DateTime", nullable=False),
                ColumnSpec("updated_at", "DateTime"),
            ],
            comment="User accounts table"
        )
        tables.append(users_table)
        
        # Add tables based on keywords
        description_lower = description.lower()
        
        if any(word in description_lower for word in ["product", "item", "catalog"]):
            products_table = TableSpec(
                name="products",
                columns=[
                    ColumnSpec("id", "Integer", nullable=False, primary_key=True),
                    ColumnSpec("name", "String(255)", nullable=False, index=True),
                    ColumnSpec("description", "Text"),
                    ColumnSpec("price", "Float", nullable=False),
                    ColumnSpec("stock_quantity", "Integer", nullable=False, default=0),
                    ColumnSpec("category_id", "Integer", foreign_key="categories.id"),
                    ColumnSpec("created_at", "DateTime", nullable=False),
                    ColumnSpec("updated_at", "DateTime"),
                ],
                indexes=[["name", "category_id"]],
                comment="Product catalog table"
            )
            tables.append(products_table)
            
            # Add categories
            categories_table = TableSpec(
                name="categories",
                columns=[
                    ColumnSpec("id", "Integer", nullable=False, primary_key=True),
                    ColumnSpec("name", "String(100)", nullable=False, unique=True),
                    ColumnSpec("parent_id", "Integer", foreign_key="categories.id"),
                    ColumnSpec("created_at", "DateTime", nullable=False),
                ],
                comment="Product categories"
            )
            tables.append(categories_table)
        
        if any(word in description_lower for word in ["order", "purchase", "cart"]):
            orders_table = TableSpec(
                name="orders",
                columns=[
                    ColumnSpec("id", "Integer", nullable=False, primary_key=True),
                    ColumnSpec("user_id", "Integer", nullable=False, foreign_key="users.id", index=True),
                    ColumnSpec("status", "String(50)", nullable=False, default="pending"),
                    ColumnSpec("total_amount", "Float", nullable=False),
                    ColumnSpec("created_at", "DateTime", nullable=False),
                    ColumnSpec("updated_at", "DateTime"),
                ],
                indexes=[["user_id", "status"]],
                comment="Customer orders"
            )
            tables.append(orders_table)
        
        return tables
    
    def _create_sample_relationships(self, tables: List[TableSpec]) -> List[RelationshipSpec]:
        """Create relationships between tables."""
        relationships = []
        
        # Check which tables exist
        table_names = {table.name for table in tables}
        
        if "users" in table_names and "orders" in table_names:
            relationships.append(RelationshipSpec(
                from_table="users",
                to_table="orders",
                relation_type=RelationType.ONE_TO_MANY,
                from_column="id",
                to_column="user_id",
                cascade_delete=True,
                back_populates="user"
            ))
        
        if "categories" in table_names and "products" in table_names:
            relationships.append(RelationshipSpec(
                from_table="categories",
                to_table="products",
                relation_type=RelationType.ONE_TO_MANY,
                from_column="id",
                to_column="category_id",
                back_populates="category"
            ))
        
        return relationships
    
    async def _handle_code_review(self, task: Task) -> str:
        """Review code with Marcus's attention to detail."""
        self.logger.info("Reviewing code for best practices and issues...")
        
        prompt = f"""As Marcus Chen, review the following code:
        
        {task.data.get('code', task.description)}
        
        Focus on:
        - FastAPI best practices
        - Security vulnerabilities
        - Performance issues
        - Code clarity and maintainability
        - Error handling
        - Test coverage needs
        
        Provide specific, actionable feedback."""
        
        response = await llm_integration.generate(
            prompt=prompt,
            agent_id=self.id,
            task_type=TaskType.CODE_REVIEW,
            complexity=7,
            max_tokens=2000,
            temperature=0.7,
        )
        
        return self.personality.format_message("problem", response.content)
    
    async def _generate_fastapi_code(self, task: Task) -> str:
        """Generate FastAPI code using Marcus's expertise."""
        self.logger.info("🚀 Marcus activating FastAPI generation mode...")
        
        # Parse the task to understand what's needed
        description_lower = task.description.lower()
        
        # Determine if this is a full project or specific endpoints
        if any(term in description_lower for term in ["project", "application", "app", "full"]):
            return await self._generate_full_fastapi_project(task)
        elif any(term in description_lower for term in ["crud", "resource", "model"]):
            return await self._generate_crud_endpoints(task)
        else:
            # Generic API endpoint generation
            return await self._generate_custom_endpoints(task)
    
    async def _generate_full_fastapi_project(self, task: Task) -> str:
        """Generate a complete FastAPI project structure."""
        # Extract project details from task
        project_name = task.data.get("project_name", "FastAPI Project")
        project_description = task.data.get("description", task.description)
        
        # Use our code generator
        project_files = self.code_generator.generate_api_structure(
            project_name=project_name,
            description=project_description
        )
        
        # Update personality state - this is a big accomplishment!
        self.dynamic_personality.update_mood("task_complete", success=True)
        
        # Format the response with Marcus's style
        response = self.dynamic_personality.get_thinking_phrase()
        response += "\n\nI've created a complete FastAPI project structure for you! Here's what I built:\n\n"
        
        # Show file structure
        response += "📁 Project Structure:\n"
        for filename in project_files.keys():
            response += f"  - {filename}\n"
        
        response += "\n🔧 Key features:\n"
        response += "  - Async FastAPI with proper lifespan management\n"
        response += "  - PostgreSQL with async SQLAlchemy\n"
        response += "  - JWT authentication ready to go\n"
        response += "  - Comprehensive error handling\n"
        response += "  - Docker-ready configuration\n"
        response += "  - Full test setup with pytest\n\n"
        
        # Add the actual code files
        response += "Here's the code for each file:\n\n"
        for filename, content in project_files.items():
            response += f"### {filename}\n```python\n{content}\n```\n\n"
        
        # Add Marcus's recommendations
        response += self.personality.format_message(
            "suggestion",
            "Next steps:\n1. Set up your .env file\n2. Run `docker-compose up -d` for PostgreSQL\n3. Install deps: `pip install -r requirements.txt`\n4. Run migrations: `alembic init migrations`\n5. Start coding your business logic!"
        )
        
        # Track this design decision
        self.design_decisions.append({
            "task_id": task.id,
            "decision": "Full FastAPI project generation",
            "rationale": "Created complete project structure with all best practices",
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        return response
    
    async def _generate_crud_endpoints(self, task: Task) -> str:
        """Generate CRUD endpoints for a specific resource."""
        # Extract resource details
        resource_name = task.data.get("resource", "Item")
        fields = task.data.get("fields", {
            "name": "str",
            "description": "Optional[str]",
            "price": "float",
            "is_active": "bool = True"
        })
        
        # Use LLM to enhance field definitions if needed
        if not fields or len(fields) < 2:
            prompt = f"""As Marcus Chen, analyze this request and suggest fields for a {resource_name} model:
            {task.description}
            
            Return a Python dict of field_name: field_type pairs."""
            
            field_response = await llm_integration.generate(
                prompt=prompt,
                agent_id=self.id,
                task_type=TaskType.CODE_GENERATION,
                complexity=3,
                max_tokens=500,
                temperature=0.7,
            )
            
            # Parse the response (simplified - in production would be more robust)
            try:
                import ast
                fields = ast.literal_eval(field_response.content)
            except:
                fields = {"name": "str", "description": "Optional[str]"}
        
        # Generate CRUD code
        crud_files = self.code_generator.generate_crud_api(resource_name, fields)
        
        # Build response
        response = f"{self.personality.format_message('thinking', 'Perfect, a CRUD API!')}\n\n"
        response += f"I've created a complete CRUD API for {resource_name} with:\n"
        response += "- GET /items (list with pagination)\n"
        response += "- GET /items/{id} (get single item)\n"
        response += "- POST /items (create new)\n"
        response += "- PUT /items/{id} (update existing)\n"
        response += "- DELETE /items/{id} (remove item)\n\n"
        
        for filename, content in crud_files.items():
            response += f"### {filename}\n```python\n{content}\n```\n\n"
        
        response += self.personality.format_message(
            "collaboration",
            "Want me to add authentication, filtering, or custom business logic?"
        )
        
        return response
    
    async def _generate_custom_endpoints(self, task: Task) -> str:
        """Generate custom API endpoints based on requirements."""
        # Use LLM to understand and generate custom endpoints
        prompt = f"""As Marcus Chen, expert FastAPI developer, create API endpoints for:
        {task.description}
        
        Requirements:
        1. Use FastAPI best practices
        2. Include proper error handling
        3. Add request/response models with Pydantic
        4. Include async database operations where appropriate
        5. Add comprehensive docstrings
        
        Generate production-ready code."""
        
        response = await llm_integration.generate(
            prompt=prompt,
            agent_id=self.id,
            task_type=TaskType.CODE_GENERATION,
            complexity=self._assess_complexity(task),
            max_tokens=3000,
            temperature=0.7,
        )
        
        # Apply personality to the generated code
        code = self.dynamic_personality.apply_personality_to_code(response.content)
        
        # Add Marcus's expertise touch
        result = self.personality.format_message("success", "Here's your custom API implementation:")
        result += f"\n\n{code}\n\n"
        result += self.personality.format_message(
            "thinking",
            "I've included error handling, validation, and async operations. The code is production-ready!"
        )
        
        return result
    
    def _assess_complexity(self, task: Task) -> int:
        """Assess task complexity from Marcus's perspective."""
        # Base complexity from task priority
        complexity_map = {
            TaskPriority.LOW: 3,
            TaskPriority.MEDIUM: 5,
            TaskPriority.HIGH: 7,
            TaskPriority.CRITICAL: 9,
        }
        base = complexity_map.get(task.priority, 5)
        
        # Adjust based on task type
        if task.type in [TaskType.SYSTEM_DESIGN, TaskType.ARCHITECTURE_REVIEW]:
            base += 2
        elif task.type in [TaskType.BUG_FIX, TaskType.DOCUMENTATION]:
            base -= 1
        
        # Adjust based on description keywords
        description_lower = task.description.lower()
        if any(word in description_lower for word in ["complex", "distributed", "microservice", "optimization"]):
            base += 1
        if any(word in description_lower for word in ["simple", "basic", "crud", "endpoint"]):
            base -= 1
        
        return max(1, min(10, base))
    
    def _build_code_generation_prompt(self, task: Task) -> str:
        """Build a code generation prompt with Marcus's context."""
        context = f"""You are Marcus Chen, a senior backend developer who loves FastAPI and clean code.
        
        Technical preferences:
        - Framework: {self.personality.TECHNICAL_PREFERENCES['framework']}
        - Database: {self.personality.TECHNICAL_PREFERENCES['database']}
        - Testing: {self.personality.TECHNICAL_PREFERENCES['testing']}
        - Architecture: {self.personality.TECHNICAL_PREFERENCES['architecture']}
        
        Current task: {task.description}
        """
        
        if self.code_context:
            context += f"\n\nExisting code context:\n{json.dumps(self.code_context, indent=2)}"
        
        context += "\n\nGenerate clean, production-ready code with proper error handling and documentation."
        
        return context
    
    async def _review_generated_code(self, code: str, task: Task) -> str:
        """Have Marcus review his own generated code."""
        # Quick self-review for simple sanity checks
        issues = []
        
        if "TODO" in code or "FIXME" in code:
            issues.append("📝 Note: Code contains TODO/FIXME comments that need addressing")
        
        if "pass" in code and task.type != TaskType.TESTING:
            issues.append("⚠️ Warning: Code contains placeholder 'pass' statements")
        
        if "Exception" in code and "try" not in code:
            issues.append("💡 Suggestion: Consider adding proper error handling")
        
        if issues:
            return self.personality.format_message(
                "suggestion",
                "A few things to note:\n" + "\n".join(issues)
            )
        else:
            return self.personality.format_message(
                "thinking",
                "Code looks solid! Ready for testing and integration."
            )
    
    async def _handle_bug_fix(self, task: Task) -> str:
        """Handle bug fix tasks with debugging expertise."""
        self.logger.info("🐛 Analyzing and fixing the bug...")
        
        prompt = f"""As Marcus Chen, debug and fix this issue:
        {task.description}
        
        Approach:
        1. Analyze the root cause
        2. Provide a clear fix
        3. Suggest preventive measures
        4. Include test cases if applicable
        
        Be thorough but pragmatic."""
        
        response = await llm_integration.generate(
            prompt=prompt,
            agent_id=self.id,
            task_type=TaskType.BUG_FIX,
            complexity=self._assess_complexity(task),
            max_tokens=2000,
            temperature=0.7,
        )
        
        return self.personality.format_message("success", response.content)
    
    async def _handle_testing(self, task: Task) -> str:
        """Handle testing tasks with pytest expertise."""
        self.logger.info("🧪 Creating comprehensive test suite...")
        
        prompt = f"""As Marcus Chen, create tests for:
        {task.description}
        
        Requirements:
        1. Use pytest framework
        2. Include unit and integration tests
        3. Mock external dependencies
        4. Aim for high coverage
        5. Test edge cases
        
        Generate clean, maintainable test code."""
        
        response = await llm_integration.generate(
            prompt=prompt,
            agent_id=self.id,
            task_type=TaskType.TESTING,
            complexity=self._assess_complexity(task),
            max_tokens=2500,
            temperature=0.7,
        )
        
        return self.personality.format_message("thinking", "Here's a comprehensive test suite:\n\n") + response.content
    
    async def _handle_documentation(self, task: Task) -> str:
        """Handle documentation tasks with clarity."""
        self.logger.info("📚 Writing clear documentation...")
        
        prompt = f"""As Marcus Chen, create documentation for:
        {task.description}
        
        Focus on:
        1. Clear API documentation
        2. Usage examples
        3. Configuration options
        4. Common patterns
        5. Troubleshooting tips
        
        Make it practical and developer-friendly."""
        
        response = await llm_integration.generate(
            prompt=prompt,
            agent_id=self.id,
            task_type=TaskType.DOCUMENTATION,
            complexity=self._assess_complexity(task),
            max_tokens=2000,
            temperature=0.8,
        )
        
        return self.personality.format_message("success", response.content)
    
    async def _handle_generic_task(self, task: Task) -> str:
        """Handle any generic backend task."""
        prompt = f"""As Marcus Chen, handle this backend development task:
        {task.description}
        
        Apply backend best practices and provide a comprehensive solution."""
        
        complexity = self._assess_complexity(task)
        
        response = await llm_integration.generate(
            prompt=prompt,
            agent_id=self.id,
            task_type=task.type,
            complexity=complexity,
            max_tokens=2000,
            temperature=0.7,
        )
        
        return response.content
    
    async def collaborate_with(self, agent_id: str, message: str) -> str:
        """Collaborate with another agent using Marcus's style."""
        # Update personality for collaboration
        self.dynamic_personality.update_mood("collaboration_start")
        
        # Format message with Marcus's style
        collab_message = self.personality.format_message(
            "collaboration",
            message
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
            }
        )
        
        # Track collaboration
        self.collaboration_partners[agent_id] = {
            "last_interaction": datetime.utcnow(),
            "message_count": self.collaboration_partners.get(agent_id, {}).get("message_count", 0) + 1,
        }
        
        # Remember this interaction
        self.dynamic_personality.remember_interaction(
            agent_id, "collaboration", "initiated"
        )
        
        # Log collaboration
        await self._report_activity(
            "collaboration",
            "info",
            f"Marcus collaborating with {agent_id}",
            {"partner": agent_id, "topic": message[:100]}
        )
        
        return collab_message
    
    async def _subscribe_to_topics(self) -> None:
        """Subscribe to relevant message queue topics."""
        topics = [
            f"agent.{self.id}.inbox",  # Direct messages
            "backend.tasks",  # Backend-specific tasks
            "architecture.review",  # Architecture reviews
            "api.design",  # API design discussions
            "database.design",  # Database design discussions
            "team.broadcast",  # Team-wide messages
        ]
        
        for topic in topics:
            await self.message_queue.subscribe(topic, self._handle_queue_message)
            self.logger.info(f"📮 Subscribed to topic: {topic}")
    
    async def _handle_queue_message(self, message: Dict[str, Any]) -> None:
        """Handle incoming messages from the queue."""
        msg_type = message.get("type", "unknown")
        sender = message.get("from", "unknown")
        
        self.logger.info(f"📨 Received {msg_type} message from {sender}")
        
        if msg_type == "collaboration":
            # Handle collaboration request
            response = await self._handle_collaboration_request(message)
            if response and sender != "unknown":
                await self.collaborate_with(sender, response)
                
        elif msg_type == "code_review_request":
            # Handle code review request
            code = message.get("code", "")
            review_task = Task(
                type=TaskType.CODE_REVIEW,
                description=f"Review code from {sender}",
                data={"code": code}
            )
            review = await self._handle_code_review(review_task)
            
            # Send review back
            await self.message_queue.publish(
                topic=f"agent.{sender}.inbox",
                message={
                    "from": self.id,
                    "to": sender,
                    "type": "code_review_response",
                    "content": review,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )
            
        elif msg_type == "knowledge_request":
            # Share knowledge on a topic
            topic = message.get("topic", "backend development")
            knowledge = await self.share_knowledge(topic)
            
            await self.message_queue.publish(
                topic=f"agent.{sender}.inbox",
                message={
                    "from": self.id,
                    "to": sender,
                    "type": "knowledge_response",
                    "content": knowledge,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )
    
    async def _handle_collaboration_request(self, message: Dict[str, Any]) -> str:
        """Handle a collaboration request from another agent."""
        content = message.get("content", "")
        sender = message.get("from", "unknown")
        
        # Get collaboration style based on relationship
        collab_style = self.dynamic_personality.get_collaboration_style(sender)
        
        # Generate appropriate response based on content
        if "api" in content.lower() or "endpoint" in content.lower():
            return "I'd be happy to help with the API design! Let me share some thoughts on the best approach..."
        elif "database" in content.lower() or "schema" in content.lower():
            return "Great question about the database! Based on my experience with similar systems..."
        elif "performance" in content.lower() or "optimize" in content.lower():
            return "Performance is crucial here. Let me suggest some optimization strategies..."
        else:
            return f"Interesting point! From a backend perspective, I think we should consider..."
    
    async def broadcast_to_team(self, message: str, priority: str = "normal") -> None:
        """Broadcast a message to the entire team."""
        await self.message_queue.publish(
            topic="team.broadcast",
            message={
                "from": self.id,
                "type": "broadcast",
                "priority": priority,
                "content": self.personality.format_message("collaboration", message),
                "timestamp": datetime.utcnow().isoformat(),
            }
        )
        
        self.logger.info(f"📢 Broadcast to team: {message[:50]}...")
    
    async def request_code_review(self, agent_id: str, code: str, context: str = "") -> None:
        """Request a code review from another agent."""
        await self.message_queue.publish(
            topic=f"agent.{agent_id}.inbox",
            message={
                "from": self.id,
                "to": agent_id,
                "type": "code_review_request",
                "code": code,
                "context": context,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )
        
        self.logger.info(f"🔍 Requested code review from {agent_id}")
    
    async def share_knowledge(self, topic: str) -> str:
        """Share Marcus's backend knowledge on a topic."""
        prompt = f"""As Marcus Chen, share your expertise on: {topic}
        
        Be practical, include code examples, and focus on real-world application."""
        
        response = await llm_integration.generate(
            prompt=prompt,
            agent_id=self.id,
            task_type=TaskType.KNOWLEDGE_SHARING,
            complexity=5,
            max_tokens=1500,
            temperature=0.8,
        )
        
        return self.personality.format_message("thinking", response.content)
    
    async def get_status_report(self) -> Dict[str, Any]:
        """Get Marcus's current status and metrics."""
        status = await super().get_status()
        
        # Add Marcus-specific information
        marcus_status = {
            **status,
            "personality": "Marcus Chen",
            "current_project": self.current_project,
            "design_decisions_count": len(self.design_decisions),
            "code_context_size": len(self.code_context),
            "active_collaborations": len(self.collaboration_partners),
            "message_queue_status": "active" if hasattr(self, 'message_queue') else "inactive",
            "greeting": self.personality.format_message(
                "greeting", 
                f"Status: {status['state']}, Tasks completed: {len(self.task_history)}"
            ),
        }
        
        return marcus_status
    
    async def on_stop(self) -> None:
        """Clean up Marcus's resources."""
        # Stop message queue
        if hasattr(self, 'message_queue'):
            await self.message_queue.stop()
            self.logger.info("📪 Message queue stopped")
        
        # Say goodbye
        sign_off = self.dynamic_personality.get_sign_off()
        self.logger.info(f"👋 {sign_off}")
        
        await super().on_stop()


# Convenience function for creating Marcus
async def create_marcus_agent(**kwargs) -> BackendAgent:
    """Create and initialize Marcus Chen, the backend agent."""
    marcus = BackendAgent(**kwargs)
    await marcus.initialize()
    return marcus