#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_dpa\tasks\models.py #python #source_code  
**Category:** Source Code  
**Status:** Active
"""









# Models

**Created:** 2024-10-15  
**Updated:** 2025-07-26 10:26:57  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_dpa\tasks\models.py #python #source_code  
**Category:** Source Code  
**Status:** Active

"""
Task and Reminder Data Models for ImpressionCore Personal Assistant

This module defines the core data structures for task management and reminders,
providing a foundation for the task management system with proper typing and
validation.

Created: 2025-01-03
Author: GitHub Copilot
Version: 1.0
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid


class TaskPriority(Enum):
    """Task priority levels with numeric values for sorting"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5


class TaskStatus(Enum):
    """Task lifecycle status"""
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    WAITING = "waiting"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"


class TriggerType(Enum):
    """Reminder trigger types"""
    TIME_ABSOLUTE = "time_absolute"      # Specific datetime
    TIME_RELATIVE = "time_relative"      # Relative to creation/due date
    TIME_RECURRING = "time_recurring"    # Recurring pattern
    LOCATION = "location"                # Location-based
    EVENT = "event"                      # Event-based
    CONDITIONAL = "conditional"          # Conditional logic


class NotificationType(Enum):
    """Notification delivery methods"""
    POPUP = "popup"
    SOUND = "sound"
    EMAIL = "email"
    SMS = "sms"
    VOICE = "voice"
    VISUAL = "visual"
    SYSTEM = "system"


class RecurrencePattern(Enum):
    """Recurring task patterns"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    CUSTOM = "custom"


@dataclass
class TaskMetadata:
    """Extended task metadata"""
    estimated_duration: Optional[int] = None  # minutes
    actual_duration: Optional[int] = None
    difficulty_level: Optional[int] = None    # 1-5 scale
    energy_required: Optional[int] = None     # 1-5 scale
    location: Optional[str] = None
    tools_required: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)  # Task IDs
    subtasks: List[str] = field(default_factory=list)      # Task IDs
    attachments: List[str] = field(default_factory=list)   # File paths
    url_references: List[str] = field(default_factory=list)
    notes: Optional[str] = None


