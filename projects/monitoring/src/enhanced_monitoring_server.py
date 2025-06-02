"""
Enhanced WebSocket monitoring server for AIOSv3 agents.

Features:
- API key authentication
- Rate limiting
- Enhanced error handling
- JWT token support
"""

import asyncio
import json
import os
import time
import weakref
import hashlib
import secrets
from typing import Set, Dict, Any, Optional
from datetime import datetime, timedelta
from aiohttp import web, WSMsgType
import aiohttp_cors
import jwt
from functools import wraps

from .agent_registry import AgentRegistry
from .database import MonitoringDatabase

# Rate limiting store (in production, use Redis)
RATE_LIMIT_STORE = {}

class AuthenticationError(Exception):
    """Authentication related errors."""
    pass

class RateLimitError(Exception):
    """Rate limiting errors."""
    pass

def require_auth(f):
    """Decorator for endpoints requiring authentication."""
    @wraps(f)
    async def wrapper(self, request):
        # Check API key
        api_key = request.headers.get('X-API-Key') or request.query.get('api_key')
        if not api_key:
            return web.json_response(
                {'error': 'API key required'}, 
                status=401
            )
        
        if not self.validate_api_key(api_key):
            return web.json_response(
                {'error': 'Invalid API key'}, 
                status=401
            )
        
        # Rate limiting
        client_ip = request.remote
        if not self.check_rate_limit(client_ip, api_key):
            return web.json_response(
                {'error': 'Rate limit exceeded'}, 
                status=429
            )
        
        # Add auth info to request
        request['auth'] = {'api_key': api_key, 'client_ip': client_ip}
        return await f(self, request)
    
    return wrapper

