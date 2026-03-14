"""Event handling for PostgreSQL notifications and WebSocket broadcasting."""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Dict, List

from sqlalchemy.ext.asyncio import AsyncSession
from asyncpg import connect

from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class EventManager:
    """Manages PostgreSQL notifications and WebSocket broadcasting."""
    
    def __init__(self):
        self.connections: List[asyncio.Queue] = []
        self.pg_connection = None
        self.listener_task = None
        self.running = False
    
    async def start(self):
        """Start the event manager."""
        if self.running:
            return
        
        self.running = True
        self.listener_task = asyncio.create_task(self._listen_postgres())
        logger.info("Event manager started")
    
    async def stop(self):
        """Stop the event manager."""
        self.running = False
        if self.listener_task:
            self.listener_task.cancel()
            try:
                await self.listener_task
            except asyncio.CancelledError:
                pass
        
        if self.pg_connection:
            await self.pg_connection.close()
        
        logger.info("Event manager stopped")
    
    async def _listen_postgres(self):
        """Listen to PostgreSQL notifications."""
        try:
            # Extract connection details from DATABASE_URL
            db_url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
            self.pg_connection = await connect(db_url)
            
            await self.pg_connection.add_listener(
                settings.PG_NOTIFY_CHANNEL, 
                self._on_pg_notification
            )
            
            logger.info(f"Listening to PostgreSQL channel: {settings.PG_NOTIFY_CHANNEL}")
            
            # Keep the connection alive
            while self.running:
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Error in PostgreSQL listener: {e}")
            self.running = False
    
    def _on_pg_notification(self, connection, pid, channel, payload):
        """Handle PostgreSQL notification."""
        try:
            event_data = json.loads(payload)
            asyncio.create_task(self._broadcast_event(event_data))
        except Exception as e:
            logger.error(f"Error processing notification: {e}")
    
    async def _broadcast_event(self, event_data: Dict[str, Any]):
        """Broadcast event to all connected WebSocket clients."""
        if not self.connections:
            return
        
        # Add timestamp if not present
        if "timestamp" not in event_data:
            from datetime import datetime, timezone
            event_data["timestamp"] = datetime.now(timezone.utc).isoformat()
        
        # Send to all connections
        disconnected = []
        for i, connection in enumerate(self.connections):
            try:
                await connection.put(event_data)
            except Exception as e:
                logger.warning(f"Failed to send to connection {i}: {e}")
                disconnected.append(i)
        
        # Remove disconnected connections
        for i in reversed(disconnected):
            self.connections.pop(i)
    
    def add_connection(self, connection: asyncio.Queue):
        """Add a WebSocket connection."""
        self.connections.append(connection)
        logger.info(f"Added connection. Total: {len(self.connections)}")
    
    def remove_connection(self, connection: asyncio.Queue):
        """Remove a WebSocket connection."""
        try:
            self.connections.remove(connection)
            logger.info(f"Removed connection. Total: {len(self.connections)}")
        except ValueError:
            pass
    
    async def trigger_event(self, event_type: str, entity: str, entity_id: str, payload: Dict[str, Any]):
        """Manually trigger an event."""
        event_data = {
            "schema_version": 1,
            "event_type": event_type,
            "entity": entity,
            "entity_id": entity_id,
            "payload": payload,
        }
        
        await self._broadcast_event(event_data)


# Global event manager instance
event_manager = EventManager()
