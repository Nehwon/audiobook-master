"""Packets API endpoints."""

from __future__ import annotations

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from app.core.database import get_db
from app.models.packet import Packet, PacketStatus
from app.schemas.packet import (
    PacketCreate, 
    PacketResponse, 
    PacketUpdate, 
    PacketListResponse, 
    PacketStatsResponse
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=PacketResponse, status_code=201)
async def create_packet(
    packet_data: PacketCreate,
    db: AsyncSession = Depends(get_db)
) -> Packet:
    """Create a new packet."""
    try:
        packet = Packet(**packet_data.dict())
        db.add(packet)
        await db.commit()
        await db.refresh(packet)
        
        logger.info(f"Created packet {packet.id}: {packet.title}")
        return packet
        
    except Exception as e:
        logger.error(f"Failed to create packet: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create packet")


@router.get("/", response_model=PacketListResponse)
async def list_packets(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    status: PacketStatus | None = Query(None, description="Filter by status"),
    db: AsyncSession = Depends(get_db)
) -> PacketListResponse:
    """List packets with pagination."""
    try:
        # Build query
        query = select(Packet)
        
        # Apply status filter
        if status:
            query = query.where(Packet.status == status)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination and ordering
        offset = (page - 1) * per_page
        query = query.order_by(desc(Packet.created_at)).offset(offset).limit(per_page)
        
        # Execute query
        result = await db.execute(query)
        packets = result.scalars().all()
        
        # Calculate pages
        pages = (total + per_page - 1) // per_page
        
        return PacketListResponse(
            packets=packets,
            total=total,
            page=page,
            per_page=per_page,
            pages=pages
        )
        
    except Exception as e:
        logger.error(f"Failed to list packets: {e}")
        raise HTTPException(status_code=500, detail="Failed to list packets")


@router.get("/stats", response_model=PacketStatsResponse)
async def get_packet_stats(db: AsyncSession = Depends(get_db)) -> PacketStatsResponse:
    """Get packet statistics."""
    try:
        # Get status counts
        status_counts = {}
        for status in PacketStatus:
            query = select(func.count(Packet.id)).where(Packet.status == status)
            result = await db.execute(query)
            status_counts[status.value] = result.scalar() or 0
        
        # Get total packets
        total_query = select(func.count(Packet.id))
        total_result = await db.execute(total_query)
        total = total_result.scalar() or 0
        
        # Get total files across all packets
        # This is a simplified calculation - in real implementation you'd sum the file counts
        total_files = 0
        avg_files_per_packet = 0.0
        
        if total > 0:
            # Get all packets to calculate file statistics
            query = select(Packet)
            result = await db.execute(query)
            packets = result.scalars().all()
            
            for packet in packets:
                if packet.files and isinstance(packet.files, list):
                    total_files += len(packet.files)
            
            avg_files_per_packet = total_files / total
        
        # Get recent publications (last 24 hours)
        from datetime import datetime, timedelta
        yesterday = datetime.utcnow() - timedelta(days=1)
        
        recent_query = select(func.count(Packet.id)).where(
            Packet.published_at >= yesterday
        )
        recent_result = await db.execute(recent_query)
        recent_publications = recent_result.scalar() or 0
        
        return PacketStatsResponse(
            total=total,
            draft=status_counts.get("draft", 0),
            ready=status_counts.get("ready", 0),
            publishing=status_counts.get("publishing", 0),
            published=status_counts.get("published", 0),
            failed=status_counts.get("failed", 0),
            avg_files_per_packet=round(avg_files_per_packet, 2),
            total_files=total_files,
            recent_publications=recent_publications
        )
        
    except Exception as e:
        logger.error(f"Failed to get packet stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get packet statistics")