class EnhancedMonitoringServer:
    """Enhanced monitoring server with authentication and persistence."""
    
    def __init__(self, port: int = 6795):
        self.port = port
        self.app = web.Application()
        self.websockets: Set[weakref.ref] = set()
        
        # Initialize database
        self.db = None
        self.db_path = os.getenv('MONITORING_DB_PATH', 'monitoring.db')
        
        # Authentication
        self.master_api_key = os.getenv('MONITORING_API_KEY', self.generate_api_key())
        self.api_keys = {self.master_api_key: {'name': 'master', 'created': datetime.utcnow()}}
        self.jwt_secret = os.getenv('JWT_SECRET', secrets.token_urlsafe(32))
        
        # Rate limiting (requests per minute)
        self.rate_limit = int(os.getenv('RATE_LIMIT', '100'))
        
        # Agent registry
        self.agent_registry = AgentRegistry(self)
        
        self.setup_routes()
        self.setup_cors()
        
        print(f"Master API Key: {self.master_api_key}")
        
    def generate_api_key(self) -> str:
        """Generate a secure API key."""
        return f"aios_{secrets.token_urlsafe(32)}"
    
    def validate_api_key(self, api_key: str) -> bool:
        """Validate API key."""
        return api_key in self.api_keys
    
    def check_rate_limit(self, client_ip: str, api_key: str) -> bool:
        """Check rate limiting for client."""
        key = f"{client_ip}:{api_key}"
        now = datetime.utcnow()
        
        if key not in RATE_LIMIT_STORE:
            RATE_LIMIT_STORE[key] = []
        
        # Clean old requests
        RATE_LIMIT_STORE[key] = [
            req_time for req_time in RATE_LIMIT_STORE[key] 
            if now - req_time < timedelta(minutes=1)
        ]
        
        # Check limit
        if len(RATE_LIMIT_STORE[key]) >= self.rate_limit:
            return False
        
        # Add current request
        RATE_LIMIT_STORE[key].append(now)
        return True
    
    def setup_routes(self):
        """Configure server routes."""
        # WebSocket endpoint (authenticated)
        self.app.router.add_get('/ws', self.websocket_handler)
        
        # Public endpoints
        self.app.router.add_get('/api/health', self.health_check)
        
        # Authenticated endpoints
        self.app.router.add_post('/api/activities', self.post_activity)
        self.app.router.add_get('/api/activities', self.get_activities)
        self.app.router.add_get('/api/agents', self.get_agents)
        
        # Agent registration endpoints
        self.app.router.add_post('/api/agents/register', self.register_agent)
        self.app.router.add_delete('/api/agents/{agent_id}', self.unregister_agent)
        self.app.router.add_post('/api/agents/{agent_id}/heartbeat', self.agent_heartbeat)
        self.app.router.add_get('/api/agents/{agent_id}', self.get_agent)
        
        # Admin endpoints
        self.app.router.add_post('/api/admin/api-keys', self.create_api_key)
        self.app.router.add_get('/api/admin/api-keys', self.list_api_keys)
        
    def setup_cors(self):
        """Configure CORS for dashboard access."""
        cors = aiohttp_cors.setup(self.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
            )
        })
        
        for route in list(self.app.router.routes()):
            cors.add(route)
    
    async def websocket_handler(self, request):
        """Handle authenticated WebSocket connections."""
        # Check authentication for WebSocket
        api_key = request.query.get('api_key')
        if not api_key or not self.validate_api_key(api_key):
            return web.Response(status=401, text="Unauthorized")
        
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        # Store weak reference with auth info
        ws_ref = weakref.ref(ws)
        self.websockets.add(ws_ref)
        
        try:
            # Send initial authenticated state
            await ws.send_json({
                'type': 'connection',
                'status': 'connected',
                'authenticated': True,
                'timestamp': datetime.utcnow().isoformat()
            })
            
            # Handle messages
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        await self.handle_ws_message(data, ws, api_key)
                    except json.JSONDecodeError:
                        await ws.send_json({
                            'type': 'error',
                            'message': 'Invalid JSON'
                        })
                elif msg.type == WSMsgType.ERROR:
                    print(f'WebSocket error: {ws.exception()}')
                    break
                    
        except Exception as e:
            print(f"WebSocket handler error: {e}")
            try:
                await ws.send_json({
                    'type': 'error',
                    'message': 'Connection error'
                })
            except:
                pass
        finally:
            self.websockets.discard(ws_ref)
            
        return ws
    
    async def handle_ws_message(self, data: Dict[str, Any], ws, api_key: str):
        """Process authenticated WebSocket messages."""
        msg_type = data.get('type')
        
        try:
            if msg_type == 'activity':
                # Store and broadcast activity
                activity_data = data.get('activity', {})
                activity_data['api_key'] = api_key  # Track source
                activity = await self.store_activity(activity_data)
                await self.broadcast_activity(activity)
                
            elif msg_type == 'ping':
                await ws.send_json({
                    'type': 'pong',
                    'timestamp': datetime.utcnow().isoformat()
                })
                
            elif msg_type == 'subscribe':
                # Subscribe to specific activity types
                filters = data.get('filters', {})
                await ws.send_json({
                    'type': 'subscribed',
                    'filters': filters
                })
                
            else:
                await ws.send_json({
                    'type': 'error',
                    'message': f'Unknown message type: {msg_type}'
                })
                
        except Exception as e:
            await ws.send_json({
                'type': 'error',
                'message': str(e)
            })
    
    async def store_activity(self, activity: Dict[str, Any]) -> Dict[str, Any]:
        """Store activity with enhanced metadata."""
        # Add server metadata
        activity.update({
            'stored_at': datetime.utcnow().isoformat(),
            'server_version': '1.0.0',
            'id': activity.get('id', secrets.token_urlsafe(8))
        })
        
        # Store in database if available
        if self.db:
            await self.db.store_activity(activity)
        else:
            # Fallback to in-memory store
            if not hasattr(self, '_activities'):
                self._activities = []
            
            self._activities.append(activity)
            
            # Keep only last 1000 in memory
            if len(self._activities) > 1000:
                self._activities = self._activities[-1000:]
        
        return activity
    
    async def broadcast_activity(self, activity: Dict[str, Any]):
        """Broadcast activity to authenticated clients."""
        message = {
            'type': 'activity',
            'activity': activity,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Send to all connected clients
        disconnected = []
        for ws_ref in list(self.websockets):
            ws = ws_ref()
            if ws is not None and not ws.closed:
                try:
                    await ws.send_json(message)
                except (ConnectionResetError, ConnectionAbortedError):
                    disconnected.append(ws_ref)
            else:
                disconnected.append(ws_ref)
        
        # Clean up disconnected clients
        for ws_ref in disconnected:
            self.websockets.discard(ws_ref)
    
    async def health_check(self, request):
        """Public health check endpoint."""
        return web.json_response({
            'status': 'healthy',
            'version': '1.0.0',
            'connections': len(self.websockets),
            'uptime': time.time(),
            'features': ['authentication', 'rate_limiting', 'websockets']
        })
    
    @require_auth
    async def post_activity(self, request):
        """Store new activity via REST API."""
        try:
            data = await request.json()
            activity = await self.store_activity(data)
            await self.broadcast_activity(activity)
            
            return web.json_response({
                'status': 'stored',
                'activity_id': activity['id']
            })
            
        except Exception as e:
            return web.json_response(
                {'error': str(e)}, 
                status=400
            )
    
    @require_auth
    async def get_activities(self, request):
        """Get stored activities with filtering."""
        try:
            # Get query parameters
            limit = int(request.query.get('limit', 100))
            since = request.query.get('since')
            agent_id = request.query.get('agent_id')
            
            # Get activities (from memory for now)
            activities = getattr(self, '_activities', [])
            
            # Apply filters
            if since:
                since_dt = datetime.fromisoformat(since.replace('Z', '+00:00'))
                activities = [
                    a for a in activities 
                    if datetime.fromisoformat(a['stored_at']) > since_dt
                ]
            
            if agent_id:
                activities = [
                    a for a in activities 
                    if a.get('agent_id') == agent_id
                ]
            
            # Apply limit
            activities = activities[-limit:]
            
            return web.json_response({
                'activities': activities,
                'count': len(activities),
                'total': len(getattr(self, '_activities', []))
            })
            
        except Exception as e:
            return web.json_response(
                {'error': str(e)}, 
                status=400
            )
    
    @require_auth
    async def get_agents(self, request):
        """Get registered agents."""
        try:
            # Get status filter if provided
            status_filter = request.query.get('status')
            agent_type = request.query.get('type')
            capability = request.query.get('capability')
            
            # Get agents from registry
            if agent_type:
                agents = self.agent_registry.get_agents_by_type(agent_type)
            elif capability:
                agents = self.agent_registry.get_agents_by_capability(capability)
            else:
                agents = self.agent_registry.get_agents(status_filter)
            
            return web.json_response({
                'agents': agents,
                'count': len(agents),
                'total_registered': len(self.agent_registry.agents)
            })
            
        except Exception as e:
            return web.json_response({
                'error': str(e)
            }, status=500)
    
    @require_auth
    async def create_api_key(self, request):
        """Create new API key (admin only)."""
        # Check if master key
        auth = request.get('auth', {})
        if auth.get('api_key') != self.master_api_key:
            return web.json_response(
                {'error': 'Master API key required'}, 
                status=403
            )
        
        try:
            data = await request.json()
            name = data.get('name', 'unnamed')
            
            new_key = self.generate_api_key()
            self.api_keys[new_key] = {
                'name': name,
                'created': datetime.utcnow()
            }
            
            return web.json_response({
                'api_key': new_key,
                'name': name
            })
            
        except Exception as e:
            return web.json_response(
                {'error': str(e)}, 
                status=400
            )
    
    @require_auth
    async def list_api_keys(self, request):
        """List API keys (admin only)."""
        # Check if master key
        auth = request.get('auth', {})
        if auth.get('api_key') != self.master_api_key:
            return web.json_response(
                {'error': 'Master API key required'}, 
                status=403
            )
        
        keys_info = []
        for key, info in self.api_keys.items():
            keys_info.append({
                'key': key[:12] + '...',  # Partial key for security
                'name': info['name'],
                'created': info['created'].isoformat()
            })
        
        return web.json_response({
            'api_keys': keys_info,
            'count': len(keys_info)
        })
    
    # Agent Registration Endpoints
    @require_auth
    async def register_agent(self, request):
        """Register a new agent with the monitoring server."""
        try:
            data = await request.json()
            result = await self.agent_registry.register_agent(data)
            
            if result['success']:
                return web.json_response(result, status=200)
            else:
                return web.json_response(result, status=400)
                
        except Exception as e:
            return web.json_response({
                'success': False,
                'error': str(e),
                'message': 'Agent registration failed'
            }, status=500)
    
    @require_auth
    async def unregister_agent(self, request):
        """Unregister an agent."""
        try:
            agent_id = request.match_info['agent_id']
            result = await self.agent_registry.unregister_agent(agent_id)
            
            if result['success']:
                return web.json_response(result, status=200)
            else:
                return web.json_response(result, status=404)
                
        except Exception as e:
            return web.json_response({
                'success': False,
                'error': str(e),
                'message': 'Agent unregistration failed'
            }, status=500)
    
    @require_auth
    async def agent_heartbeat(self, request):
        """Process agent heartbeat."""
        try:
            agent_id = request.match_info['agent_id']
            data = await request.json()
            result = await self.agent_registry.heartbeat(agent_id, data)
            
            if result['success']:
                return web.json_response(result, status=200)
            else:
                return web.json_response(result, status=400)
                
        except Exception as e:
            return web.json_response({
                'success': False,
                'error': str(e),
                'message': 'Heartbeat processing failed'
            }, status=500)
    
    @require_auth
    async def get_agent(self, request):
        """Get specific agent information."""
        try:
            agent_id = request.match_info['agent_id']
            agent = self.agent_registry.get_agent(agent_id)
            
            if agent:
                return web.json_response({
                    'success': True,
                    'agent': agent
                })
            else:
                return web.json_response({
                    'success': False,
                    'error': 'Agent not found'
                }, status=404)
                
        except Exception as e:
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    async def broadcast_to_websockets(self, message: Dict[str, Any]):
        """Broadcast message to all connected WebSocket clients."""
        await self.broadcast_activity(message)
    
    async def initialize(self):
        """Initialize the server components."""
        # Initialize database
        self.db = MonitoringDatabase(self.db_path)
        await self.db.initialize()
        
        # Add agent_registrations table to database
        await self.db.db.executescript("""
            CREATE TABLE IF NOT EXISTS agent_registrations (
                agent_id TEXT PRIMARY KEY,
                name TEXT,
                agent_type TEXT,
                capabilities TEXT,
                endpoint TEXT,
                status TEXT,
                registered_at TIMESTAMP,
                last_heartbeat TIMESTAMP,
                metadata TEXT
            );
            
            CREATE INDEX IF NOT EXISTS idx_agent_registrations_status 
            ON agent_registrations(status);
            CREATE INDEX IF NOT EXISTS idx_agent_registrations_type 
            ON agent_registrations(agent_type);
        """)
        await self.db.db.commit()
        
        print("✅ Database initialized")
    
    async def start_server(self):
        """Start the server with initialization."""
        await self.initialize()
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', self.port)
        await site.start()
        print(f"✅ Server running on http://0.0.0.0:{self.port}")
        
        # Keep running
        try:
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            print("Shutting down...")
            await runner.cleanup()
    
    def run(self):
        """Start the enhanced server."""
        print(f"🚀 Enhanced Monitoring Server starting on port {self.port}")
        print(f"🔑 Master API Key: {self.master_api_key}")
        print(f"📊 Rate limit: {self.rate_limit} requests/minute")
        
        asyncio.run(self.start_server())


if __name__ == '__main__':
    server = EnhancedMonitoringServer()
    server.run()