"""
Agent registration system for automatic discovery and monitoring.

This module provides automatic agent registration with the monitoring server,
allowing agents to announce themselves and receive monitoring services.
"""

import asyncio
import json
import time
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

import aiohttp
from aiohttp import web


@dataclass
class AgentRegistration:
    """Agent registration information."""
    agent_id: str
    name: str
    agent_type: str
    capabilities: List[str]
    endpoint: str
    status: str = "active"
    registered_at: datetime = None
    last_heartbeat: datetime = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.registered_at is None:
            self.registered_at = datetime.utcnow()
        if self.last_heartbeat is None:
            self.last_heartbeat = datetime.utcnow()
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['registered_at'] = self.registered_at.isoformat()
        data['last_heartbeat'] = self.last_heartbeat.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentRegistration':
        """Create from dictionary."""
        if 'registered_at' in data and isinstance(data['registered_at'], str):
            data['registered_at'] = datetime.fromisoformat(data['registered_at'])
        if 'last_heartbeat' in data and isinstance(data['last_heartbeat'], str):
            data['last_heartbeat'] = datetime.fromisoformat(data['last_heartbeat'])
        return cls(**data)


class AgentRegistry:
    """Central registry for agent discovery and management."""
    
    def __init__(self, monitoring_server):
        self.monitoring_server = monitoring_server
        self.agents: Dict[str, AgentRegistration] = {}
        self.heartbeat_timeout = timedelta(minutes=5)
        self.cleanup_interval = 60  # seconds
        
        # Start background cleanup task
        asyncio.create_task(self._cleanup_stale_agents())
    
    async def register_agent(self, registration_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new agent or update existing registration."""
        try:
            agent_id = registration_data.get('agent_id')
            if not agent_id:
                agent_id = str(uuid.uuid4())
                registration_data['agent_id'] = agent_id
            
            # Validate required fields
            required_fields = ['name', 'agent_type', 'capabilities', 'endpoint']
            for field in required_fields:
                if field not in registration_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Create or update registration
            if agent_id in self.agents:
                # Update existing registration
                existing = self.agents[agent_id]
                existing.name = registration_data['name']
                existing.agent_type = registration_data['agent_type']
                existing.capabilities = registration_data['capabilities']
                existing.endpoint = registration_data['endpoint']
                existing.status = registration_data.get('status', 'active')
                existing.last_heartbeat = datetime.utcnow()
                existing.metadata.update(registration_data.get('metadata', {}))
                
                registration = existing
            else:
                # Create new registration
                registration = AgentRegistration(
                    agent_id=agent_id,
                    name=registration_data['name'],
                    agent_type=registration_data['agent_type'],
                    capabilities=registration_data['capabilities'],
                    endpoint=registration_data['endpoint'],
                    status=registration_data.get('status', 'active'),
                    metadata=registration_data.get('metadata', {})
                )
                self.agents[agent_id] = registration
            
            # Store in database if available
            if hasattr(self.monitoring_server, 'db') and self.monitoring_server.db:
                await self._store_registration(registration)
            
            # Notify monitoring server about new agent
            await self._notify_agent_registered(registration)
            
            return {
                'success': True,
                'agent_id': agent_id,
                'message': 'Agent registered successfully',
                'registration': registration.to_dict()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Agent registration failed'
            }
    
    async def unregister_agent(self, agent_id: str) -> Dict[str, Any]:
        """Unregister an agent."""
        try:
            if agent_id not in self.agents:
                return {
                    'success': False,
                    'error': 'Agent not found',
                    'message': f'Agent {agent_id} not registered'
                }
            
            registration = self.agents[agent_id]
            registration.status = 'unregistered'
            
            # Remove from active registry
            del self.agents[agent_id]
            
            # Update database
            if hasattr(self.monitoring_server, 'db') and self.monitoring_server.db:
                await self._update_registration_status(agent_id, 'unregistered')
            
            # Notify monitoring server
            await self._notify_agent_unregistered(registration)
            
            return {
                'success': True,
                'message': f'Agent {agent_id} unregistered successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Agent unregistration failed'
            }
    
    async def heartbeat(self, agent_id: str, status_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process agent heartbeat."""
        try:
            if agent_id not in self.agents:
                return {
                    'success': False,
                    'error': 'Agent not registered',
                    'message': f'Agent {agent_id} must register first'
                }
            
            registration = self.agents[agent_id]
            registration.last_heartbeat = datetime.utcnow()
            
            # Update status if provided
            if status_data:
                registration.status = status_data.get('status', registration.status)
                registration.metadata.update(status_data.get('metadata', {}))
            
            # Store heartbeat activity
            await self._log_heartbeat_activity(registration, status_data)
            
            return {
                'success': True,
                'message': 'Heartbeat received',
                'server_time': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Heartbeat processing failed'
            }
    
    def get_agents(self, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get list of registered agents."""
        agents = []
        for registration in self.agents.values():
            if status_filter is None or registration.status == status_filter:
                agents.append(registration.to_dict())
        return agents
    
    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get specific agent registration."""
        if agent_id in self.agents:
            return self.agents[agent_id].to_dict()
        return None
    
    def get_agents_by_type(self, agent_type: str) -> List[Dict[str, Any]]:
        """Get agents by type."""
        agents = []
        for registration in self.agents.values():
            if registration.agent_type == agent_type:
                agents.append(registration.to_dict())
        return agents
    
    def get_agents_by_capability(self, capability: str) -> List[Dict[str, Any]]:
        """Get agents that have a specific capability."""
        agents = []
        for registration in self.agents.values():
            if capability in registration.capabilities:
                agents.append(registration.to_dict())
        return agents
    
    async def _cleanup_stale_agents(self):
        """Background task to clean up stale agent registrations."""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                
                cutoff_time = datetime.utcnow() - self.heartbeat_timeout
                stale_agents = []
                
                for agent_id, registration in self.agents.items():
                    if registration.last_heartbeat < cutoff_time:
                        stale_agents.append(agent_id)
                
                for agent_id in stale_agents:
                    registration = self.agents[agent_id]
                    registration.status = 'stale'
                    await self._notify_agent_stale(registration)
                    del self.agents[agent_id]
                    
                if stale_agents:
                    print(f"Cleaned up {len(stale_agents)} stale agent registrations")
                    
            except Exception as e:
                print(f"Error in agent cleanup: {e}")
    
    async def _store_registration(self, registration: AgentRegistration):
        """Store agent registration in database."""
        try:
            if hasattr(self.monitoring_server, 'db') and self.monitoring_server.db:
                await self.monitoring_server.db.execute("""
                    INSERT OR REPLACE INTO agent_registrations (
                        agent_id, name, agent_type, capabilities, endpoint, 
                        status, registered_at, last_heartbeat, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    registration.agent_id,
                    registration.name,
                    registration.agent_type,
                    json.dumps(registration.capabilities),
                    registration.endpoint,
                    registration.status,
                    registration.registered_at.isoformat(),
                    registration.last_heartbeat.isoformat(),
                    json.dumps(registration.metadata)
                ))
                await self.monitoring_server.db.commit()
        except Exception as e:
            print(f"Error storing registration: {e}")
    
    async def _update_registration_status(self, agent_id: str, status: str):
        """Update agent registration status in database."""
        try:
            if hasattr(self.monitoring_server, 'db') and self.monitoring_server.db:
                await self.monitoring_server.db.execute("""
                    UPDATE agent_registrations 
                    SET status = ?, last_heartbeat = ?
                    WHERE agent_id = ?
                """, (status, datetime.utcnow().isoformat(), agent_id))
                await self.monitoring_server.db.commit()
        except Exception as e:
            print(f"Error updating registration status: {e}")
    
    async def _log_heartbeat_activity(self, registration: AgentRegistration, status_data: Optional[Dict[str, Any]]):
        """Log heartbeat as monitoring activity."""
        activity = {
            'id': str(uuid.uuid4()),
            'agent_id': registration.agent_id,
            'agent_name': registration.name,
            'type': 'heartbeat',
            'status': 'success',
            'message': 'Agent heartbeat received',
            'metadata': {
                'agent_type': registration.agent_type,
                'capabilities': registration.capabilities,
                'endpoint': registration.endpoint,
                'status_data': status_data or {}
            },
            'stored_at': datetime.utcnow().isoformat()
        }
        
        # Store in monitoring server
        if hasattr(self.monitoring_server, 'store_activity'):
            await self.monitoring_server.store_activity(activity)
    
    async def _notify_agent_registered(self, registration: AgentRegistration):
        """Notify monitoring server about agent registration."""
        activity = {
            'id': str(uuid.uuid4()),
            'agent_id': registration.agent_id,
            'agent_name': registration.name,
            'type': 'registration',
            'status': 'success',
            'message': f'Agent {registration.name} registered successfully',
            'metadata': {
                'agent_type': registration.agent_type,
                'capabilities': registration.capabilities,
                'endpoint': registration.endpoint,
                'registration_time': registration.registered_at.isoformat()
            },
            'stored_at': datetime.utcnow().isoformat()
        }
        
        if hasattr(self.monitoring_server, 'store_activity'):
            await self.monitoring_server.store_activity(activity)
        
        # Broadcast to WebSocket clients
        if hasattr(self.monitoring_server, 'broadcast_to_websockets'):
            await self.monitoring_server.broadcast_to_websockets({
                'type': 'agent_registered',
                'agent': registration.to_dict(),
                'activity': activity
            })
    
    async def _notify_agent_unregistered(self, registration: AgentRegistration):
        """Notify monitoring server about agent unregistration."""
        activity = {
            'id': str(uuid.uuid4()),
            'agent_id': registration.agent_id,
            'agent_name': registration.name,
            'type': 'unregistration',
            'status': 'info',
            'message': f'Agent {registration.name} unregistered',
            'metadata': {
                'agent_type': registration.agent_type,
                'unregistration_time': datetime.utcnow().isoformat()
            },
            'stored_at': datetime.utcnow().isoformat()
        }
        
        if hasattr(self.monitoring_server, 'store_activity'):
            await self.monitoring_server.store_activity(activity)
        
        # Broadcast to WebSocket clients
        if hasattr(self.monitoring_server, 'broadcast_to_websockets'):
            await self.monitoring_server.broadcast_to_websockets({
                'type': 'agent_unregistered',
                'agent_id': registration.agent_id,
                'activity': activity
            })
    
    async def _notify_agent_stale(self, registration: AgentRegistration):
        """Notify about stale agent."""
        activity = {
            'id': str(uuid.uuid4()),
            'agent_id': registration.agent_id,
            'agent_name': registration.name,
            'type': 'stale_agent',
            'status': 'warning',
            'message': f'Agent {registration.name} has gone stale (no heartbeat)',
            'metadata': {
                'agent_type': registration.agent_type,
                'last_heartbeat': registration.last_heartbeat.isoformat(),
                'stale_detected_at': datetime.utcnow().isoformat()
            },
            'stored_at': datetime.utcnow().isoformat()
        }
        
        if hasattr(self.monitoring_server, 'store_activity'):
            await self.monitoring_server.store_activity(activity)


class AgentRegistrationMixin:
    """Mixin to add agent registration functionality to agents."""
    
    def __init__(self, monitoring_url: str = 'http://localhost:6795', 
                 api_key: str = 'aios_default_key', **kwargs):
        super().__init__(**kwargs)
        self.monitoring_url = monitoring_url
        self.api_key = api_key
        self.registration_id = None
        self.heartbeat_interval = 30  # seconds
        self.heartbeat_task = None
        
    async def register_with_monitoring(self) -> bool:
        """Register this agent with the monitoring server."""
        try:
            registration_data = {
                'agent_id': self.id,
                'name': getattr(self, 'name', f'Agent-{self.id[:8]}'),
                'agent_type': getattr(self, 'agent_type', 'generic'),
                'capabilities': getattr(self, 'capabilities', []),
                'endpoint': f'agent://{self.id}',
                'status': 'active',
                'metadata': {
                    'started_at': datetime.utcnow().isoformat(),
                    'python_class': self.__class__.__name__,
                    'config': getattr(self, 'config', {})
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f'{self.monitoring_url}/api/agents/register',
                    json=registration_data,
                    headers={'X-API-Key': self.api_key}
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get('success'):
                            self.registration_id = result.get('agent_id')
                            print(f"Agent {self.name} registered successfully with monitoring server")
                            
                            # Start heartbeat task
                            self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
                            return True
                        else:
                            print(f"Registration failed: {result.get('error')}")
                            return False
                    else:
                        print(f"Registration failed with status {response.status}")
                        return False
                        
        except Exception as e:
            print(f"Error registering with monitoring server: {e}")
            return False
    
    async def unregister_from_monitoring(self) -> bool:
        """Unregister from monitoring server."""
        try:
            if self.heartbeat_task:
                self.heartbeat_task.cancel()
                try:
                    await self.heartbeat_task
                except asyncio.CancelledError:
                    pass
            
            if not self.registration_id:
                return True
            
            async with aiohttp.ClientSession() as session:
                async with session.delete(
                    f'{self.monitoring_url}/api/agents/{self.registration_id}',
                    headers={'X-API-Key': self.api_key}
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get('success'):
                            print(f"Agent {self.name} unregistered successfully")
                            return True
                    
            return False
            
        except Exception as e:
            print(f"Error unregistering from monitoring server: {e}")
            return False
    
    async def _heartbeat_loop(self):
        """Background heartbeat loop."""
        while True:
            try:
                await asyncio.sleep(self.heartbeat_interval)
                await self._send_heartbeat()
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Heartbeat error: {e}")
    
    async def _send_heartbeat(self):
        """Send heartbeat to monitoring server."""
        try:
            if not self.registration_id:
                return
            
            status_data = {
                'status': getattr(self, 'state', 'active'),
                'metadata': {
                    'current_tasks': len(getattr(self, 'current_tasks', {})),
                    'tasks_completed': len(getattr(self, 'task_history', [])),
                    'uptime_seconds': getattr(self, 'uptime_seconds', 0),
                    'memory_usage': len(getattr(self, 'memory', {})),
                    'last_heartbeat': datetime.utcnow().isoformat()
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f'{self.monitoring_url}/api/agents/{self.registration_id}/heartbeat',
                    json=status_data,
                    headers={'X-API-Key': self.api_key}
                ) as response:
                    if response.status != 200:
                        result = await response.json()
                        if not result.get('success'):
                            print(f"Heartbeat failed: {result.get('error')}")
                            
        except Exception as e:
            print(f"Error sending heartbeat: {e}")