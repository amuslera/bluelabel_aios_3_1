#!/usr/bin/env python3
"""
Simple Real Task Demo - Creates actual utility files

This demo creates real files in a sandbox directory to demonstrate
what the agents would produce.
"""

import os
import shutil
from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
from rich.syntax import Syntax


def create_string_formatter():
    """Create the string formatter utility code"""
    return '''"""
String Formatting Utilities

Provides various string manipulation and formatting functions.
"""

from typing import Optional


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate a string to a maximum length with a suffix.
    
    Args:
        text: The string to truncate
        max_length: Maximum length of the output string
        suffix: Suffix to add when truncating (default: "...")
        
    Returns:
        Truncated string with suffix if needed
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def snake_to_camel(snake_str: str) -> str:
    """Convert snake_case to camelCase."""
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def camel_to_snake(camel_str: str) -> str:
    """Convert camelCase to snake_case."""
    result = []
    for i, char in enumerate(camel_str):
        if char.isupper() and i > 0:
            result.append('_')
        result.append(char.lower())
    return ''.join(result)


def format_file_size(bytes_size: int) -> str:
    """Format bytes into human-readable size."""
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    size = float(bytes_size)
    unit_index = 0
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"
    return f"{size:.1f} {units[unit_index]}"


def pluralize(word: str, count: int) -> str:
    """Simple English word pluralization."""
    if count == 1:
        return word
    
    if word.endswith('y') and len(word) > 1 and word[-2] not in 'aeiou':
        return word[:-1] + 'ies'
    elif word.endswith(('s', 'x', 'z', 'ch', 'sh')):
        return word + 'es'
    else:
        return word + 's'
'''


def create_test_code():
    """Create test code for the utility"""
    return '''"""
Unit tests for string_formatter module.
"""

import pytest
from src.utils.string_formatter import (
    truncate_string, snake_to_camel, camel_to_snake,
    format_file_size, pluralize
)


def test_truncate_string():
    """Test string truncation."""
    assert truncate_string("hello", 10) == "hello"
    assert truncate_string("hello world", 8) == "hello..."
    assert truncate_string("test", 10, "…") == "test"


def test_snake_to_camel():
    """Test snake_case to camelCase conversion."""
    assert snake_to_camel("hello_world") == "helloWorld"
    assert snake_to_camel("test_case_name") == "testCaseName"
    assert snake_to_camel("single") == "single"


def test_camel_to_snake():
    """Test camelCase to snake_case conversion."""
    assert camel_to_snake("helloWorld") == "hello_world"
    assert camel_to_snake("testCaseName") == "test_case_name"
    assert camel_to_snake("single") == "single"


def test_format_file_size():
    """Test file size formatting."""
    assert format_file_size(100) == "100 B"
    assert format_file_size(1024) == "1.0 KB"
    assert format_file_size(1536) == "1.5 KB"
    assert format_file_size(1048576) == "1.0 MB"


def test_pluralize():
    """Test word pluralization."""
    assert pluralize("cat", 1) == "cat"
    assert pluralize("cat", 2) == "cats"
    assert pluralize("baby", 2) == "babies"
    assert pluralize("box", 2) == "boxes"
    assert pluralize("boy", 2) == "boys"
'''


def run_simple_demo():
    """Run the simple demo that creates real files"""
    console = Console()
    
    # Welcome screen
    console.clear()
    console.print(Panel(
        Align.center(
            Text.from_markup(
                "[bold cyan]Simple Real Task Demo[/bold cyan]\n\n"
                "[yellow]Creating String Formatter Utility[/yellow]\n\n"
                "This demo will create real files:\n"
                "• Python utility module\n"
                "• Comprehensive test suite\n"
                "• All in a sandbox directory\n\n"
                "[bold green]Let's see what agents would create![/bold green]",
                justify="center"
            )
        ),
        title="Real File Demo",
        border_style="blue"
    ))
    
    input("\nPress Enter to continue...")
    
    # Create sandbox
    sandbox_dir = "sandbox_demo"
    if os.path.exists(sandbox_dir):
        console.print(f"\n[yellow]Cleaning existing sandbox...[/yellow]")
        shutil.rmtree(sandbox_dir)
    
    os.makedirs(f"{sandbox_dir}/src/utils", exist_ok=True)
    os.makedirs(f"{sandbox_dir}/tests/unit", exist_ok=True)
    
    console.print(f"\n[green]✓ Created sandbox: {sandbox_dir}/[/green]")
    
    # Create utility file
    console.print("\n[bold]Creating utility module...[/bold]")
    utility_code = create_string_formatter()
    
    with open(f"{sandbox_dir}/src/utils/string_formatter.py", "w") as f:
        f.write(utility_code)
    
    # Create __init__ files
    for path in [
        f"{sandbox_dir}/src/__init__.py",
        f"{sandbox_dir}/src/utils/__init__.py", 
        f"{sandbox_dir}/tests/__init__.py",
        f"{sandbox_dir}/tests/unit/__init__.py"
    ]:
        open(path, "w").close()
    
    console.print("[green]✅ Created src/utils/string_formatter.py[/green]")
    
    # Show a sample of the code
    console.print("\n[bold]Sample of generated utility code:[/bold]")
    syntax = Syntax(utility_code[:500] + "\n...", "python", theme="monokai", line_numbers=True)
    console.print(syntax)
    
    # Create test file
    console.print("\n[bold]Creating test suite...[/bold]")
    test_code = create_test_code()
    
    with open(f"{sandbox_dir}/tests/unit/test_string_formatter.py", "w") as f:
        f.write(test_code)
    
    console.print("[green]✅ Created tests/unit/test_string_formatter.py[/green]")
    
    # Show test sample
    console.print("\n[bold]Sample of generated test code:[/bold]")
    syntax = Syntax(test_code[:400] + "\n...", "python", theme="monokai", line_numbers=True)
    console.print(syntax)
    
    # Summary
    console.print("\n" + "="*60)
    console.print("[bold green]✨ Task Complete![/bold green]")
    console.print("="*60)
    
    console.print(f"\n[bold]Files created in '{sandbox_dir}':[/bold]")
    console.print("📁 sandbox_demo/")
    console.print("  📁 src/")
    console.print("    📁 utils/")
    console.print("      📄 string_formatter.py (5 utility functions)")
    console.print("  📁 tests/")
    console.print("    📁 unit/")
    console.print("      📄 test_string_formatter.py (15+ test cases)")
    
    console.print("\n[dim]This demonstrates what our AI agents would create[/dim]")
    console.print("[dim]when given a real development task.[/dim]")
    
    console.print(f"\n[yellow]Sandbox location: {os.path.abspath(sandbox_dir)}/[/yellow]")
    
    # Cleanup option
    console.print("\n[bold]Options:[/bold]")
    console.print("1. Keep the sandbox files for inspection")
    console.print("2. Clean up the sandbox")
    
    choice = input("\nYour choice (1 or 2): ").strip()
    
    if choice == "2":
        shutil.rmtree(sandbox_dir)
        console.print("[green]✅ Sandbox cleaned up[/green]")
    else:
        console.print(f"[green]✅ Files kept in {sandbox_dir}/[/green]")


if __name__ == "__main__":
    try:
        run_simple_demo()
    except KeyboardInterrupt:
        print("\n\nDemo cancelled by user")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()