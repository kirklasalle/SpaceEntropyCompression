#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_dpa\reminders\reminder_engine.py #python #source_code  
**Category:** Source Code  
**Status:** Active
"""









# Reminder Engine

**Created:** 2024-10-15  
**Updated:** 2025-07-26 10:26:57  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_dpa\reminders\reminder_engine.py #python #source_code  
**Category:** Source Code  
**Status:** Active

"""
Reminder Engine for ImpressionCore Personal Assistant

This module provides intelligent reminder functionality with multiple trigger types,
adaptive notifications, and context-aware reminder delivery.

Created: 2025-01-03
Author: GitHub Copilot
Version: 1.0
"""

import json
import logging
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from ..tasks.models import (
    Reminder, TriggerType, NotificationType,
    ReminderList, ReminderDict
)
from ..tasks.models import Task
from ...core.utils.rich_logging import setup_rich_logging
from ...core.utils.rich_status_animation import StatusAnimation


class ReminderEngine:
    """
    Intelligent reminder engine with multiple trigger types and adaptive notifications.
    Handles context-aware reminder delivery and user behavior learning.
    """
    
    def __init__(self, storage_path: Optional[str] = None, user_id: Optional[str] = None):
        """Initialize reminder engine"""
        self.logger = setup_rich_logging(__name__)
        self.user_id = user_id
        self.storage_path = Path(storage_path or "src/user_data/reminders")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Reminder storage
        self._reminders: Dict[str, Reminder] = {}
        self._active_reminders: Dict[str, Reminder] = {}
        
        # Notification callbacks
        self._notification_handlers: Dict[NotificationType, Callable] = {}
        
        # Engine state
        self._running = False
        self._check_interval = 30  # seconds
        self._engine_thread: Optional[threading.Thread] = None
        
        # Load existing reminders
        self._load_reminders()
        
        # Setup default notification handlers
        self._setup_default_handlers()
        
        self.logger.info("ReminderEngine initialized", extra={
            "storage_path": str(self.storage_path),
            "user_id": self.user_id,
            "reminder_count": len(self._reminders)
        })
    
    def create_reminder(self,
                       task_id: str,
                       message: str,
                       trigger_type: TriggerType,
                       trigger_value: Any,
                       notification_type: NotificationType = NotificationType.POPUP,
                       **kwargs) -> Reminder:
        """
        Create a new reminder
        
        Args:
            task_id: Associated task ID
            message: Reminder message
            trigger_type: Type of trigger
            trigger_value: Trigger-specific value
            notification_type: How to deliver the notification
            **kwargs: Additional reminder parameters
        
        Returns:
            Created Reminder object
        """
        animation = StatusAnimation(
            total_steps=4,
            description="Creating reminder"
        )
        
        try:
            animation.start()
            
            # Step 1: Validate input
            animation.update(1, "Validating input")
            if not task_id:
                raise ValueError("Task ID is required")
            if not message:
                raise ValueError("Reminder message is required")
            
            # Step 2: Create reminder
            animation.update(2, "Creating reminder")
            reminder = Reminder(
                task_id=task_id,
                message=message,
                trigger_type=trigger_type,
                trigger_value=trigger_value,
                notification_type=notification_type,
                user_id=self.user_id,
                **kwargs
            )
            
            # Step 3: Calculate next trigger time
            animation.update(3, "Calculating trigger time")
            reminder.next_trigger = self._calculate_next_trigger(reminder)
            
            # Step 4: Store reminder
            animation.update(4, "Storing reminder")
            self._reminders[reminder.id] = reminder
            if reminder.is_active:
                self._active_reminders[reminder.id] = reminder
            
            self._save_reminder(reminder)
            
            animation.complete("Reminder created successfully")
            
            self.logger.info("Reminder created", extra={
                "reminder_id": reminder.id,
                "task_id": task_id,
                "trigger_type": trigger_type.value,
                "next_trigger": reminder.next_trigger.isoformat() if reminder.next_trigger else None
            })
            
            return reminder
            
        except Exception as e:
            animation.fail(f"Failed to create reminder: {str(e)}")
            self.logger.error("Reminder creation failed", extra={
                "task_id": task_id,
                "error": str(e)
            })
            raise
    
    def get_reminder(self, reminder_id: str) -> Optional[Reminder]:
        """Retrieve a reminder by ID"""
        return self._reminders.get(reminder_id)
    
    def update_reminder(self, reminder_id: str, **updates) -> bool:
        """Update a reminder with new information"""
        reminder = self._reminders.get(reminder_id)
        if not reminder:
            self.logger.warning("Reminder not found for update", extra={"reminder_id": reminder_id})
            return False
        
        # Track changes
        changes = {}
        
        # Update allowed fields
        updatable_fields = {
            'message', 'trigger_type', 'trigger_value', 'notification_type',
            'is_active', 'is_snoozed'
        }
        
        for field, value in updates.items():
            if field in updatable_fields and hasattr(reminder, field):
                old_value = getattr(reminder, field)
                if old_value != value:
                    setattr(reminder, field, value)
                    changes[field] = {'old': old_value, 'new': value}
        
        if changes:
            reminder.updated_at = datetime.now()
            
            # Recalculate trigger time if trigger info changed
            if any(field in changes for field in ['trigger_type', 'trigger_value']):
                reminder.next_trigger = self._calculate_next_trigger(reminder)
            
            # Update active reminders
            if reminder.is_active and reminder.id not in self._active_reminders:
                self._active_reminders[reminder.id] = reminder
            elif not reminder.is_active and reminder.id in self._active_reminders:
                del self._active_reminders[reminder.id]
            
            self._save_reminder(reminder)
            
            self.logger.info("Reminder updated", extra={
                "reminder_id": reminder_id,
                "changes": changes
            })
        
        return True
    
    def cancel_reminder(self, reminder_id: str) -> bool:
        """Cancel (deactivate) a reminder"""
        reminder = self._reminders.get(reminder_id)
        if not reminder:
            return False
        
        reminder.is_active = False
        reminder.updated_at = datetime.now()
        
        if reminder_id in self._active_reminders:
            del self._active_reminders[reminder_id]
        
        self._save_reminder(reminder)
        
        self.logger.info("Reminder cancelled", extra={
            "reminder_id": reminder_id
        })
        
        return True
    
    def snooze_reminder(self, reminder_id: str, duration_minutes: Optional[int] = None) -> bool:
        """Snooze a reminder for specified duration"""
        reminder = self._reminders.get(reminder_id)
        if not reminder:
            return False
        
        try:
            reminder.snooze(duration_minutes)
            
            # Update next trigger time
            reminder.next_trigger = reminder.snoozed_until
            
            self._save_reminder(reminder)
            
            self.logger.info("Reminder snoozed", extra={
                "reminder_id": reminder_id,
                "snoozed_until": reminder.snoozed_until.isoformat() if reminder.snoozed_until else None,
                "snooze_count": reminder.metadata.snooze_count
            })
            
            return True
            
        except ValueError as e:
            self.logger.warning("Failed to snooze reminder", extra={
                "reminder_id": reminder_id,
                "error": str(e)
            })
            return False
    
    def acknowledge_reminder(self, reminder_id: str) -> bool:
        """Acknowledge a reminder"""
        reminder = self._reminders.get(reminder_id)
        if not reminder:
            return False
        
        reminder.acknowledge()
        
        if reminder_id in self._active_reminders:
            del self._active_reminders[reminder_id]
        
        self._save_reminder(reminder)
        
        self.logger.info("Reminder acknowledged", extra={
            "reminder_id": reminder_id
        })
        
        return True
    
    def get_reminders_for_task(self, task_id: str) -> ReminderList:
        """Get all reminders for a specific task"""
        return [r for r in self._reminders.values() if r.task_id == task_id]
    
    def get_active_reminders(self) -> ReminderList:
        """Get all active reminders"""
        return list(self._active_reminders.values())
    
    def get_due_reminders(self) -> ReminderList:
        """Get reminders that are due to trigger"""
        now = datetime.now()
        due_reminders = []
        
        for reminder in self._active_reminders.values():
            if reminder.is_due():
                due_reminders.append(reminder)
        
        return due_reminders
    
    def start_engine(self):
        """Start the reminder engine monitoring thread"""
        if self._running:
            self.logger.warning("Reminder engine is already running")
            return
        
        self._running = True
        self._engine_thread = threading.Thread(target=self._engine_loop, daemon=True)
        self._engine_thread.start()
        
        self.logger.info("Reminder engine started")
    
    def stop_engine(self):
        """Stop the reminder engine monitoring thread"""
        if not self._running:
            return
        
        self._running = False
        if self._engine_thread and self._engine_thread.is_alive():
            self._engine_thread.join(timeout=5.0)
        
        self.logger.info("Reminder engine stopped")
    
    def register_notification_handler(self, notification_type: NotificationType, handler: Callable):
        """Register a custom notification handler"""
        self._notification_handlers[notification_type] = handler
        
        self.logger.info("Notification handler registered", extra={
            "notification_type": notification_type.value
        })
    
    def _engine_loop(self):
        """Main engine monitoring loop"""
        self.logger.info("Reminder engine monitoring started")
        
        while self._running:
            try:
                # Check for due reminders
                due_reminders = self.get_due_reminders()
                
                for reminder in due_reminders:
                    self._trigger_reminder(reminder)
                
                # Sleep before next check
                time.sleep(self._check_interval)
                
            except Exception as e:
                self.logger.error("Error in reminder engine loop", extra={
                    "error": str(e)
                })
                time.sleep(self._check_interval)
    
    def _trigger_reminder(self, reminder: Reminder):
        """Trigger a reminder notification"""
        try:
            # Mark as triggered
            reminder.trigger()
            
            # Send notification
            handler = self._notification_handlers.get(reminder.notification_type)
            if handler:
                handler(reminder)
            else:
                self._default_notification_handler(reminder)
            
            # Handle snooze expiration
            if reminder.is_snoozed and reminder.snoozed_until and datetime.now() >= reminder.snoozed_until:
                reminder.is_snoozed = False
                reminder.snoozed_until = None
            
            self._save_reminder(reminder)
            
            self.logger.info("Reminder triggered", extra={
                "reminder_id": reminder.id,
                "task_id": reminder.task_id,
                "notification_type": reminder.notification_type.value
            })
            
        except Exception as e:
            self.logger.error("Failed to trigger reminder", extra={
                "reminder_id": reminder.id,
                "error": str(e)
            })
    
    def _calculate_next_trigger(self, reminder: Reminder) -> Optional[datetime]:
        """Calculate the next trigger time for a reminder"""
        if reminder.trigger_type == TriggerType.TIME_ABSOLUTE:
            if isinstance(reminder.trigger_value, datetime):
                return reminder.trigger_value
            elif isinstance(reminder.trigger_value, str):
                try:
                    return datetime.fromisoformat(reminder.trigger_value)
                except ValueError:
                    pass
        
        elif reminder.trigger_type == TriggerType.TIME_RELATIVE:
            # Handle relative time (e.g., "in 30 minutes")
            if isinstance(reminder.trigger_value, dict):
                delta_kwargs = reminder.trigger_value
                return datetime.now() + timedelta(**delta_kwargs)
            elif isinstance(reminder.trigger_value, int):
                # Assume minutes
                return datetime.now() + timedelta(minutes=reminder.trigger_value)
        
        elif reminder.trigger_type == TriggerType.TIME_RECURRING:
            # Handle recurring reminders
            if isinstance(reminder.trigger_value, dict):
                pattern = reminder.trigger_value.get('pattern')
                interval = reminder.trigger_value.get('interval', 1)
                
                if pattern == 'daily':
                    return datetime.now() + timedelta(days=interval)
                elif pattern == 'weekly':
                    return datetime.now() + timedelta(weeks=interval)
                elif pattern == 'monthly':
                    return datetime.now() + timedelta(days=30 * interval)
        
        # Default: trigger immediately for unsupported types
        return datetime.now()
    
    def _default_notification_handler(self, reminder: Reminder):
        """Default notification handler for reminders"""
        self.logger.info(f"REMINDER: {reminder.message}", extra={
            "reminder_id": reminder.id,
            "task_id": reminder.task_id,
            "notification_type": reminder.notification_type.value
        })
    
    def _setup_default_handlers(self):
        """Setup default notification handlers"""
        self._notification_handlers[NotificationType.POPUP] = self._popup_handler
        self._notification_handlers[NotificationType.SYSTEM] = self._system_handler
        self._notification_handlers[NotificationType.VOICE] = self._voice_handler
    
    def _popup_handler(self, reminder: Reminder):
        """Handle popup notifications"""
        # For now, just log - can be extended with actual popup implementation
        self.logger.info(f"[POPUP] {reminder.message}", extra={
            "reminder_id": reminder.id,
            "task_id": reminder.task_id
        })
    
    def _system_handler(self, reminder: Reminder):
        """Handle system notifications"""
        # For now, just log - can be extended with OS notifications
        self.logger.info(f"[SYSTEM] {reminder.message}", extra={
            "reminder_id": reminder.id,
            "task_id": reminder.task_id
        })
    
    def _voice_handler(self, reminder: Reminder):
        """Handle voice notifications"""
        # For now, just log - can be extended with TTS
        self.logger.info(f"[VOICE] {reminder.message}", extra={
            "reminder_id": reminder.id,
            "task_id": reminder.task_id
        })
    
    def _load_reminders(self):
        """Load reminders from storage"""
        try:
            reminders_file = self.storage_path / "reminders.json"
            if reminders_file.exists():
                with open(reminders_file, 'r', encoding='utf-8') as f:
                    reminders_data = json.load(f)
                
                for reminder_data in reminders_data.get('reminders', []):
                    reminder = self._dict_to_reminder(reminder_data)
                    self._reminders[reminder.id] = reminder
                    
                    if reminder.is_active:
                        self._active_reminders[reminder.id] = reminder
                
                self.logger.info("Reminders loaded from storage", extra={
                    "reminder_count": len(self._reminders),
                    "active_count": len(self._active_reminders)
                })
        
        except Exception as e:
            self.logger.error("Failed to load reminders", extra={"error": str(e)})
    
    def _save_reminder(self, reminder: Reminder):
        """Save a single reminder to storage"""
        try:
            self._save_all_reminders()
        except Exception as e:
            self.logger.error("Failed to save reminder", extra={
                "reminder_id": reminder.id,
                "error": str(e)
            })
    
    def _save_all_reminders(self):
        """Save all reminders to storage"""
        try:
            reminders_file = self.storage_path / "reminders.json"
            
            reminders_data = {
                'reminders': [reminder.to_dict() for reminder in self._reminders.values()],
                'metadata': {
                    'last_updated': datetime.now().isoformat(),
                    'reminder_count': len(self._reminders),
                    'active_count': len(self._active_reminders)
                }
            }
            
            with open(reminders_file, 'w', encoding='utf-8') as f:
                json.dump(reminders_data, f, indent=2, ensure_ascii=False)
        
        except Exception as e:
            self.logger.error("Failed to save reminders", extra={"error": str(e)})
    
    def _dict_to_reminder(self, reminder_data: Dict[str, Any]) -> Reminder:
        """Convert dictionary to Reminder object"""
        # Convert enum values back to enums
        if 'trigger_type' in reminder_data:
            reminder_data['trigger_type'] = TriggerType(reminder_data['trigger_type'])
        
        if 'notification_type' in reminder_data:
            reminder_data['notification_type'] = NotificationType(reminder_data['notification_type'])
        
        # Convert datetime strings back to datetime objects
        datetime_fields = ['created_at', 'updated_at', 'last_triggered', 'next_trigger', 'snoozed_until']
        for field in datetime_fields:
            if field in reminder_data and reminder_data[field]:
                reminder_data[field] = datetime.fromisoformat(reminder_data[field])
        
        # Handle metadata
        if 'metadata' in reminder_data:
            from ..tasks.models import ReminderMetadata
            metadata_dict = reminder_data.pop('metadata')
            reminder_data['metadata'] = ReminderMetadata(**metadata_dict)
        
        return Reminder(**reminder_data)
