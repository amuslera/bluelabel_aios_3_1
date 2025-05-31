#!/usr/bin/env python3
"""
Debug connection issues
"""

import asyncio
import json
import websockets
import logging
import traceback

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def debug_connection():
    """Debug connection step by step."""
    try:
        logger.info("1. Connecting to ws://localhost:8765...")
        websocket = await websockets.connect("ws://localhost:8765")
        logger.info("2. Connection established!")
        
        logger.info("3. Waiting for welcome message...")
        welcome_msg = await websocket.recv()
        logger.info(f"4. Received welcome: {welcome_msg}")
        
        logger.info("5. Sending registration...")
        reg_message = {
            "type": "register",
            "id": "debug_client",
            "role": "test",
            "name": "Debug Client",
            "terminal_id": "debug_terminal"
        }
        await websocket.send(json.dumps(reg_message))
        logger.info("6. Registration sent!")
        
        logger.info("7. Waiting for sync_state...")
        try:
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            logger.info(f"8. Received response: {response}")
        except asyncio.TimeoutError:
            logger.error("8. Timeout waiting for response!")
        
        await websocket.close()
        logger.info("9. Connection closed cleanly")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(debug_connection())