#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_dpa\integration\calendar_integration.py #python #source_code  
**Category:** Source Code  
**Status:** Active
"""









# Calendar Integration

**Created:** 2024-10-15  
**Updated:** 2025-07-26 10:26:57  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_dpa\integration\calendar_integration.py #python #source_code  
**Category:** Source Code  
**Status:** Active

"""
Calendar Integration for ImpressionCore Assistant

This module provides calendar integration capabilities for task and reminder management,
allowing seamless synchronization with external calendar systems.

Created: June 6, 2025
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum

from ..tasks.models import Task, TaskPriority, TaskStatus
from ..reminders.reminder_engine import Reminder

# Configure logging
logger = logging.getLogger(__name__)

class CalendarProvider(Enum):
    """Supported calendar providers."""
    GOOGLE = "google"
    OUTLOOK = "outlook"
    APPLE = "apple"
    CALDAV = "caldav"
    LOCAL = "local"

@dataclass
class CalendarEvent:
    """Represents a calendar event."""
    id: str
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    attendees: List[str] = None
    recurring: bool = False
    recurrence_rule: Optional[str] = None
    calendar_id: str = "default"
    provider: CalendarProvider = CalendarProvider.LOCAL
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.attendees is None:
            self.attendees = []
        if self.metadata is None:
            self.metadata = {}

