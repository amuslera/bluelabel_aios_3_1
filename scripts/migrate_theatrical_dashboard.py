#!/usr/bin/env python3
"""
Migration script to safely import the v3.0 theatrical dashboard into v3.1
Preserves existing functionality while adding the enhanced dashboard.
"""

import os
import shutil
import sys
from pathlib import Path
import argparse

def create_backup(target_dir: Path):
    """Create a backup of existing dashboard if it exists."""
    if target_dir.exists():
        backup_dir = target_dir.parent / f"{target_dir.name}_backup_{int(time.time())}"
        print(f"✅ Backing up existing dashboard to: {backup_dir}")
        shutil.copytree(target_dir, backup_dir)
        return backup_dir
    return None

def migrate_theatrical_dashboard(source_root: Path, target_root: Path, dry_run: bool = False):
    """Migrate the theatrical dashboard from v3.0 to v3.1"""
    
    print("🎭 Starting Theatrical Dashboard Migration from v3.0 to v3.1")
    print(f"Source: {source_root}")
    print(f"Target: {target_root}")
    
    # Define source and target paths
    source_theatrical = source_root / "theatrical_monitoring"
    target_theatrical = target_root / "projects" / "theatrical_dashboard"
    
    if not source_theatrical.exists():
        print(f"❌ Source theatrical monitoring not found at: {source_theatrical}")
        return False
    
    # Step 1: Create backup if needed
    if not dry_run and target_theatrical.exists():
        backup_path = create_backup(target_theatrical)
    
    # Step 2: Create target directory structure
    if not dry_run:
        target_theatrical.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created target directory: {target_theatrical}")
    
    # Step 3: Copy core files
    files_to_copy = [
        ("theatrical_monitoring_dashboard.py", "theatrical_dashboard.py"),
        ("theatrical_orchestrator.py", "theatrical_orchestrator.py"),
        ("README.md", "README.md"),
        ("THEATRICAL_MONITORING_TECHNICAL_GUIDE.md", "TECHNICAL_GUIDE.md"),
    ]
    
    for source_file, target_file in files_to_copy:
        source_path = source_theatrical / source_file
        target_path = target_theatrical / target_file
        
        if source_path.exists():
            if not dry_run:
                shutil.copy2(source_path, target_path)
            print(f"✅ Copied: {source_file} -> {target_file}")
        else:
            print(f"⚠️  Skipped (not found): {source_file}")
    
    # Step 4: Copy dashboards directory
    source_dashboards = source_theatrical / "dashboards"
    target_dashboards = target_theatrical / "dashboards"
    
    if source_dashboards.exists():
        if not dry_run:
            shutil.copytree(source_dashboards, target_dashboards, dirs_exist_ok=True)
        print(f"✅ Copied dashboards directory")
    
    # Step 5: Create integration module for v3.1 compatibility
    integration_content = '''"""
Integration module to adapt v3.0 theatrical dashboard for v3.1 agents
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

# Import v3.1 agent implementations
from src.agents.specialists.backend_agent import BackendAgent
from src.agents.specialists.frontend_agent import FrontendAgent
from src.agents.specialists.qa_agent import QAAgent
from src.agents.specialists.devops_agent import DevOpsAgent

# Map v3.0 agent types to v3.1 implementations
AGENT_MAPPING = {
    "backend-001": BackendAgent,
    "frontend-001": FrontendAgent,
    "qa-001": QAAgent,
    "devops-001": DevOpsAgent,
}

def create_v31_agent(agent_id: str, agent_type: str):
    """Create a v3.1 agent instance for the theatrical dashboard."""
    agent_class = AGENT_MAPPING.get(agent_id)
    if agent_class:
        return agent_class()
    return None
'''
    
    integration_path = target_theatrical / "v31_integration.py"
    if not dry_run:
        integration_path.write_text(integration_content)
    print("✅ Created v3.1 integration module")
    
    # Step 6: Create launch script
    launch_content = '''#!/usr/bin/env python3
"""
Launch script for the theatrical dashboard in v3.1
"""

import asyncio
import sys
from pathlib import Path

# Add theatrical dashboard to path
sys.path.insert(0, str(Path(__file__).parent))

from theatrical_dashboard import TheatricalMonitoringApp
from theatrical_orchestrator import TheatricalOrchestrator

async def main():
    """Run the theatrical monitoring dashboard."""
    # Create and run the app
    app = TheatricalMonitoringApp()
    
    # Run the orchestrator in the background
    orchestrator = TheatricalOrchestrator()
    
    # Create tasks for both
    dashboard_task = asyncio.create_task(app.run_async())
    orchestrator_task = asyncio.create_task(orchestrator.run_demo())
    
    # Wait for both to complete
    await asyncio.gather(dashboard_task, orchestrator_task)

if __name__ == "__main__":
    print("🎭 Launching AIOSv3.1 Theatrical Dashboard...")
    print("This shows the v3.0 visualization with v3.1 agents")
    asyncio.run(main())
'''
    
    launch_path = target_theatrical / "launch.py"
    if not dry_run:
        launch_path.write_text(launch_content)
        launch_path.chmod(0o755)  # Make executable
    print("✅ Created launch script")
    
    # Step 7: Update imports in theatrical_dashboard.py for v3.1
    if not dry_run:
        dashboard_path = target_theatrical / "theatrical_dashboard.py"
        if dashboard_path.exists():
            content = dashboard_path.read_text()
            
            # Update imports to use v3.1 paths
            replacements = [
                ("from enhanced_mock_provider import", "# from enhanced_mock_provider import"),
                ("from agents.base.enhanced_agent import", "from src.agents.base.enhanced_agent import"),
                ("from agents.base.types import", "from src.agents.base.types import"),
                ("from core.routing.router import", "from src.core.routing.router import"),
                ("from core.routing.providers.claude import", "from src.core.routing.providers.claude import"),
                ("from core.routing.providers.openai import", "from src.core.routing.providers.openai import"),
            ]
            
            for old, new in replacements:
                content = content.replace(old, new)
            
            dashboard_path.write_text(content)
            print("✅ Updated imports for v3.1 compatibility")
    
    print("\n🎉 Migration completed successfully!")
    print(f"\n📍 Theatrical dashboard installed at: {target_theatrical}")
    print("\n🚀 To run the dashboard:")
    print(f"   cd {target_root}")
    print(f"   python3 projects/theatrical_dashboard/launch.py")
    
    return True

if __name__ == "__main__":
    import time
    
    parser = argparse.ArgumentParser(description="Migrate v3.0 theatrical dashboard to v3.1")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without doing it")
    args = parser.parse_args()
    
    # Define paths
    v3_root = Path("/Users/arielmuslera/Development/Projects/bluelabel-AIOSv3")
    v31_root = Path("/Users/arielmuslera/Development/Projects/bluelabel-AIOSv3.1")
    
    # Verify paths exist
    if not v3_root.exists():
        print(f"❌ v3.0 root not found: {v3_root}")
        sys.exit(1)
    
    if not v31_root.exists():
        print(f"❌ v3.1 root not found: {v31_root}")
        sys.exit(1)
    
    # Run migration
    success = migrate_theatrical_dashboard(v3_root, v31_root, dry_run=args.dry_run)
    sys.exit(0 if success else 1)