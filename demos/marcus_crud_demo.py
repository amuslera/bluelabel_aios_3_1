#!/usr/bin/env python3
"""
Demo: Marcus Chen builds a complete CRUD API for a Task Management System.

This demonstrates Marcus's full capabilities:
- FastAPI code generation
- Database schema design
- API implementation
- Testing suggestions
- Documentation
"""

import asyncio
import logging
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.agents.specialists.backend_agent import create_marcus_agent
from src.agents.base.types import Task, TaskType, TaskPriority


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

console = Console()


async def demonstrate_marcus():
    """Run the Marcus CRUD API demo."""
    console.print("\n[bold blue]🚀 Marcus Chen - Backend Agent Demo[/bold blue]\n")
    console.print("Watch as Marcus builds a complete Task Management API!\n")
    
    # Create Marcus
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task_id = progress.add_task("Initializing Marcus Chen...", total=None)
        
        marcus = await create_marcus_agent(agent_id="marcus_demo")
        await marcus.on_start()
        
        progress.update(task_id, completed=True)
    
    console.print("[green]✅ Marcus is ready![/green]\n")
    
    # Task 1: Design the database schema
    console.print(Panel.fit(
        "[bold]Task 1: Database Schema Design[/bold]\n"
        "Marcus will design a database schema for our task management system.",
        title="📊 Database Design",
        border_style="cyan"
    ))
    
    db_task = Task(
        type=TaskType.DATABASE_DESIGN,
        description=(
            "Design a database schema for a task management system. "
            "We need to track tasks with title, description, status, priority, "
            "assignee, due date, and timestamps. Tasks can have multiple tags "
            "and comments. Users can be assigned to multiple tasks."
        ),
        priority=TaskPriority.HIGH,
        data={"project": "TaskManager"}
    )
    
    console.print("\n[yellow]Marcus is thinking...[/yellow]\n")
    db_result = await marcus.execute_task(db_task)
    
    # Display database design results
    console.print(Panel(
        db_result[:1500] + "...\n\n[dim](Schema truncated for display)[/dim]",
        title="Database Schema Result",
        border_style="green"
    ))
    
    # Task 2: Generate the FastAPI project
    console.print("\n" + Panel.fit(
        "[bold]Task 2: FastAPI Project Generation[/bold]\n"
        "Now Marcus will create the complete FastAPI project structure.",
        title="🏗️ API Generation",
        border_style="cyan"
    ))
    
    api_task = Task(
        type=TaskType.CODE_GENERATION,
        description=(
            "Create a complete FastAPI project for the task management system. "
            "Include all CRUD endpoints for tasks, user authentication, "
            "and proper error handling. Use the database schema we just designed."
        ),
        priority=TaskPriority.HIGH,
        data={
            "project_name": "TaskManager API",
            "description": "A comprehensive task management API with authentication"
        }
    )
    
    console.print("\n[yellow]Marcus is coding...[/yellow]\n")
    api_result = await marcus.execute_task(api_task)
    
    # Extract and display key files
    if "main.py" in api_result:
        # Find main.py content
        main_start = api_result.find("### main.py")
        if main_start != -1:
            main_end = api_result.find("### ", main_start + 1)
            main_content = api_result[main_start:main_end] if main_end != -1 else api_result[main_start:main_start+1000]
            
            console.print(Panel(
                Syntax(main_content, "python", theme="monokai", line_numbers=True),
                title="main.py (Preview)",
                border_style="green"
            ))
    
    # Task 3: Generate specific CRUD endpoints
    console.print("\n" + Panel.fit(
        "[bold]Task 3: Task CRUD Endpoints[/bold]\n"
        "Marcus will now generate specific CRUD endpoints for tasks.",
        title="🔧 CRUD Implementation",
        border_style="cyan"
    ))
    
    crud_task = Task(
        type=TaskType.CODE_GENERATION,
        description="Generate CRUD endpoints for the Task resource with all fields from our schema",
        priority=TaskPriority.MEDIUM,
        data={
            "resource": "Task",
            "fields": {
                "title": "str",
                "description": "Optional[str]",
                "status": "str = 'pending'",
                "priority": "int = 5",
                "assignee_id": "Optional[int]",
                "due_date": "Optional[datetime]",
                "completed_at": "Optional[datetime]",
            }
        }
    )
    
    console.print("\n[yellow]Marcus is implementing CRUD operations...[/yellow]\n")
    crud_result = await marcus.execute_task(crud_task)
    
    # Show CRUD summary
    crud_table = Table(title="Generated CRUD Endpoints", show_header=True, header_style="bold magenta")
    crud_table.add_column("Method", style="cyan", width=8)
    crud_table.add_column("Endpoint", style="green")
    crud_table.add_column("Description", style="white")
    
    crud_table.add_row("GET", "/tasks", "List all tasks with pagination")
    crud_table.add_row("GET", "/tasks/{id}", "Get a specific task by ID")
    crud_table.add_row("POST", "/tasks", "Create a new task")
    crud_table.add_row("PUT", "/tasks/{id}", "Update an existing task")
    crud_table.add_row("DELETE", "/tasks/{id}", "Delete a task")
    
    console.print(crud_table)
    
    # Task 4: Add testing suggestions
    console.print("\n" + Panel.fit(
        "[bold]Task 4: Testing Strategy[/bold]\n"
        "Finally, Marcus will suggest a testing approach.",
        title="🧪 Testing",
        border_style="cyan"
    ))
    
    test_task = Task(
        type=TaskType.TESTING,
        description="Create a test suite for the task management API endpoints",
        priority=TaskPriority.MEDIUM
    )
    
    console.print("\n[yellow]Marcus is writing tests...[/yellow]\n")
    test_result = await marcus.execute_task(test_task)
    
    console.print(Panel(
        test_result[:800] + "...\n\n[dim](Tests truncated for display)[/dim]",
        title="Test Suite",
        border_style="green"
    ))
    
    # Show Marcus's status
    console.print("\n[bold cyan]📊 Marcus's Final Status[/bold cyan]\n")
    status = await marcus.get_status_report()
    
    status_table = Table(show_header=False, box=None)
    status_table.add_column("Metric", style="cyan")
    status_table.add_column("Value", style="green")
    
    status_table.add_row("Tasks Completed", str(len(marcus.task_history)))
    status_table.add_row("Design Decisions", str(status["design_decisions_count"]))
    status_table.add_row("Mood", marcus.dynamic_personality.state.mood.value)
    status_table.add_row("Energy Level", marcus.dynamic_personality.state.energy.name)
    
    console.print(status_table)
    
    # Collaboration demo
    console.print("\n[bold cyan]💬 Collaboration Demo[/bold cyan]\n")
    console.print("Marcus can collaborate with other agents via message queue:")
    
    # Simulate collaboration
    await marcus.broadcast_to_team(
        "Just finished the Task Management API! It includes full CRUD operations, "
        "authentication, and comprehensive error handling. Ready for frontend integration! 🎉",
        priority="high"
    )
    
    console.print("[green]✅ Broadcast sent to team![/green]")
    
    # Clean up
    await marcus.on_stop()
    
    console.print("\n[bold green]🎉 Demo Complete![/bold green]\n")
    console.print("Marcus successfully built:")
    console.print("- Complete database schema with relationships")
    console.print("- Full FastAPI project structure")
    console.print("- CRUD endpoints with validation")
    console.print("- Test suite with pytest")
    console.print("- Documentation and error handling\n")


async def main():
    """Run the demo."""
    try:
        await demonstrate_marcus()
    except KeyboardInterrupt:
        console.print("\n[red]Demo interrupted by user[/red]")
    except Exception as e:
        console.print(f"\n[red]Error during demo: {e}[/red]")
        raise


if __name__ == "__main__":
    asyncio.run(main())