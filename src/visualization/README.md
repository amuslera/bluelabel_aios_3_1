# AI Agent Visualization System

Professional-grade real-time visualization for AI agent collaboration with enhanced interactivity and session analysis.

## Quick Start

### If you see solid borders:
```bash
python3 src/visualization/quick_interactive_demo.py
```

### If you see dotted/dashed borders:
```bash
python3 src/visualization/ascii_demo.py
```

## Available Demos

### Enhanced Interactive Demos
- **`interactive_demo.py`** - Full interactive experience with keyboard controls
- **`quick_interactive_demo.py`** - Quick showcase of enhanced features (30 seconds)

### ASCII Compatibility Demos  
- **`ascii_demo.py`** - Solid ASCII borders for all terminals
- **`ascii_visualizer.py`** - Test ASCII visualization components

### Feature Testing
- **`test_enhanced_features.py`** - Comprehensive feature validation
- **`test_border_fix.py`** - Border rendering verification

### Original Demos
- **`final_demo.py`** - Complete 6-phase sprint simulation
- **`quick_final_demo.py`** - Quick demonstration
- **`showcase_demo.py`** - Feature showcase

## Terminal Compatibility

### Border Rendering Issues?

Some terminals may display Unicode box drawing characters as dotted or dashed lines instead of solid borders.

**Solutions:**
1. **ASCII Version** (Recommended): Use `ascii_demo.py` for guaranteed solid borders
2. **Terminal Settings**: Enable Unicode/UTF-8 support in your terminal
3. **Font Issues**: Try a different monospace font that supports box drawing

### Supported Terminals
- ✅ **ASCII Version**: Works on ALL terminals
- ✅ macOS Terminal, iTerm2
- ✅ Linux Terminal, GNOME Terminal  
- ✅ Windows Terminal, PowerShell
- ⚠️ **Unicode Version**: May show dotted lines in some configurations

## Features

### Enhanced Visualization (Sprint 2.6)
- **Scrollable Chat History**: Navigate with ↑↓ arrows, PgUp/PgDn
- **Interactive Session Menu**: Post-completion menu with 8 options
- **Advanced Search**: Find messages in chat history with filtering
- **Professional Keyboard Navigation**: Real-time controls
- **Complete Session Export**: JSON audit trails with all interactions
- **Action History**: Track last 3-4 actions per agent

### Core Visualization
- **Live Agent Activities**: Real-time work progress display
- **Team Communication**: Chat with agent identification
- **Workflow Tracking**: Sprint progress visualization  
- **Metrics Dashboard**: Live counters and statistics
- **Theatrical Pacing**: Human-comprehensible speed control

## Usage Examples

### Basic Demo
```bash
# Standard version with Unicode borders
python3 src/visualization/quick_interactive_demo.py

# ASCII version with solid borders  
python3 src/visualization/ascii_demo.py
```

### Interactive Experience
```bash
# Full interactive demo with keyboard controls
python3 src/visualization/interactive_demo.py

# Controls:
# ↑↓ - Scroll chat history
# PgUp/PgDn - Page navigation  
# m - Open session menu
# q - Quit
```

### Testing
```bash
# Test all enhanced features
python3 src/visualization/test_enhanced_features.py

# Test border rendering
python3 src/visualization/test_border_fix.py
```

## Architecture

### Core Components
- **`enhanced_visualizer.py`** - Main visualization engine with Unicode borders
- **`ascii_visualizer.py`** - ASCII-only version for compatibility
- **`interactive_demo.py`** - Full interactive demonstration
- **`ascii_demo.py`** - ASCII compatibility demonstration

### Key Classes
- **`EnhancedVisualizer`** - Main visualization system
- **`ASCIIVisualizer`** - ASCII-compatible visualization
- **`ChatHistoryManager`** - Scrollable chat with search
- **`SessionMenu`** - Interactive post-completion menu
- **`KeyboardHandler`** - Cross-platform keyboard input

### Export Format
Session data is exported as JSON with:
- Session metadata and timing
- Complete chat history
- Agent action history
- Final metrics and workflow status
- Timestamped event logs

## Troubleshooting

### Dotted Borders
**Problem**: Seeing dotted/dashed lines instead of solid borders  
**Solution**: Use the ASCII version: `python3 src/visualization/ascii_demo.py`

### Keyboard Controls Not Working
**Problem**: Arrow keys or menu not responding  
**Solution**: Ensure terminal supports raw input mode, try different terminal

### Unicode Display Issues
**Problem**: Emojis or special characters not displaying  
**Solution**: Check terminal UTF-8 support, use ASCII version as fallback

### Performance Issues
**Problem**: Slow rendering or high CPU usage  
**Solution**: Reduce refresh rate, close other terminal applications

## Development

### Adding New Demos
1. Create new demo script in `src/visualization/`
2. Import required classes from `enhanced_visualizer.py` or `ascii_visualizer.py`
3. Follow existing demo patterns for consistency
4. Add to README.md documentation

### Extending Functionality
1. **New Agent Types**: Add to `_initialize_agents()` method
2. **New Activity Types**: Extend `ActivityType` enum
3. **New Panel Types**: Add render methods to visualizer classes
4. **New Export Formats**: Extend `export_session_log()` method

## Files Overview

```
src/visualization/
├── enhanced_visualizer.py     # Main visualization engine (689 lines)
├── ascii_visualizer.py        # ASCII-compatible version (548 lines)
├── interactive_demo.py        # Full interactive experience (536 lines)
├── ascii_demo.py             # ASCII demonstration (173 lines)
├── quick_interactive_demo.py  # Quick feature showcase (173 lines)
├── test_enhanced_features.py  # Feature testing (129 lines)
├── test_border_fix.py        # Border rendering test (65 lines)
├── final_demo.py             # Complete sprint simulation
├── quick_final_demo.py       # Quick demonstration
└── showcase_demo.py          # Feature showcase
```

**Total**: 2,000+ lines of visualization code with comprehensive demos and testing.

## Status

✅ **Phase 2.6 Complete** - Enhanced visualization system fully operational  
✅ **ASCII Compatibility** - Universal terminal support  
✅ **Interactive Features** - Scrollable chat, session menu, keyboard controls  
✅ **Production Ready** - Complete session export and analysis capabilities

Ready for Phase 3: Production Hardening 🚀