#!/usr/bin/env python3
"""
Collaborative Agent - Enhanced BaseAgent with Multi-Terminal Collaboration

This bridges the Enhanced BaseAgent framework with real-time collaboration,
enabling multiple Claude Code instances to work together on the same repository.
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
import websockets

from src.agents.base.enhanced_agent import EnhancedBaseAgent, EnhancedAgentConfig, EnhancedTask, EnhancedTaskResult
from src.agents.base.types import TaskType, AgentType
from src.core.routing.router import LLMRouter, RoutingPolicy, RoutingStrategy
from src.core.routing.providers.claude import ClaudeProvider, ClaudeConfig

logger = logging.getLogger(__name__)


class CollaborativeAgentConfig(EnhancedAgentConfig):
    """Configuration for collaborative agents."""
    collaboration_server: str = "ws://localhost:8765"
    role: str
    
    def __init__(self, role: str, collaboration_server: str = "ws://localhost:8765", **kwargs):
        # Set defaults based on role
        defaults = self._get_role_defaults(role)
        defaults.update(kwargs)
        defaults['role'] = role
        defaults['collaboration_server'] = collaboration_server
        
        super().__init__(**defaults)
    
    def _get_role_defaults(self, role: str) -> Dict[str, Any]:
        """Get default configuration based on agent role."""
        role_configs = {
            "cto": {
                "agent_type": AgentType.CTO,
                "name": "CTO Agent",
                "description": "Chief Technology Officer for technical leadership and architectural decisions",
                "default_routing_strategy": RoutingStrategy.PERFORMANCE_OPTIMIZED,
                "temperature": 0.3,
                "max_tokens": 4096
            },
            "backend-dev": {
                "agent_type": AgentType.BACKEND_DEV,
                "name": "Backend Developer",
                "description": "Backend developer specializing in server-side implementation",
                "default_routing_strategy": RoutingStrategy.COST_OPTIMIZED,
                "temperature": 0.4,
                "max_tokens": 3072
            },
            "qa": {
                "agent_type": AgentType.QA_ENGINEER,
                "name": "QA Engineer", 
                "description": "Quality assurance engineer for testing and validation",
                "default_routing_strategy": RoutingStrategy.BALANCED,
                "temperature": 0.2,
                "max_tokens": 2048
            },
            "human": {
                "agent_type": AgentType.GENERALIST,
                "name": "Product Owner",
                "description": "Human product owner and project coordinator",
                "default_routing_strategy": RoutingStrategy.COST_OPTIMIZED,
                "temperature": 0.7,
                "max_tokens": 1024
            }
        }
        
        return role_configs.get(role, {
            "agent_type": AgentType.GENERALIST,
            "name": f"{role.title()} Agent",
            "description": f"Specialized agent for {role} tasks",
            "default_routing_strategy": RoutingStrategy.BALANCED,
            "temperature": 0.5,
            "max_tokens": 2048
        })


class CollaborativeAgent(EnhancedBaseAgent):
    """
    Enhanced BaseAgent with multi-terminal collaboration capabilities.
    
    This agent can:
    - Connect to collaboration server for real-time coordination
    - Receive task assignments from orchestrator
    - Share context and status with other agents
    - Execute tasks using Enhanced BaseAgent framework
    """
    
    def __init__(self, config: CollaborativeAgentConfig, llm_router: Optional[LLMRouter] = None):
        super().__init__(config)
        
        self.collab_config = config
        self.role = config.role
        self.collaboration_server = config.collaboration_server
        
        # Collaboration state
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.connected = False
        self.collaborators: Dict[str, Any] = {}
        self.assigned_tasks: List[Dict[str, Any]] = []
        self.current_assignment: Optional[Dict[str, Any]] = None
        
        # Use provided router or create default
        if llm_router:
            self.router = llm_router
    
    async def _on_initialize(self) -> None:
        """Initialize collaborative agent."""
        # Connect to collaboration server
        await self.connect_to_collaboration()
        
        # Role-specific initialization
        await self._initialize_role_specific()
        
        # Start collaboration tasks
        asyncio.create_task(self._collaboration_loop())
    
    async def _on_shutdown(self) -> None:
        """Shutdown collaborative agent."""
        if self.websocket and self.connected:
            await self.send_collaboration_message({
                "type": "status_update",
                "from_id": self.agent_id,
                "status": "shutting_down"
            })
            await self.websocket.close()
    
    async def connect_to_collaboration(self):
        """Connect to the collaboration server."""
        try:
            logger.info(f"Connecting to collaboration server: {self.collaboration_server}")
            self.websocket = await websockets.connect(self.collaboration_server)
            self.connected = True
            
            # Register with server
            await self.send_collaboration_message({
                "type": "register",
                "id": self.agent_id,
                "role": self.role,
                "name": self.config.name,
                "terminal_id": str(uuid.uuid4()),
                "capabilities": [cap.value for cap in self.config.capabilities] if hasattr(self.config, 'capabilities') else []
            })
            
            logger.info(f"✅ Connected as: {self.config.name} ({self.role})")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to collaboration server: {e}")
            self.connected = False
    
    async def send_collaboration_message(self, data: Dict[str, Any]):
        """Send message to collaboration server."""
        if self.websocket and self.connected:
            try:
                await self.websocket.send(json.dumps(data))
            except Exception as e:
                logger.error(f"Failed to send collaboration message: {e}")
                self.connected = False
    
    async def _collaboration_loop(self):
        """Main collaboration loop - listen for messages and tasks."""
        if not self.connected:
            return
        
        try:
            async for message_str in self.websocket:
                try:
                    data = json.loads(message_str)
                    await self._handle_collaboration_message(data)
                except json.JSONDecodeError:
                    logger.error("Received invalid JSON from collaboration server")
                except Exception as e:
                    logger.error(f"Error handling collaboration message: {e}")
        
        except websockets.exceptions.ConnectionClosed:
            self.connected = False
            logger.warning("🔌 Disconnected from collaboration server")
    
    async def _handle_collaboration_message(self, data: Dict[str, Any]):
        """Handle messages from collaboration server."""
        message_type = data.get("type")
        
        if message_type == "welcome":
            logger.info(f"📡 {data.get('message')}")
        
        elif message_type == "sync_state":
            self.collaborators = data.get("collaborators", {})
            recent_messages = data.get("recent_messages", [])
            logger.info(f"🔄 Synced with {len(self.collaborators)} collaborators")
        
        elif message_type == "new_message":
            await self._handle_team_message(data)
        
        elif message_type == "task_assignment":
            await self._handle_task_assignment(data)
        
        elif message_type == "task_updated":
            await self._handle_task_update(data)
        
        elif message_type == "collaborator_joined":
            collaborator = data.get("collaborator", {})
            logger.info(f"✅ {collaborator.get('name')} ({collaborator.get('role')}) joined the team")
        
        elif message_type == "collaborator_left":
            logger.info(f"👋 {data.get('message', 'Someone left')}")
    
    async def _handle_team_message(self, data: Dict[str, Any]):
        """Handle messages from team members."""
        message = data.get("message", {})
        from_name = data.get("from_name", "Unknown")
        content = message.get("content", "")
        from_role = message.get("from_role", "")
        
        # Log the message
        timestamp = datetime.fromtimestamp(message.get("timestamp", 0))
        logger.info(f"💬 [{timestamp.strftime('%H:%M:%S')}] {from_name}: {content}")
        
        # If this is a question directed at us or our role, we might want to respond
        if self._should_respond_to_message(content, from_role):
            await self._generate_response_to_message(content, from_name, from_role)
    
    def _should_respond_to_message(self, content: str, from_role: str) -> bool:
        """Determine if we should respond to a team message."""
        content_lower = content.lower()
        
        # Respond if our role is mentioned
        if self.role.lower() in content_lower:
            return True
        
        # Respond if it's a question and we're the appropriate role
        if "?" in content:
            if self.role == "cto" and any(word in content_lower for word in ["architecture", "technical", "design", "decision"]):
                return True
            elif self.role == "backend-dev" and any(word in content_lower for word in ["implement", "code", "backend", "api"]):
                return True
            elif self.role == "qa" and any(word in content_lower for word in ["test", "quality", "bug", "validation"]):
                return True
        
        return False
    
    async def _generate_response_to_message(self, content: str, from_name: str, from_role: str):
        """Generate and send response to team message."""
        try:
            # Create a task for responding to the team message
            response_task = EnhancedTask(
                task_type=TaskType.GENERAL,
                prompt=f"""As a {self.role} in our development team, respond to this message from {from_name} ({from_role}):

