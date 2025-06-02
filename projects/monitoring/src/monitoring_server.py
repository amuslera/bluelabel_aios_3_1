"""
WebSocket monitoring server for AIOSv3 agents.

Provides real-time activity streaming and historical queries.
"""

import asyncio
import json
import time
import weakref
import logging
import os
from typing import Set, Dict, Any, Optional
from datetime import datetime
from aiohttp import web
import aiohttp_cors

class MonitoringServer:
    """Real-time monitoring server with WebSocket support."""
    
    def __init__(self, port: int = 6795):
        self.port = port
        self.app = web.Application()
        self.websockets: Set[weakref.ref] = set()
        self.activity_store = ActivityStore()
        self.logger = self.setup_logging()
        self.setup_routes()
        self.setup_cors()
        
    def setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger('monitoring_server')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            log_file = os.getenv('MONITORING_LOG_FILE', 'logs/monitoring.log')
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.INFO)
            
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.ERROR)
            
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
        
        return logger
    
    def setup_routes(self):
        """Configure server routes."""
        # WebSocket endpoint
        self.app.router.add_get('/ws', self.websocket_handler)
        
        # REST endpoints
        self.app.router.add_get('/api/health', self.health_check)
        self.app.router.add_post('/api/activities', self.post_activity)
        self.app.router.add_get('/api/activities', self.get_activities)
        self.app.router.add_get('/api/agents', self.get_agents)
        
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
        """Handle WebSocket connections."""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        # Store weak reference
        ws_ref = weakref.ref(ws)
        self.websockets.add(ws_ref)
        
        try:
            # Send initial state
            await ws.send_json({
                'type': 'connection',
                'status': 'connected',
                'timestamp': datetime.utcnow().isoformat()
            })
            
            # Handle messages
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    await self.handle_ws_message(data, ws)
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    self.logger.error(f'WebSocket error: {ws.exception()}')
                    
        except Exception as e:
            self.logger.error(f"WebSocket handler error: {e}")
        finally:
            self.websockets.discard(ws_ref)
            
        return ws
    
    async def handle_ws_message(self, data: Dict[str, Any], ws):
        """Process WebSocket messages."""
        msg_type = data.get('type')
        
        if msg_type == 'activity':
            # Store and broadcast activity
            activity = await self.activity_store.add(data['activity'])
            await self.broadcast_activity(activity)
        elif msg_type == 'ping':
            await ws.send_json({'type': 'pong'})
            
    async def broadcast_activity(self, activity: Dict[str, Any]):
        """Broadcast activity to all connected clients."""
        message = {
            'type': 'activity',
            'activity': activity
        }
        
        # Send to all connected clients
        for ws_ref in list(self.websockets):
            ws = ws_ref()
            if ws is not None:
                try:
                    await ws.send_json(message)
                except ConnectionResetError:
                    self.websockets.discard(ws_ref)
                    
    async def health_check(self, request):
        """Health check endpoint."""
        return web.json_response({
            'status': 'healthy',
            'connections': len(self.websockets),
            'activities': self.activity_store.count()
        })
    
    def run(self):
        """Start the server."""
        print(f"🚀 Monitoring Server starting on port {self.port}")
        print(f"📝 Logs: logs/monitoring.log")
        self.logger.info(f"Monitoring Server starting on port {self.port}")
        
        # Suppress aiohttp access logs to prevent stdout flooding
        web.run_app(
            self.app, 
            host='0.0.0.0', 
            port=self.port,
            access_log=None  # Disable access logging
        )


class ActivityStore:
    """Storage for agent activities."""
    
    def __init__(self, max_memory: int = 10000):
        self.activities = []
        self.max_memory = max_memory
        self.agents = {}
        
    async def add(self, activity: Dict[str, Any]) -> Dict[str, Any]:
        """Add activity to store."""
        # Add timestamp
        activity['stored_at'] = datetime.utcnow().isoformat()
        
        # Update agent info
        agent_id = activity.get('agent_id')
        if agent_id:
            self.agents[agent_id] = {
                'id': agent_id,
                'name': activity.get('agent_name', 'Unknown'),
                'last_seen': activity['stored_at']
            }
        
        # Store activity
        self.activities.append(activity)
        
        # Manage memory
        if len(self.activities) > self.max_memory:
            # TODO: Overflow to disk
            self.activities = self.activities[-self.max_memory:]
            
        return activity
    
    def count(self) -> int:
        """Get activity count."""
        return len(self.activities)


if __name__ == '__main__':
    server = MonitoringServer()
    server.run()