class CalendarIntegration:
    """
    Main calendar integration class that handles synchronization
    between tasks/reminders and external calendar systems.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize calendar integration.
        
        Args:
            config: Configuration dictionary for calendar providers
        """
        self.config = config or {}
        self.providers = {}
        self.sync_enabled = self.config.get('sync_enabled', True)
        self.default_calendar = self.config.get('default_calendar', 'ImpressionCore Tasks')
        
        # Initialize providers based on config
        self._initialize_providers()
        
        logger.info("Calendar integration initialized")
    
    def _initialize_providers(self):
        """Initialize configured calendar providers."""
        for provider_name, provider_config in self.config.get('providers', {}).items():
            try:
                if provider_config.get('enabled', False):
                    provider = self._create_provider(provider_name, provider_config)
                    if provider:
                        self.providers[provider_name] = provider
                        logger.info(f"Initialized {provider_name} calendar provider")
            except Exception as e:
                logger.error(f"Failed to initialize {provider_name} provider: {e}")
    
    def _create_provider(self, provider_name: str, config: Dict[str, Any]):
        """Create a calendar provider instance."""
        # In a full implementation, this would create actual provider instances
        # For now, return a mock provider
        class MockProvider:
            def __init__(self, name, config):
                self.name = name
                self.config = config
                self.authenticated = False
            
            async def authenticate(self):
                """Authenticate with the provider."""
                self.authenticated = True
                return True
            
            async def get_events(self, start_date, end_date):
                """Get events from the provider."""
                return []
            
            async def create_event(self, event):
                """Create an event in the provider."""
                return f"mock_{event.id}"
            
            async def update_event(self, event_id, event):
                """Update an event in the provider."""
                return True
            
            async def delete_event(self, event_id):
                """Delete an event from the provider."""
                return True
        
        return MockProvider(provider_name, config)
    
    async def sync_task_to_calendar(self, task: Task) -> Optional[str]:
        """
        Sync a task to the calendar as an event.
        
        Args:
            task: Task to sync to calendar
            
        Returns:
            Calendar event ID if successful, None otherwise
        """
        if not self.sync_enabled:
            return None
        
        try:
            # Convert task to calendar event
            event = self._task_to_event(task)
            
            # Get the appropriate provider
            provider = self._get_primary_provider()
            if not provider:
                logger.warning("No calendar provider available for sync")
                return None
            
            # Create event in calendar
            event_id = await provider.create_event(event)
            
            logger.info(f"Synced task {task.id} to calendar as event {event_id}")
            return event_id
            
        except Exception as e:
            logger.error(f"Failed to sync task {task.id} to calendar: {e}")
            return None
    
    async def sync_reminder_to_calendar(self, reminder: Reminder) -> Optional[str]:
        """
        Sync a reminder to the calendar as an event.
        
        Args:
            reminder: Reminder to sync to calendar
            
        Returns:
            Calendar event ID if successful, None otherwise
        """
        if not self.sync_enabled:
            return None
        
        try:
            # Convert reminder to calendar event
            event = self._reminder_to_event(reminder)
            
            # Get the appropriate provider
            provider = self._get_primary_provider()
            if not provider:
                logger.warning("No calendar provider available for sync")
                return None
            
            # Create event in calendar
            event_id = await provider.create_event(event)
            
            logger.info(f"Synced reminder {reminder.id} to calendar as event {event_id}")
            return event_id
            
        except Exception as e:
            logger.error(f"Failed to sync reminder {reminder.id} to calendar: {e}")
            return None
    
    def _task_to_event(self, task: Task) -> CalendarEvent:
        """Convert a task to a calendar event."""
        # Calculate event duration based on task complexity
        duration_hours = 1  # Default duration
        if task.priority == TaskPriority.HIGH:
            duration_hours = 2
        elif task.priority == TaskPriority.LOW:
            duration_hours = 0.5
        
        start_time = task.due_date or datetime.now()
        end_time = start_time + timedelta(hours=duration_hours)
        
        return CalendarEvent(
            id=f"task_{task.id}",
            title=f"Task: {task.title}",
            description=f"Priority: {task.priority.value}\n\n{task.description}",
            start_time=start_time,
            end_time=end_time,
            calendar_id=self.default_calendar,
            metadata={
                'task_id': task.id,
                'task_priority': task.priority.value,
                'task_status': task.status.value,
                'source': 'impressioncore_task'
            }
        )
    
    def _reminder_to_event(self, reminder: Reminder) -> CalendarEvent:
        """Convert a reminder to a calendar event."""
        # For reminders, create a short event at the reminder time
        start_time = reminder.trigger_time
        end_time = start_time + timedelta(minutes=15)  # 15-minute reminder slot
        
        return CalendarEvent(
            id=f"reminder_{reminder.id}",
            title=f"Reminder: {reminder.message}",
            description=f"Type: {reminder.reminder_type}\n\n{reminder.message}",
            start_time=start_time,
            end_time=end_time,
            calendar_id=self.default_calendar,
            metadata={
                'reminder_id': reminder.id,
                'reminder_type': reminder.reminder_type,
                'source': 'impressioncore_reminder'
            }
        )
    
    def _get_primary_provider(self):
        """Get the primary calendar provider."""
        if not self.providers:
            return None
        
        # Return the first enabled provider
        return next(iter(self.providers.values()))
    
    async def get_calendar_events(self, start_date: datetime, end_date: datetime) -> List[CalendarEvent]:
        """
        Get calendar events from all providers within the specified date range.
        
        Args:
            start_date: Start date for event retrieval
            end_date: End date for event retrieval
            
        Returns:
            List of calendar events
        """
        all_events = []
        
        for provider_name, provider in self.providers.items():
            try:
                events = await provider.get_events(start_date, end_date)
                # Convert provider events to CalendarEvent objects
                for event in events:
                    if isinstance(event, CalendarEvent):
                        all_events.append(event)
                    else:
                        # Convert if needed
                        all_events.append(self._convert_provider_event(event, provider_name))
                        
            except Exception as e:
                logger.error(f"Failed to get events from {provider_name}: {e}")
        
        return sorted(all_events, key=lambda x: x.start_time)
    
    def _convert_provider_event(self, event_data: Dict[str, Any], provider_name: str) -> CalendarEvent:
        """Convert provider-specific event data to CalendarEvent."""
        # This would handle conversion from different provider formats
        # For now, return a basic conversion
        return CalendarEvent(
            id=event_data.get('id', ''),
            title=event_data.get('title', ''),
            description=event_data.get('description', ''),
            start_time=event_data.get('start_time', datetime.now()),
            end_time=event_data.get('end_time', datetime.now()),
            location=event_data.get('location'),
            provider=CalendarProvider(provider_name) if provider_name in [p.value for p in CalendarProvider] else CalendarProvider.LOCAL
        )
    
    async def remove_task_from_calendar(self, task_id: str, event_id: str) -> bool:
        """
        Remove a task-related event from the calendar.
        
        Args:
            task_id: ID of the task
            event_id: ID of the calendar event
            
        Returns:
            True if successfully removed, False otherwise
        """
        try:
            provider = self._get_primary_provider()
            if not provider:
                return False
            
            success = await provider.delete_event(event_id)
            if success:
                logger.info(f"Removed task {task_id} event {event_id} from calendar")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to remove task event from calendar: {e}")
            return False
    
    async def update_task_in_calendar(self, task: Task, event_id: str) -> bool:
        """
        Update a task-related event in the calendar.
        
        Args:
            task: Updated task
            event_id: ID of the calendar event to update
            
        Returns:
            True if successfully updated, False otherwise
        """
        try:
            provider = self._get_primary_provider()
            if not provider:
                return False
            
            # Convert updated task to event
            updated_event = self._task_to_event(task)
            updated_event.id = event_id  # Keep the existing event ID
            
            success = await provider.update_event(event_id, updated_event)
            if success:
                logger.info(f"Updated task {task.id} event {event_id} in calendar")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to update task event in calendar: {e}")
            return False
    
    def get_integration_status(self) -> Dict[str, Any]:
        """
        Get the current status of calendar integration.
        
        Returns:
            Dictionary containing integration status information
        """
        return {
            'sync_enabled': self.sync_enabled,
            'providers_configured': len(self.providers),
            'providers': {
                name: {
                    'authenticated': getattr(provider, 'authenticated', False),
                    'config': provider.config if hasattr(provider, 'config') else {}
                }
                for name, provider in self.providers.items()
            },
            'default_calendar': self.default_calendar
        }

# Convenience functions for easy integration
async def sync_task_to_calendar(task: Task, integration: CalendarIntegration = None) -> Optional[str]:
    """Convenience function to sync a task to calendar."""
    if integration is None:
        integration = CalendarIntegration()
    return await integration.sync_task_to_calendar(task)

async def sync_reminder_to_calendar(reminder: Reminder, integration: CalendarIntegration = None) -> Optional[str]:
    """Convenience function to sync a reminder to calendar."""
    if integration is None:
        integration = CalendarIntegration()
    return await integration.sync_reminder_to_calendar(reminder)
