"""
SQLite database layer for monitoring server.
Handles persistent storage of activities and agent data.
"""

import asyncio
import aiosqlite
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

class MonitoringDatabase:
    """SQLite database for monitoring data persistence."""
    
    def __init__(self, db_path: str = "monitoring.db"):
        self.db_path = db_path
        self.db = None
        
    async def initialize(self):
        """Initialize database and create tables."""
        self.db = await aiosqlite.connect(self.db_path)
        await self.create_tables()
        await self.create_indexes()
        
    async def create_tables(self):
        """Create necessary database tables."""
        await self.db.executescript("""
            CREATE TABLE IF NOT EXISTS activities (
                id TEXT PRIMARY KEY,
                agent_id TEXT,
                agent_name TEXT,
                activity_type TEXT,
                status TEXT,
                message TEXT,
                metadata TEXT,
                api_key TEXT,
                stored_at TIMESTAMP,
                created_at TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS agents (
                id TEXT PRIMARY KEY,
                name TEXT,
                status TEXT,
                capabilities TEXT,
                last_seen TIMESTAMP,
                first_seen TIMESTAMP,
                total_activities INTEGER DEFAULT 0
            );
            
            CREATE TABLE IF NOT EXISTS api_keys (
                key_hash TEXT PRIMARY KEY,
                name TEXT,
                created_at TIMESTAMP,
                last_used TIMESTAMP,
                usage_count INTEGER DEFAULT 0
            );
        """)
        await self.db.commit()
        
    async def create_indexes(self):
        """Create database indexes for performance."""
        await self.db.executescript("""
            CREATE INDEX IF NOT EXISTS idx_activities_agent_id ON activities(agent_id);
            CREATE INDEX IF NOT EXISTS idx_activities_stored_at ON activities(stored_at);
            CREATE INDEX IF NOT EXISTS idx_activities_type ON activities(activity_type);
            CREATE INDEX IF NOT EXISTS idx_agents_last_seen ON agents(last_seen);
        """)
        await self.db.commit()
        
    async def store_activity(self, activity: Dict[str, Any]) -> str:
        """Store activity in database."""
        activity_id = activity.get('id')
        agent_id = activity.get('agent_id')
        
        await self.db.execute("""
            INSERT INTO activities (
                id, agent_id, agent_name, activity_type, status, 
                message, metadata, api_key, stored_at, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            activity_id,
            agent_id,
            activity.get('agent_name'),
            activity.get('type'),
            activity.get('status'),
            activity.get('message'),
            json.dumps(activity.get('metadata', {})),
            activity.get('api_key'),
            activity.get('stored_at'),
            activity.get('timestamp', activity.get('stored_at'))
        ))
        
        # Update agent info
        if agent_id:
            await self.update_agent(agent_id, activity)
            
        await self.db.commit()
        return activity_id
        
    async def update_agent(self, agent_id: str, activity: Dict[str, Any]):
        """Update agent information."""
        agent_name = activity.get('agent_name', 'Unknown')
        status = activity.get('status', 'active')
        
        # Check if agent exists
        cursor = await self.db.execute(
            "SELECT id FROM agents WHERE id = ?", (agent_id,)
        )
        exists = await cursor.fetchone()
        
        if exists:
            # Update existing agent
            await self.db.execute("""
                UPDATE agents SET 
                    name = ?, status = ?, last_seen = ?, 
                    total_activities = total_activities + 1
                WHERE id = ?
            """, (agent_name, status, activity.get('stored_at'), agent_id))
        else:
            # Create new agent
            await self.db.execute("""
                INSERT INTO agents (
                    id, name, status, last_seen, first_seen, total_activities
                ) VALUES (?, ?, ?, ?, ?, 1)
            """, (
                agent_id, agent_name, status, 
                activity.get('stored_at'), activity.get('stored_at')
            ))
            
    async def get_activities(
        self, 
        limit: int = 100, 
        since: Optional[datetime] = None,
        agent_id: Optional[str] = None,
        activity_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get activities with filtering."""
        query = "SELECT * FROM activities WHERE 1=1"
        params = []
        
        if since:
            query += " AND stored_at > ?"
            params.append(since.isoformat())
            
        if agent_id:
            query += " AND agent_id = ?"
            params.append(agent_id)
            
        if activity_type:
            query += " AND activity_type = ?"
            params.append(activity_type)
            
        query += " ORDER BY stored_at DESC LIMIT ?"
        params.append(limit)
        
        cursor = await self.db.execute(query, params)
        rows = await cursor.fetchall()
        
        activities = []
        for row in rows:
            activity = {
                'id': row[0],
                'agent_id': row[1],
                'agent_name': row[2],
                'type': row[3],
                'status': row[4],
                'message': row[5],
                'metadata': json.loads(row[6]) if row[6] else {},
                'api_key': row[7],
                'stored_at': row[8],
                'timestamp': row[9]
            }
            activities.append(activity)
            
        return activities
        
    async def get_agents(self) -> List[Dict[str, Any]]:
        """Get all agents with their status."""
        cursor = await self.db.execute("""
            SELECT id, name, status, last_seen, first_seen, total_activities
            FROM agents ORDER BY last_seen DESC
        """)
        rows = await cursor.fetchall()
        
        agents = []
        for row in rows:
            agent = {
                'id': row[0],
                'name': row[1],
                'status': row[2],
                'last_seen': row[3],
                'first_seen': row[4],
                'total_activities': row[5]
            }
            agents.append(agent)
            
        return agents
        
    async def get_activity_count(self) -> int:
        """Get total activity count."""
        cursor = await self.db.execute("SELECT COUNT(*) FROM activities")
        row = await cursor.fetchone()
        return row[0] if row else 0
        
    async def cleanup_old_activities(self, days: int = 30):
        """Clean up activities older than specified days."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        cursor = await self.db.execute(
            "DELETE FROM activities WHERE stored_at < ?", 
            (cutoff.isoformat(),)
        )
        deleted = cursor.rowcount
        await self.db.commit()
        
        return deleted
        
    async def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics."""
        stats = {}
        
        # Activity counts
        cursor = await self.db.execute("SELECT COUNT(*) FROM activities")
        stats['total_activities'] = (await cursor.fetchone())[0]
        
        # Agent counts
        cursor = await self.db.execute("SELECT COUNT(*) FROM agents")
        stats['total_agents'] = (await cursor.fetchone())[0]
        
        # Activities in last 24 hours
        yesterday = datetime.utcnow() - timedelta(days=1)
        cursor = await self.db.execute(
            "SELECT COUNT(*) FROM activities WHERE stored_at > ?",
            (yesterday.isoformat(),)
        )
        stats['activities_24h'] = (await cursor.fetchone())[0]
        
        # Active agents (seen in last hour)
        last_hour = datetime.utcnow() - timedelta(hours=1)
        cursor = await self.db.execute(
            "SELECT COUNT(*) FROM agents WHERE last_seen > ?",
            (last_hour.isoformat(),)
        )
        stats['active_agents'] = (await cursor.fetchone())[0]
        
        return stats
        
    async def close(self):
        """Close database connection."""
        if self.db:
            await self.db.close()
            
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()