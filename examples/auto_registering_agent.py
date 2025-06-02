#!/usr/bin/env python3
"""
Example agent with automatic monitoring server registration.

This demonstrates how agents can automatically register with the monitoring
server and send heartbeats without manual intervention.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from agents.base.monitoring_agent import MonitoringAgent
from agents.base.agent import AgentConfig, Task, TaskType, Priority
from agents.base.types import AgentType


class ExampleAgent(MonitoringAgent):
    """Example agent that demonstrates auto-registration capabilities."""
    
    async def _execute_task_internal(self, task: Task, model_id: str) -> dict:
        """Execute a simple task - just simulate some work."""
        # Simulate some work
        await asyncio.sleep(1)
        
        # Report progress
        await self.send_custom_metric("task_progress", 0.5)
        
        # Do more work
        await asyncio.sleep(1)
        
        # Report completion
        await self.report_milestone(f"Completed task of type {task.type}")
        
        return {
            "message": f"Successfully processed task: {task.description}",
            "timestamp": datetime.utcnow().isoformat(),
            "model_used": model_id,
            "task_id": task.id
        }
    
    def can_handle_task(self, task: Task) -> bool:
        """This agent can handle general and test tasks."""
        return task.type in ["general", "test", "example"] or "general" in self.capabilities


async def main():
    """Run the example agent."""
    # Create agent configuration
    config = AgentConfig(
        name="Example Agent",
        description="An example agent demonstrating auto-registration",
        agent_type=AgentType.GENERALIST,
        capabilities=["general", "test", "example", "demonstration"],
        model_preferences={"primary": "claude-3-sonnet"},
        max_concurrent_tasks=2,
        heartbeat_interval=10  # Send heartbeat every 10 seconds
    )
    
    # Create the agent
    agent = ExampleAgent(
        config=config,
        monitoring_url=os.getenv('MONITORING_URL', 'http://localhost:6795'),
        api_key=os.getenv('MONITORING_API_KEY', 'aios_default_key')
    )
    
    try:
        print(f"🚀 Starting {agent.name}")
        
        # Start the agent (will auto-register)
        await agent.start()
        
        print(f"✅ {agent.name} started and registered")
        
        # Create and execute some example tasks
        tasks = [
            Task(
                type="test",
                description="Test task 1: Simple greeting",
                priority=Priority.HIGH
            ),
            Task(
                type="example", 
                description="Example task: Data processing simulation",
                priority=Priority.MEDIUM
            ),
            Task(
                type="general",
                description="General task: Status check",
                priority=Priority.LOW
            )
        ]
        
        print(f"📋 Executing {len(tasks)} tasks...")
        
        # Execute tasks
        for i, task in enumerate(tasks, 1):
            print(f"  Task {i}/{len(tasks)}: {task.description}")
            result = await agent.execute_task(task)
            print(f"  ✅ Result: {result.status} in {result.execution_time:.2f}s")
            
            # Small delay between tasks
            await asyncio.sleep(2)
        
        # Report overall completion
        await agent.report_milestone("All example tasks completed", {
            "total_tasks": len(tasks),
            "execution_duration": "approximately 10 seconds"
        })
        
        print("🎉 All tasks completed! Agent will continue running...")
        print("💡 Check the monitoring server dashboard to see agent status")
        print("⏹️  Press Ctrl+C to stop the agent")
        
        # Keep running until interrupted
        try:
            while True:
                await asyncio.sleep(5)
                
                # Periodically send a custom metric
                await agent.send_custom_metric("example_metric", {
                    "timestamp": datetime.utcnow().isoformat(),
                    "status": "running",
                    "iterations": getattr(agent, '_iterations', 0) + 1
                })
                agent._iterations = getattr(agent, '_iterations', 0) + 1
                
        except KeyboardInterrupt:
            print("\\n🛑 Shutdown requested...")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        await agent.report_issue(f"Agent error: {str(e)}", "error")
    
    finally:
        # Stop the agent (will auto-unregister)
        await agent.stop()
        print(f"👋 {agent.name} stopped and unregistered")


if __name__ == "__main__":
    print("🤖 AIOSv3 Auto-Registering Agent Example")
    print("=" * 50)
    
    # Check if monitoring server is specified
    monitoring_url = os.getenv('MONITORING_URL', 'http://localhost:6795')
    api_key = os.getenv('MONITORING_API_KEY', 'aios_default_key')
    
    print(f"📡 Monitoring Server: {monitoring_url}")
    print(f"🔑 API Key: {api_key[:12]}...")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\\n👋 Goodbye!")