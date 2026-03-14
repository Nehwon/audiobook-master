"""Packet model for publication bundles."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Integer, String, Text, Boolean, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class PacketStatus(str, Enum):
    """Packet status enumeration."""
    DRAFT = "draft"
    READY = "ready"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"


class Packet(Base):
    """Publication packet model."""
    
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Status and progress
    status: Mapped[PacketStatus] = mapped_column(
        String(20), 
        default=PacketStatus.DRAFT, 
        nullable=False,
        index=True
    )
    
    # Files in packet
    files: Mapped[list] = mapped_column(
        JSON, 
        nullable=False,
        default=list
    )
    
    # Metadata
    packet_metadata: Mapped[Optional[dict]] = mapped_column(
        JSON, 
        nullable=True,
        default={}
    )
    
    # Publication settings
    changelog_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    channels: Mapped[list] = mapped_column(
        JSON, 
        nullable=False,
        default=list
    )
    
    # Timing
    published_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        nullable=True
    )
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        nullable=True
    )
    
    # Publication results
    publication_results: Mapped[Optional[dict]] = mapped_column(
        JSON, 
        nullable=True,
        default={}
    )
    
    # User information
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        String(36), 
        nullable=True,
        index=True
    )
    
    # Job association
    job_ids: Mapped[list] = mapped_column(
        JSON, 
        nullable=False,
        default=list
    )
    
    def to_dict(self) -> dict:
        """Convert packet to dictionary with additional fields."""
        data = super().to_dict()
        data.update({
            "file_count": len(self.files) if self.files else 0,
            "is_published": self.status == PacketStatus.PUBLISHED,
            "is_ready": self.status == PacketStatus.READY,
            "time_since_creation": self.calculate_time_since_creation(),
        })
        return data
    
    def calculate_time_since_creation(self) -> Optional[float]:
        """Calculate time since creation in seconds."""
        return (datetime.utcnow() - self.created_at).total_seconds()
    
    def add_file(self, file_path: str, metadata: Optional[dict] = None) -> None:
        """Add a file to the packet."""
        if not self.files:
            self.files = []
        
        file_info = {
            "path": file_path,
            "added_at": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        self.files.append(file_info)
    
    def remove_file(self, file_path: str) -> bool:
        """Remove a file from the packet."""
        if self.files:
            original_length = len(self.files)
            self.files = [
                f for f in self.files 
                if f.get("path") != file_path
            ]
            return len(self.files) < original_length
        return False
    
    def add_channel(self, channel: str) -> None:
        """Add a publication channel."""
        if not self.channels:
            self.channels = []
        if channel not in self.channels:
            self.channels.append(channel)
    
    def remove_channel(self, channel: str) -> bool:
        """Remove a publication channel."""
        if self.channels and channel in self.channels:
            self.channels.remove(channel)
            return True
        return False
    
    def mark_ready(self) -> None:
        """Mark packet as ready for publication."""
        self.status = PacketStatus.READY
    
    def start_publishing(self) -> None:
        """Start the publishing process."""
        self.status = PacketStatus.PUBLISHING
    
    def complete_publishing(self, results: dict) -> None:
        """Complete the publishing process."""
        self.status = PacketStatus.PUBLISHED
        self.published_at = datetime.utcnow()
        self.publication_results = results
    
    def fail_publishing(self, error_message: str) -> None:
        """Fail the publishing process."""
        self.status = PacketStatus.FAILED
        self.publication_results = {
            "error": error_message,
            "failed_at": datetime.utcnow().isoformat()
        }
    
    def can_publish(self) -> bool:
        """Check if packet can be published."""
        return (
            self.status == PacketStatus.READY and 
            self.files and 
            len(self.files) > 0
        )
    
    def __repr__(self) -> str:
        return f"<Packet(id={self.id}, title={self.title}, status={self.status})>"