@dataclass
class Task:
    """Core task data structure"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: Optional[str] = None
    category: str = "general"
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.CREATED
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    due_date: Optional[datetime] = None
    start_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Organization
    tags: List[str] = field(default_factory=list)
    project: Optional[str] = None
    
    # Progress tracking
    progress_percentage: int = 0
    
    # Reminders and recurrence
    reminders: List[str] = field(default_factory=list)  # Reminder IDs
    is_recurring: bool = False
    recurrence_pattern: Optional[RecurrencePattern] = None
    recurrence_interval: Optional[int] = None
    
    # Extended metadata
    metadata: TaskMetadata = field(default_factory=TaskMetadata)
    
    # System fields
    user_id: Optional[str] = None
    is_archived: bool = False
    is_deleted: bool = False
    
    def __post_init__(self):
        """Post-initialization validation and setup"""
        if not self.title:
            raise ValueError("Task title cannot be empty")
        
        # Ensure updated_at is current
        self.updated_at = datetime.now()
        
        # Validate progress percentage
        if not 0 <= self.progress_percentage <= 100:
            raise ValueError("Progress percentage must be between 0 and 100")
    
    def update_status(self, new_status: TaskStatus):
        """Update task status with timestamp tracking"""
        self.status = new_status
        self.updated_at = datetime.now()
        
        if new_status == TaskStatus.COMPLETED:
            self.completed_at = datetime.now()
            self.progress_percentage = 100
    
    def add_tag(self, tag: str):
        """Add a tag if not already present"""
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.now()
    
    def remove_tag(self, tag: str):
        """Remove a tag if present"""
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.now()
    
    def is_overdue(self) -> bool:
        """Check if task is overdue"""
        if not self.due_date:
            return False
        return datetime.now() > self.due_date and self.status != TaskStatus.COMPLETED
    
    def days_until_due(self) -> Optional[int]:
        """Calculate days until due date"""
        if not self.due_date:
            return None
        delta = self.due_date - datetime.now()
        return delta.days
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary for serialization"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'priority': self.priority.value,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'tags': self.tags,
            'project': self.project,
            'progress_percentage': self.progress_percentage,
            'reminders': self.reminders,
            'is_recurring': self.is_recurring,
            'recurrence_pattern': self.recurrence_pattern.value if self.recurrence_pattern else None,
            'recurrence_interval': self.recurrence_interval,
            'metadata': {
                'estimated_duration': self.metadata.estimated_duration,
                'actual_duration': self.metadata.actual_duration,
                'difficulty_level': self.metadata.difficulty_level,
                'energy_required': self.metadata.energy_required,
                'location': self.metadata.location,
                'tools_required': self.metadata.tools_required,
                'dependencies': self.metadata.dependencies,
                'subtasks': self.metadata.subtasks,
                'attachments': self.metadata.attachments,
                'url_references': self.metadata.url_references,
                'notes': self.metadata.notes
            },
            'user_id': self.user_id,
            'is_archived': self.is_archived,
            'is_deleted': self.is_deleted
        }


@dataclass
class ReminderMetadata:
    """Extended reminder metadata"""
    snooze_count: int = 0
    max_snooze_count: int = 3
    snooze_duration: int = 15  # minutes
    urgency_level: int = 1     # 1-5 scale
    sound_file: Optional[str] = None
    custom_message: Optional[str] = None
    requires_acknowledgment: bool = False
    auto_reschedule: bool = False


@dataclass
class Reminder:
    """Core reminder data structure"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_id: str = ""
    
    # Trigger configuration
    trigger_type: TriggerType = TriggerType.TIME_ABSOLUTE
    trigger_value: Any = None  # Flexible trigger value based on type
    
    # Notification configuration
    message: str = ""
    notification_type: NotificationType = NotificationType.POPUP
    
    # State management
    is_active: bool = True
    is_snoozed: bool = False
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_triggered: Optional[datetime] = None
    next_trigger: Optional[datetime] = None
    snoozed_until: Optional[datetime] = None
    
    # Extended metadata
    metadata: ReminderMetadata = field(default_factory=ReminderMetadata)
    
    # System fields
    user_id: Optional[str] = None
    
    def __post_init__(self):
        """Post-initialization validation and setup"""
        if not self.task_id:
            raise ValueError("Reminder must be associated with a task")
        
        if not self.message:
            raise ValueError("Reminder message cannot be empty")
        
        self.updated_at = datetime.now()
    
    def snooze(self, duration_minutes: Optional[int] = None):
        """Snooze the reminder for specified duration"""
        if self.metadata.snooze_count >= self.metadata.max_snooze_count:
            raise ValueError("Maximum snooze count reached")
        
        duration = duration_minutes or self.metadata.snooze_duration
        self.is_snoozed = True
        self.snoozed_until = datetime.now().replace(
            minute=datetime.now().minute + duration
        )
        self.metadata.snooze_count += 1
        self.updated_at = datetime.now()
    
    def acknowledge(self):
        """Acknowledge the reminder"""
        self.is_active = False
        self.updated_at = datetime.now()
    
    def trigger(self):
        """Mark reminder as triggered"""
        self.last_triggered = datetime.now()
        self.updated_at = datetime.now()
        
        # Handle auto-reschedule for recurring reminders
        if self.metadata.auto_reschedule and self.trigger_type == TriggerType.TIME_RECURRING:
            self._schedule_next_occurrence()
    
    def _schedule_next_occurrence(self):
        """Schedule next occurrence for recurring reminders"""
        # This would be implemented based on recurrence pattern
        # For now, placeholder implementation
        pass
    
    def is_due(self) -> bool:
        """Check if reminder is due to trigger"""
        if not self.is_active or self.is_snoozed:
            return False
        
        if self.next_trigger:
            return datetime.now() >= self.next_trigger
        
        # For simple time-based triggers
        if self.trigger_type == TriggerType.TIME_ABSOLUTE and isinstance(self.trigger_value, datetime):
            return datetime.now() >= self.trigger_value
        
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert reminder to dictionary for serialization"""
        return {
            'id': self.id,
            'task_id': self.task_id,
            'trigger_type': self.trigger_type.value,
            'trigger_value': str(self.trigger_value),
            'message': self.message,
            'notification_type': self.notification_type.value,
            'is_active': self.is_active,
            'is_snoozed': self.is_snoozed,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'last_triggered': self.last_triggered.isoformat() if self.last_triggered else None,
            'next_trigger': self.next_trigger.isoformat() if self.next_trigger else None,
            'snoozed_until': self.snoozed_until.isoformat() if self.snoozed_until else None,
            'metadata': {
                'snooze_count': self.metadata.snooze_count,
                'max_snooze_count': self.metadata.max_snooze_count,
                'snooze_duration': self.metadata.snooze_duration,
                'urgency_level': self.metadata.urgency_level,
                'sound_file': self.metadata.sound_file,
                'custom_message': self.metadata.custom_message,
                'requires_acknowledgment': self.metadata.requires_acknowledgment,
                'auto_reschedule': self.metadata.auto_reschedule
            },
            'user_id': self.user_id
        }


# Type aliases for convenience
TaskDict = Dict[str, Any]
ReminderDict = Dict[str, Any]
TaskList = List[Task]
ReminderList = List[Reminder]
