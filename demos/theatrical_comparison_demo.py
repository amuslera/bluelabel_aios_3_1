#!/usr/bin/env python3
"""
Theatrical Dashboard Comparison Demo

Shows different theatrical dashboard options available in v3.1:
1. Simple standalone demo (no agents)
2. Standard theatrical dashboard (mock LLM)
3. Advanced theatrical dashboard (real LLM option)
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def print_menu():
    """Print the demo menu"""
    print("\n" + "=" * 60)
    print("🎭 AIOSv3.1 Theatrical Dashboard Options")
    print("=" * 60)
    print("\n1. Simple Standalone Demo ✅ WORKING")
    print("   - Beautiful Rich-based UI simulation")
    print("   - No real agents or LLM calls")
    print("   - Perfect for quick demonstrations")
    print("\n2. Minimal Theatrical Dashboard ✅ WORKING")
    print("   - Clean Rich-based dashboard UI")
    print("   - Mock agents (no complex setup)")
    print("   - Real-time updates and metrics")
    print("\n3. NEW: Textual Dashboard (v3.0 Style) 🆕 RECOMMENDED")
    print("   - Uses Textual framework like v3.0")
    print("   - Tabbed interface with rich UI")
    print("   - Mock agents, no complex setup")
    print("\n4. Standard Theatrical Dashboard ⚠️  EXPERIMENTAL")
    print("   - Real v3.1 agent integration")
    print("   - May have initialization issues")
    print("\n5. Original v3.0 Textual Dashboard ❌ INCOMPATIBLE")
    print("   - Requires fixing import issues")
    print("   - Different architecture than v3.1")
    print("\nQ. Quit")
    print("-" * 60)


async def run_simple_demo():
    """Run the simple standalone demo"""
    print("\n🎬 Starting Simple Standalone Demo...")
    print("This is a lightweight simulation with no real agents.\n")
    
    # Import and run the standalone demo
    from theatrical_demo_standalone import TheatricalDemo
    demo = TheatricalDemo()
    await demo.run()


async def run_minimal_dashboard():
    """Run the minimal theatrical dashboard"""
    print("\n🎬 Starting Minimal Theatrical Dashboard...")
    print("This uses mock agents for a clean demonstration.\n")
    
    from src.visualization.theatrical_dashboard_minimal import MinimalTheatricalDashboard
    dashboard = MinimalTheatricalDashboard()
    await dashboard.run()


async def run_textual_dashboard():
    """Run the new Textual-based dashboard"""
    print("\n🎬 Starting Textual Dashboard (v3.0 Style)...")
    print("This recreates the v3.0 design using Textual framework.\n")
    
    try:
        import textual
        print("✅ Textual is installed")
    except ImportError:
        print("❌ Textual is not installed!")
        print("\nTo install Textual, run:")
        print("  pip3 install textual")
        return
    
    from src.visualization.theatrical_dashboard_textual import TheatricalDashboard
    
    print("\nStarting dashboard...")
    print("Use Tab to switch between tabs, click buttons with mouse.")
    print("Press Ctrl+C to exit.\n")
    
    app = TheatricalDashboard()
    await app.run_async()


async def run_standard_dashboard():
    """Run the standard theatrical dashboard"""
    print("\n🎬 Starting Standard Theatrical Dashboard...")
    print("This integrates real v3.1 agents with mock LLM responses.\n")
    
    from src.visualization.theatrical_dashboard import TheatricalDashboard
    dashboard = TheatricalDashboard()
    await dashboard.run()


async def run_advanced_dashboard():
    """Run the advanced theatrical dashboard"""
    print("\n🎬 Starting Advanced Theatrical Dashboard...")
    print("This is the full-featured dashboard with all capabilities.\n")
    
    # Ask about LLM mode
    use_real_llm = input("Use real LLM API calls? (y/N): ").lower() == 'y'
    
    if use_real_llm:
        print("\n⚠️  WARNING: Real LLM calls will incur API costs!")
        confirm = input("Continue? (y/N): ").lower() == 'y'
        if not confirm:
            print("Cancelled.")
            return
    
    from src.visualization.theatrical_dashboard_advanced import AdvancedTheatricalDashboard
    dashboard = AdvancedTheatricalDashboard()
    
    # Configure for real LLM if requested
    if use_real_llm:
        dashboard.config['show_raw_llm'] = True
        print("\n🔴 LIVE LLM MODE ENABLED - Real API calls will be made!")
    else:
        print("\n🟢 MOCK MODE - No real API calls")
    
    await dashboard.run(demo_mode=True)


async def run_original_dashboard():
    """Try to run the original v3.0 dashboard"""
    print("\n🎬 Attempting to start Original v3.0 Dashboard...")
    
    try:
        # Check if the theatrical dashboard exists
        theatrical_path = project_root / "projects" / "theatrical_dashboard"
        if not theatrical_path.exists():
            print("❌ Original v3.0 dashboard not found in projects/theatrical_dashboard/")
            print("   The dashboard files may need to be migrated first.")
            return
            
        # Try to import and run
        sys.path.insert(0, str(theatrical_path))
        from theatrical_dashboard import TheatricalDashboard as V30Dashboard
        
        print("✅ Found v3.0 dashboard! Starting...")
        print("\n⚠️  Note: This may have compatibility issues with v3.1 agents.")
        
        # The v3.0 dashboard uses Textual and runs differently
        app = V30Dashboard()
        await app.run_async()
        
    except ImportError as e:
        print(f"❌ Could not import v3.0 dashboard: {e}")
        print("   You may need to install additional dependencies (textual)")
    except Exception as e:
        print(f"❌ Error running v3.0 dashboard: {e}")


async def main():
    """Main demo runner"""
    print("🎭 Welcome to AIOSv3.1 Theatrical Dashboard Demo!")
    print("This showcases different visualization options for agent monitoring.")
    
    while True:
        print_menu()
        choice = input("\nSelect option (1-4, Q): ").strip().upper()
        
        try:
            if choice == '1':
                await run_simple_demo()
            elif choice == '2':
                await run_minimal_dashboard()
            elif choice == '3':
                await run_textual_dashboard()
            elif choice == '4':
                await run_standard_dashboard()
            elif choice == '5':
                await run_original_dashboard()
            elif choice == 'Q':
                print("\n✨ Thanks for exploring the theatrical dashboards!")
                break
            else:
                print("\n❌ Invalid choice. Please try again.")
                
        except KeyboardInterrupt:
            print("\n\n⚠️  Demo interrupted by user")
        except Exception as e:
            print(f"\n\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            
        # Pause before showing menu again
        if choice in ['1', '2', '3', '4']:
            input("\nPress Enter to return to menu...")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")