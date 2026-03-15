"""WebSocket endpoints for real-time communication."""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Dict

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.events import event_manager

router = APIRouter()
logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections."""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_queues: Dict[str, asyncio.Queue] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """Connect a new WebSocket client."""
        await websocket.accept()
        
        # Close existing connection if any
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].close()
            except:
                pass
        
        # Store new connection
        self.active_connections[client_id] = websocket
        
        # Create queue for this client
        queue = asyncio.Queue()
        self.user_queues[client_id] = queue
        
        # Add to event manager
        event_manager.add_connection(queue)
        
        logger.info(f"WebSocket client connected: {client_id}")
        
        # Send welcome message
        await self.send_personal_message({
            "type": "connection",
            "message": "Connected to Audiobook Master v3 WebSocket",
            "client_id": client_id
        }, client_id)
    
    def disconnect(self, client_id: str):
        """Disconnect a WebSocket client."""
        # Remove from active connections
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        
        # Remove queue from event manager
        if client_id in self.user_queues:
            event_manager.remove_connection(self.user_queues[client_id])
            del self.user_queues[client_id]
        
        logger.info(f"WebSocket client disconnected: {client_id}")
    
    async def send_personal_message(self, message: dict, client_id: str):
        """Send a message to a specific client."""
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to send message to {client_id}: {e}")
                self.disconnect(client_id)
    
    async def broadcast(self, message: dict):
        """Broadcast a message to all connected clients."""
        disconnected_clients = []
        
        for client_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to broadcast to {client_id}: {e}")
                disconnected_clients.append(client_id)
        
        # Remove disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id)
    
    async def start_message_forwarder(self, client_id: str):
        """Start forwarding messages from queue to WebSocket."""
        if client_id not in self.user_queues:
            return
        
        queue = self.user_queues[client_id]
        
        try:
            while client_id in self.active_connections:
                try:
                    # Get message from queue (with timeout)
                    message = await asyncio.wait_for(queue.get(), timeout=1.0)
                    
                    # Send to WebSocket
                    await self.send_personal_message(message, client_id)
                    
                except asyncio.TimeoutError:
                    # Check if connection is still active
                    continue
                except Exception as e:
                    logger.error(f"Error forwarding message to {client_id}: {e}")
                    break
                    
        except Exception as e:
            logger.error(f"Message forwarder error for {client_id}: {e}")
        finally:
            self.disconnect(client_id)


# Global connection manager
manager = ConnectionManager()


@router.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    """Main WebSocket endpoint."""
    client_id = f"client_{id(websocket)}"
    
    try:
        await manager.connect(websocket, client_id)
        
        # Start message forwarding
        await manager.start_message_forwarder(client_id)
        
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {client_id}")
    except Exception as e:
        logger.error(f"WebSocket error for {client_id}: {e}")
    finally:
        manager.disconnect(client_id)


@router.websocket("/client/{client_id}")
async def websocket_client_endpoint(
    websocket: WebSocket, 
    client_id: str
):
    """WebSocket endpoint with specific client ID."""
    try:
        await manager.connect(websocket, client_id)
        
        # Start message forwarding
        await manager.start_message_forwarder(client_id)
        
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {client_id}")
    except Exception as e:
        logger.error(f"WebSocket error for {client_id}: {e}")
    finally:
        manager.disconnect(client_id)


@router.post("/trigger-event")
async def trigger_event(
    event_type: str,
    entity: str,
    entity_id: str,
    payload: dict
):
    """Manually trigger an event for testing."""
    try:
        await event_manager.trigger_event(event_type, entity, entity_id, payload)
        
        return {
            "success": True,
            "message": f"Event triggered: {event_type} for {entity} {entity_id}"
        }
        
    except Exception as e:
        logger.error(f"Failed to trigger event: {e}")
        return {
            "success": False,
            "message": f"Failed to trigger event: {str(e)}"
        }


@router.get("/status")
async def websocket_status():
    """Get WebSocket connection status."""
    return {
        "active_connections": len(manager.active_connections),
        "client_ids": list(manager.active_connections.keys()),
        "event_manager_running": event_manager.running
    }