@router.get("/{packet_id}", response_model=PacketResponse)
async def get_packet(
    packet_id: str,
    db: AsyncSession = Depends(get_db)
) -> Packet:
    """Get a specific packet."""
    try:
        query = select(Packet).where(Packet.id == packet_id)
        result = await db.execute(query)
        packet = result.scalar_one_or_none()
        
        if not packet:
            raise HTTPException(status_code=404, detail="Packet not found")
        
        return packet
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get packet {packet_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get packet")


@router.put("/{packet_id}", response_model=PacketResponse)
async def update_packet(
    packet_id: str,
    packet_update: PacketUpdate,
    db: AsyncSession = Depends(get_db)
) -> Packet:
    """Update a packet."""
    try:
        # Get existing packet
        query = select(Packet).where(Packet.id == packet_id)
        result = await db.execute(query)
        packet = result.scalar_one_or_none()
        
        if not packet:
            raise HTTPException(status_code=404, detail="Packet not found")
        
        # Update fields
        update_data = packet_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(packet, field, value)
        
        await db.commit()
        await db.refresh(packet)
        
        logger.info(f"Updated packet {packet_id}")
        return packet
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update packet {packet_id}: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update packet")


@router.delete("/{packet_id}", status_code=204)
async def delete_packet(
    packet_id: str,
    db: AsyncSession = Depends(get_db)
) -> None:
    """Delete a packet."""
    try:
        # Get existing packet
        query = select(Packet).where(Packet.id == packet_id)
        result = await db.execute(query)
        packet = result.scalar_one_or_none()
        
        if not packet:
            raise HTTPException(status_code=404, detail="Packet not found")
        
        # Check if packet can be deleted
        if packet.status == PacketStatus.PUBLISHING:
            raise HTTPException(
                status_code=400, 
                detail="Cannot delete a packet that is currently publishing"
            )
        
        await db.delete(packet)
        await db.commit()
        
        logger.info(f"Deleted packet {packet_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete packet {packet_id}: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete packet")


@router.post("/{packet_id}/publish", response_model=PacketResponse)
async def publish_packet(
    packet_id: str,
    db: AsyncSession = Depends(get_db)
) -> Packet:
    """Publish a packet."""
    try:
        # Get existing packet
        query = select(Packet).where(Packet.id == packet_id)
        result = await db.execute(query)
        packet = result.scalar_one_or_none()
        
        if not packet:
            raise HTTPException(status_code=404, detail="Packet not found")
        
        # Check if packet can be published
        if not packet.can_publish():
            raise HTTPException(
                status_code=400,
                detail="Packet is not ready for publication"
            )
        
        # Start publishing process
        packet.start_publishing()
        
        await db.commit()
        await db.refresh(packet)
        
        logger.info(f"Started publishing packet {packet_id}")
        
        # TODO: Trigger actual publishing process
        # This would typically be handled by a background task
        
        return packet
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to publish packet {packet_id}: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to publish packet")


@router.post("/{packet_id}/files", response_model=PacketResponse)
async def add_file_to_packet(
    packet_id: str,
    file_path: str,
    metadata: dict = {},
    db: AsyncSession = Depends(get_db)
) -> Packet:
    """Add a file to a packet."""
    try:
        # Get existing packet
        query = select(Packet).where(Packet.id == packet_id)
        result = await db.execute(query)
        packet = result.scalar_one_or_none()
        
        if not packet:
            raise HTTPException(status_code=404, detail="Packet not found")
        
        # Check if packet can be modified
        if packet.status in [PacketStatus.PUBLISHING, PacketStatus.PUBLISHED]:
            raise HTTPException(
                status_code=400,
                detail="Cannot modify a packet that is publishing or published"
            )
        
        # Add file
        packet.add_file(file_path, metadata)
        
        await db.commit()
        await db.refresh(packet)
        
        logger.info(f"Added file {file_path} to packet {packet_id}")
        return packet
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to add file to packet {packet_id}: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to add file to packet")


@router.delete("/{packet_id}/files", response_model=PacketResponse)
async def remove_file_from_packet(
    packet_id: str,
    file_path: str,
    db: AsyncSession = Depends(get_db)
) -> Packet:
    """Remove a file from a packet."""
    try:
        # Get existing packet
        query = select(Packet).where(Packet.id == packet_id)
        result = await db.execute(query)
        packet = result.scalar_one_or_none()
        
        if not packet:
            raise HTTPException(status_code=404, detail="Packet not found")
        
        # Check if packet can be modified
        if packet.status in [PacketStatus.PUBLISHING, PacketStatus.PUBLISHED]:
            raise HTTPException(
                status_code=400,
                detail="Cannot modify a packet that is publishing or published"
            )
        
        # Remove file
        if not packet.remove_file(file_path):
            raise HTTPException(
                status_code=404,
                detail="File not found in packet"
            )
        
        await db.commit()
        await db.refresh(packet)
        
        logger.info(f"Removed file {file_path} from packet {packet_id}")
        return packet
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to remove file from packet {packet_id}: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to remove file from packet")