"{content}"

Provide a helpful, role-appropriate response. Be concise but informative.
Context: We're working on AIOSv3, a modular AI agent platform.""",
                complexity=3,
                metadata={
                    "interaction_type": "team_message_response",
                    "from_name": from_name,
                    "from_role": from_role
                }
            )
            
            # Process the response
            result = await self.process_task(response_task)
            
            if result.success:
                # Send response to team
                await self.send_collaboration_message({
                    "type": "chat",
                    "from_id": self.agent_id,
                    "content": result.output,
                    "metadata": {
                        "responding_to": from_name,
                        "cost": result.cost,
                        "model_used": result.model_used
                    }
                })
            
        except Exception as e:
            logger.error(f"Failed to generate response to team message: {e}")
    
    async def _handle_task_assignment(self, data: Dict[str, Any]):
        """Handle task assignment from orchestrator."""
        task_data = data.get("task", {})
        
        logger.info(f"📋 Received task assignment: {task_data.get('title', 'Untitled')}")
        
        # Store assignment
        self.assigned_tasks.append(task_data)
        self.current_assignment = task_data
        
        # Update status to busy
        await self.send_collaboration_message({
            "type": "status_update",
            "from_id": self.agent_id,
            "status": "busy",
            "current_task": task_data.get("title")
        })
        
        # Execute the task
        await self._execute_assigned_task(task_data)
    
    async def _execute_assigned_task(self, task_data: Dict[str, Any]):
        """Execute an assigned task using Enhanced BaseAgent framework."""
        try:
            # Convert to EnhancedTask
            enhanced_task = EnhancedTask(
                task_type=TaskType(task_data.get("task_type", "general")),
                prompt=task_data.get("description", ""),
                complexity=task_data.get("complexity", 5),
                metadata={
                    "assigned_by": task_data.get("assigned_by"),
                    "collaboration_task_id": task_data.get("id"),
                    "role": self.role
                }
            )
            
            # Process task
            result = await self.process_task(enhanced_task)
            
            # Report results back to team
            if result.success:
                await self.send_collaboration_message({
                    "type": "task_completed",
                    "task_id": task_data.get("id"),
                    "from_id": self.agent_id,
                    "result": {
                        "success": True,
                        "output": result.output,
                        "cost": result.cost,
                        "execution_time": result.execution_time,
                        "model_used": result.model_used
                    }
                })
                
                await self.send_collaboration_message({
                    "type": "chat",
                    "from_id": self.agent_id,
                    "content": f"✅ Completed task: {task_data.get('title')}\n\n{result.output}",
                    "metadata": {
                        "task_completion": True,
                        "cost": result.cost
                    }
                })
            else:
                await self.send_collaboration_message({
                    "type": "task_failed",
                    "task_id": task_data.get("id"),
                    "from_id": self.agent_id,
                    "error": result.error
                })
        
        except Exception as e:
            logger.error(f"Failed to execute assigned task: {e}")
            await self.send_collaboration_message({
                "type": "task_failed",
                "task_id": task_data.get("id"),
                "from_id": self.agent_id,
                "error": str(e)
            })
        
        finally:
            # Update status back to active
            self.current_assignment = None
            await self.send_collaboration_message({
                "type": "status_update",
                "from_id": self.agent_id,
                "status": "active",
                "current_task": None
            })
    
    async def _handle_task_update(self, data: Dict[str, Any]):
        """Handle task status updates."""
        task = data.get("task", {})
        logger.info(f"📋 Task updated: {task.get('title')} [{task.get('status')}]")
    
    async def _initialize_role_specific(self):
        """Initialize role-specific capabilities and knowledge."""
        if self.role == "cto":
            await self._initialize_cto_knowledge()
        elif self.role == "backend-dev":
            await self._initialize_backend_knowledge()
        elif self.role == "qa":
            await self._initialize_qa_knowledge()
    
    async def _initialize_cto_knowledge(self):
        """Initialize CTO-specific knowledge."""
        await self.store_knowledge(
            content="CTO Agent specialized in system architecture, technical leadership, and strategic planning for AIOSv3 platform",
            category="role_identity",
            keywords=["cto", "architecture", "leadership", "strategy"]
        )
    
    async def _initialize_backend_knowledge(self):
        """Initialize Backend Developer knowledge."""
        await self.store_knowledge(
            content="Backend Developer Agent specialized in server-side implementation, API development, and database design for AIOSv3",
            category="role_identity", 
            keywords=["backend", "api", "database", "implementation"]
        )
    
    async def _initialize_qa_knowledge(self):
        """Initialize QA Engineer knowledge."""
        await self.store_knowledge(
            content="QA Engineer Agent specialized in testing, quality assurance, and validation for AIOSv3 platform",
            category="role_identity",
            keywords=["qa", "testing", "quality", "validation"]
        )
    
    async def _process_response(self, response, task) -> str:
        """Process response with role-specific formatting."""
        # Use role-specific response processing
        if self.role == "cto":
            return self._format_cto_response(response.content, task)
        elif self.role == "backend-dev":
            return self._format_backend_response(response.content, task)
        elif self.role == "qa":
            return self._format_qa_response(response.content, task)
        else:
            return response.content
    
    def _format_cto_response(self, content: str, task) -> str:
        """Format CTO responses."""
        return f"""# 🏗️ CTO Analysis

{content}

---
*CTO Agent | {datetime.now().strftime('%Y-%m-%d %H:%M')}*"""
    
    def _format_backend_response(self, content: str, task) -> str:
        """Format Backend Developer responses."""
        return f"""# 👨‍💻 Backend Implementation

{content}

---
*Backend Developer | {datetime.now().strftime('%Y-%m-%d %H:%M')}*"""
    
    def _format_qa_response(self, content: str, task) -> str:
        """Format QA Engineer responses."""
        return f"""# 🧪 QA Analysis

{content}

---
*QA Engineer | {datetime.now().strftime('%Y-%m-%d %H:%M')}*"""
    
    async def _customize_prompt(self, task, context: str) -> str:
        """Customize prompts based on agent role."""
        role_prompts = {
            "cto": f"""You are the CTO (Chief Technology Officer) of AIOSv3, a cutting-edge AI agent platform.
Your expertise includes system architecture, technology evaluation, engineering leadership, and strategic technical planning.

Current Context: {context}

Provide technical leadership perspective with clear recommendations, rationale, and implementation guidance.""",
            
            "backend-dev": f"""You are a Senior Backend Developer working on AIOSv3, a modular AI agent platform.
Your expertise includes Python development, API design, database architecture, and server-side implementation.

Current Context: {context}

Focus on practical implementation details, code examples, and technical execution.""",
            
            "qa": f"""You are a QA Engineer responsible for quality assurance of AIOSv3, an AI agent platform.
Your expertise includes testing strategies, quality metrics, validation procedures, and bug detection.

Current Context: {context}

Focus on testing approaches, quality criteria, and validation methods."""
        }
        
        return role_prompts.get(self.role, f"""You are a {self.role} working on AIOSv3.

Current Context: {context}

Provide expert guidance based on your role and expertise.""")


# Factory functions for easy agent creation
async def create_collaborative_cto_agent(collaboration_server: str = "ws://localhost:8765", llm_router: Optional[LLMRouter] = None) -> CollaborativeAgent:
    """Create CTO collaborative agent."""
    config = CollaborativeAgentConfig(role="cto", collaboration_server=collaboration_server)
    agent = CollaborativeAgent(config, llm_router)
    await agent.initialize()
    return agent

async def create_collaborative_backend_agent(collaboration_server: str = "ws://localhost:8765", llm_router: Optional[LLMRouter] = None) -> CollaborativeAgent:
    """Create Backend Developer collaborative agent.""" 
    config = CollaborativeAgentConfig(role="backend-dev", collaboration_server=collaboration_server)
    agent = CollaborativeAgent(config, llm_router)
    await agent.initialize()
    return agent

async def create_collaborative_qa_agent(collaboration_server: str = "ws://localhost:8765", llm_router: Optional[LLMRouter] = None) -> CollaborativeAgent:
    """Create QA Engineer collaborative agent."""
    config = CollaborativeAgentConfig(role="qa", collaboration_server=collaboration_server)
    agent = CollaborativeAgent(config, llm_router)
    await agent.initialize()
    return agent