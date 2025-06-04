"""
Simple orchestrator for agent coordination.
Human-in-the-loop for now, automation later.
"""
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from ..communication.message_bus import SimpleMessageBus

class SimpleOrchestrator:
    """Coordinates agent activities through file-based messaging."""
    
    def __init__(self, workspace_dir: str = "workspace"):
        self.workspace = Path(workspace_dir)
        self.message_bus = SimpleMessageBus(workspace_dir)
        self.agents = {}  # agent_name -> agent_instance
        self.task_queue = []
        self.completed_tasks = []
        self.log_file = self.workspace / "orchestrator.log"
        
    def register_agent(self, agent):
        """Register an agent with the orchestrator."""
        self.agents[agent.name] = agent
        self.log(f"Registered agent: {agent.name} ({agent.role})")
    
    def create_task(self, task_type: str, description: str, assigned_to: str, **kwargs) -> Dict[str, Any]:
        """Create a new task."""
        task = {
            "id": f"task_{int(time.time() * 1000)}",
            "type": task_type,
            "description": description,
            "assigned_to": assigned_to,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            **kwargs
        }
        
        self.task_queue.append(task)
        self.log(f"Created task {task['id']} for {assigned_to}: {description}")
        
        return task
    
    def send_task_to_agent(self, task: Dict[str, Any]):
        """Send a task to an agent via message bus."""
        agent_name = task["assigned_to"]
        
        message = {
            "type": "task",
            "task": task,
            "from": "orchestrator"
        }
        
        msg_id = self.message_bus.send_message(agent_name, message)
        task["message_id"] = msg_id
        task["status"] = "sent"
        
        self.log(f"Sent task {task['id']} to {agent_name} (msg: {msg_id})")
    
    def process_agent_messages(self):
        """Process messages from all agents."""
        for agent_name, agent in self.agents.items():
            # Check for messages
            message = self.message_bus.get_next_message(agent_name)
            
            if message:
                self.log(f"Processing message for {agent_name}: {message.get('type')}")
                
                # Have agent process the message
                response = agent.receive_message(message)
                
                # Mark message as processed
                self.message_bus.mark_processed(agent_name, message["id"])
                
                # Handle response
                self.handle_agent_response(agent_name, response)
    
    def handle_agent_response(self, agent_name: str, response: Dict[str, Any]):
        """Handle response from an agent."""
        response_type = response.get("type")
        
        if response_type == "task_result":
            # Task completed
            task_id = response.get("task_id")
            self.complete_task(task_id, response.get("result"))
            
        elif response_type == "handoff":
            # Agent wants to hand off to another agent
            target_agent = response.get("to_agent")
            self.log(f"Handoff requested: {agent_name} -> {target_agent}")
            
            # Forward the handoff message
            self.message_bus.send_message(target_agent, response)
            
        elif response_type == "error":
            self.log(f"Error from {agent_name}: {response.get('error')}", level="ERROR")
    
    def complete_task(self, task_id: str, result: Dict[str, Any]):
        """Mark a task as completed."""
        # Find task in queue
        task = next((t for t in self.task_queue if t["id"] == task_id), None)
        
        if task:
            task["status"] = "completed"
            task["completed_at"] = datetime.now().isoformat()
            task["result"] = result
            
            # Move to completed
            self.task_queue.remove(task)
            self.completed_tasks.append(task)
            
            self.log(f"Task {task_id} completed: {result.get('output', 'No output')}")
            
            # Check if task generated files
            if "files_created" in result:
                self.log(f"Files created: {result['files_created']}")
    
    def run_single_cycle(self):
        """Run a single orchestration cycle."""
        self.log("=== Orchestration Cycle Start ===")
        
        # Send pending tasks
        for task in self.task_queue:
            if task["status"] == "pending":
                self.send_task_to_agent(task)
        
        # Process agent responses
        self.process_agent_messages()
        
        # Show status
        stats = self.get_status()
        self.log(f"Status: {stats['pending_tasks']} pending, {stats['completed_tasks']} completed")
        
        self.log("=== Orchestration Cycle End ===\n")
    
    def run_interactive(self):
        """Run in interactive mode with human control."""
        print("\n=== Simple Orchestrator Interactive Mode ===")
        print("Commands: task, cycle, status, messages, quit")
        
        while True:
            try:
                cmd = input("\norchestrator> ").strip().lower()
                
                if cmd == "quit":
                    break
                    
                elif cmd == "task":
                    # Create a task
                    agent_name = input("Assign to agent: ")
                    task_type = input("Task type: ")
                    description = input("Description: ")
                    
                    task = self.create_task(task_type, description, agent_name)
                    print(f"Created task: {task['id']}")
                    
                elif cmd == "cycle":
                    # Run one cycle
                    self.run_single_cycle()
                    
                elif cmd == "status":
                    # Show status
                    stats = self.get_status()
                    print(json.dumps(stats, indent=2))
                    
                elif cmd == "messages":
                    # Show message stats
                    stats = self.message_bus.get_message_stats()
                    print(json.dumps(stats, indent=2))
                    
                else:
                    print("Unknown command")
                    
            except KeyboardInterrupt:
                print("\nInterrupted")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get orchestrator status."""
        return {
            "agents": list(self.agents.keys()),
            "pending_tasks": len([t for t in self.task_queue if t["status"] != "completed"]),
            "completed_tasks": len(self.completed_tasks),
            "message_stats": self.message_bus.get_message_stats()
        }
    
    def log(self, message: str, level: str = "INFO"):
        """Log a message."""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        
        # Print to console
        print(f"[Orchestrator] {message}")
        
        # Write to file
        with open(self.log_file, 'a') as f:
            f.write(log_entry)