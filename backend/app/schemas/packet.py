"""Packet schemas for API serialization."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.packet import PacketStatus


class PacketBase(BaseModel):
    """Base packet schema."""
    title: str = Field(..., min_length=1, max_length=255, description="Packet title")
    description: Optional[str] = Field(None, description="Packet description")
    metadata: Optional[dict] = Field(default={}, description="Packet metadata")
    changelog_message: Optional[str] = Field(None, description="Changelog message")
    channels: list[str] = Field(default=[], description="Publication channels")


class PacketCreate(PacketBase):
    """Schema for creating a packet."""
    files: list[str] = Field(..., min_items=1, description="List of file paths")
    job_ids: list[str] = Field(default=[], description="Associated job IDs")
    user_id: Optional[str] = Field(None, description="User ID")
    scheduled_at: Optional[datetime] = Field(None, description="Scheduled publication time")


class PacketUpdate(BaseModel):
    """Schema for updating a packet."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[PacketStatus] = None
    metadata: Optional[dict] = None
    changelog_message: Optional[str] = None
    channels: Optional[list[str]] = None
    scheduled_at: Optional[datetime] = None


class PacketResponse(PacketBase):
    """Schema for packet response."""
    id: str = Field(..., description="Packet ID")
    status: PacketStatus = Field(..., description="Packet status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    published_at: Optional[datetime] = Field(None, description="Publication timestamp")
    scheduled_at: Optional[datetime] = Field(None, description="Scheduled publication time")
    
    # File information
    files: list[dict] = Field(..., description="Files in packet")
    job_ids: list[str] = Field(..., description="Associated job IDs")
    
    # Publication information
    publication_results: Optional[dict] = Field(None, description="Publication results")
    user_id: Optional[str] = Field(None, description="User ID")
    
    # Computed fields
    file_count: int = Field(..., description="Number of files")
    is_published: bool = Field(..., description="Whether packet is published")
    is_ready: bool = Field(..., description="Whether packet is ready for publication")
    time_since_creation: Optional[float] = Field(None, description="Time since creation in seconds")
    
    class Config:
        from_attributes = True


class PacketListResponse(BaseModel):
    """Schema for packet list response."""
    packets: list[PacketResponse] = Field(..., description="List of packets")
    total: int = Field(..., description="Total number of packets")
    page: int = Field(default=1, description="Current page")
    per_page: int = Field(default=20, description="Items per page")


class PacketStatsResponse(BaseModel):
    """Schema for packet statistics response."""
    total: int = Field(..., description="Total packets")
    draft: int = Field(..., description="Draft packets")
    ready: int = Field(..., description="Ready packets")
    publishing: int = Field(..., description="Publishing packets")
    published: int = Field(..., description="Published packets")
    failed: int = Field(..., description="Failed packets")
    
    # Additional metrics
    avg_files_per_packet: float = Field(..., description="Average files per packet")
    total_files: int = Field(..., description="Total files across all packets")
    recent_publications: int = Field(..., description="Publications in last 24 hours")


class FileItem(BaseModel):
    """Schema for file item in packet."""
    path: str = Field(..., description="File path")
    size: Optional[int] = Field(None, description="File size in bytes")
    mime_type: Optional[str] = Field(None, description="File MIME type")
    added_at: datetime = Field(..., description="When file was added")
    metadata: Optional[dict] = Field(default={}, description="File metadata")


class ChannelConfig(BaseModel):
    """Schema for publication channel configuration."""
    name: str = Field(..., description="Channel name")
    enabled: bool = Field(default=True, description="Whether channel is enabled")
    config: Optional[dict] = Field(default={}, description="Channel-specific config")
    last_published_at: Optional[datetime] = Field(None, description="Last publication time")
