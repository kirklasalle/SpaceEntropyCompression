#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_dpa\reminders\trigger_system.py #python #source_code  
**Category:** Source Code  
**Status:** Active
"""









# Trigger System

**Created:** 2024-10-15  
**Updated:** 2025-07-26 10:26:57  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_dpa\reminders\trigger_system.py #python #source_code  
**Category:** Source Code  
**Status:** Active

"""
Trigger System for ImpressionCore Personal Assistant

This module provides multi-trigger reminder system with time-based, location-based,
event-based, and conditional triggers for intelligent reminder delivery.

Created: 2025-01-06
Author: ImpressionCore Development Team
Version: 1.0
Phase: 8B Week 2 - Task Management & Reminders
"""

import logging
import threading
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import re
from pathlib import Path
import schedule

from ..tasks.models import TriggerType, Reminder
from ...core.utils.rich_logging import setup_rich_logging
from ...core.utils.rich_status_animation import StatusAnimation

try:
    from ...core.utils.rich_enhancements import RichEnhancer
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class TriggerStatus(Enum):
    """Trigger status states"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    TRIGGERED = "triggered"
    EXPIRED = "expired"
    DISABLED = "disabled"


@dataclass
class TriggerEvent:
    """Represents a trigger event"""
    trigger_id: str
    reminder_id: str
    trigger_type: TriggerType
    triggered_at: datetime
    trigger_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TriggerCondition:
    """Represents a trigger condition"""
    condition_type: str  # "time", "location", "event", "variable"
    operator: str        # "eq", "gt", "lt", "contains", "matches"
    value: Any
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseTrigger:
    """Base class for all trigger types"""
    
    def __init__(self, trigger_id: str, reminder_id: str, trigger_data: Dict[str, Any]):
        self.trigger_id = trigger_id
        self.reminder_id = reminder_id
        self.trigger_data = trigger_data
        self.status = TriggerStatus.ACTIVE
        self.created_at = datetime.now()
        self.last_checked = None
        self.trigger_count = 0
        self.max_triggers = trigger_data.get('max_triggers', 1)
        
        self.logger = setup_rich_logging(f"{__name__}.{self.__class__.__name__}")
    
    def check_trigger(self) -> bool:
        """Check if trigger condition is met"""
        self.last_checked = datetime.now()
        
        if self.status != TriggerStatus.ACTIVE:
            return False
        
        if self.trigger_count >= self.max_triggers:
            self.status = TriggerStatus.EXPIRED
            return False
        
        return self._evaluate_condition()
    
    def fire_trigger(self) -> TriggerEvent:
        """Fire the trigger and create event"""
        self.trigger_count += 1
        
        if self.trigger_count >= self.max_triggers:
            self.status = TriggerStatus.TRIGGERED
        
        event = TriggerEvent(
            trigger_id=self.trigger_id,
            reminder_id=self.reminder_id,
            trigger_type=self._get_trigger_type(),
            triggered_at=datetime.now(),
            trigger_data=self.trigger_data.copy()
        )
        
        self.logger.debug(f"Trigger fired: {self.trigger_id}")
        return event
    
    def _evaluate_condition(self) -> bool:
        """Evaluate trigger-specific condition (to be overridden)"""
        raise NotImplementedError
    
    def _get_trigger_type(self) -> TriggerType:
        """Get trigger type (to be overridden)"""
        raise NotImplementedError


class TimeTrigger(BaseTrigger):
    """Time-based trigger implementation"""
    
    def _get_trigger_type(self) -> TriggerType:
        return TriggerType.TIME_ABSOLUTE
    
    def _evaluate_condition(self) -> bool:
        """Evaluate time-based condition"""
        trigger_time = self.trigger_data.get('trigger_time')
        if not trigger_time:
            return False
        
        if isinstance(trigger_time, str):
            trigger_time = datetime.fromisoformat(trigger_time)
        
        current_time = datetime.now()
        
        # Check if trigger time has passed
        if current_time >= trigger_time:
            # Check for tolerance window (default 1 minute)
            tolerance = timedelta(minutes=self.trigger_data.get('tolerance_minutes', 1))
            if current_time <= trigger_time + tolerance:
                return True
        
        return False


class RecurringTimeTrigger(BaseTrigger):
    """Recurring time-based trigger implementation"""
    
    def _get_trigger_type(self) -> TriggerType:
        return TriggerType.TIME_RECURRING
    
    def _evaluate_condition(self) -> bool:
        """Evaluate recurring time condition"""
        pattern = self.trigger_data.get('pattern')
        if not pattern:
            return False
        
        current_time = datetime.now()
        last_triggered = self.trigger_data.get('last_triggered')
        
        if last_triggered:
            if isinstance(last_triggered, str):
                last_triggered = datetime.fromisoformat(last_triggered)
            
            # Ensure minimum interval between triggers
            min_interval = timedelta(minutes=1)
            if current_time - last_triggered < min_interval:
                return False
        
        # Check pattern matching
        if pattern == 'daily':
            target_time = self.trigger_data.get('time', '09:00')
            return self._check_daily_pattern(current_time, target_time)
        elif pattern == 'weekly':
            weekday = self.trigger_data.get('weekday', 0)  # Monday = 0
            target_time = self.trigger_data.get('time', '09:00')
            return self._check_weekly_pattern(current_time, weekday, target_time)
        elif pattern == 'monthly':
            day = self.trigger_data.get('day', 1)
            target_time = self.trigger_data.get('time', '09:00')
            return self._check_monthly_pattern(current_time, day, target_time)
        
        return False
    
    def _check_daily_pattern(self, current_time: datetime, target_time: str) -> bool:
        """Check daily recurring pattern"""
        try:
            hour, minute = map(int, target_time.split(':'))
            target_datetime = current_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # Check if we're within 1 minute of target time
            time_diff = abs((current_time - target_datetime).total_seconds())
            return time_diff <= 60
        except Exception:
            return False
    
    def _check_weekly_pattern(self, current_time: datetime, weekday: int, target_time: str) -> bool:
        """Check weekly recurring pattern"""
        if current_time.weekday() != weekday:
            return False
        
        return self._check_daily_pattern(current_time, target_time)
    
    def _check_monthly_pattern(self, current_time: datetime, day: int, target_time: str) -> bool:
        """Check monthly recurring pattern"""
        if current_time.day != day:
            return False
        
        return self._check_daily_pattern(current_time, target_time)
    
    def fire_trigger(self) -> TriggerEvent:
        """Fire recurring trigger and update last triggered time"""
        self.trigger_data['last_triggered'] = datetime.now().isoformat()
        return super().fire_trigger()


class LocationTrigger(BaseTrigger):
    """Location-based trigger implementation"""
    
    def _get_trigger_type(self) -> TriggerType:
        return TriggerType.LOCATION
    
    def _evaluate_condition(self) -> bool:
        """Evaluate location-based condition"""
        # Location triggers require external location service
        # This is a placeholder implementation
        
        target_location = self.trigger_data.get('location')
        trigger_on = self.trigger_data.get('trigger_on', 'arrival')  # 'arrival' or 'departure'
        
        if not target_location:
            return False
        
        # Future enhancement: integrate with location services
        # For now, return False (location tracking not implemented)
        return False


class EventTrigger(BaseTrigger):
    """Event-based trigger implementation"""
    
    def _get_trigger_type(self) -> TriggerType:
        return TriggerType.EVENT
    
    def _evaluate_condition(self) -> bool:
        """Evaluate event-based condition"""
        event_type = self.trigger_data.get('event_type')
        
        if event_type == 'system_startup':
            # Check if system has started recently
            return self._check_system_startup()
        elif event_type == 'file_modified':
            file_path = self.trigger_data.get('file_path')
            return self._check_file_modified(file_path)
        elif event_type == 'task_completed':
            task_id = self.trigger_data.get('task_id')
            return self._check_task_completed(task_id)
        
        return False
    
    def _check_system_startup(self) -> bool:
        """Check if system started recently"""
        # Placeholder implementation
        return False
    
    def _check_file_modified(self, file_path: str) -> bool:
        """Check if file was modified recently"""
        try:
            if not file_path:
                return False
            
            path = Path(file_path)
            if not path.exists():
                return False
            
            # Check if file was modified in the last minute
            mod_time = datetime.fromtimestamp(path.stat().st_mtime)
            time_diff = (datetime.now() - mod_time).total_seconds()
            
            return time_diff <= 60
        except Exception:
            return False
    
    def _check_task_completed(self, task_id: str) -> bool:
        """Check if a specific task was completed"""
        # This would require integration with task management system
        # Placeholder implementation
        return False


class ConditionalTrigger(BaseTrigger):
    """Conditional logic trigger implementation"""
    
    def _get_trigger_type(self) -> TriggerType:
        return TriggerType.CONDITIONAL
    
    def _evaluate_condition(self) -> bool:
        """Evaluate conditional logic"""
        conditions = self.trigger_data.get('conditions', [])
        logic_operator = self.trigger_data.get('logic', 'AND')  # 'AND' or 'OR'
        
        if not conditions:
            return False
        
        results = []
        for condition in conditions:
            result = self._evaluate_single_condition(condition)
            results.append(result)
        
        if logic_operator == 'AND':
            return all(results)
        elif logic_operator == 'OR':
            return any(results)
        
        return False
    
    def _evaluate_single_condition(self, condition: Dict[str, Any]) -> bool:
        """Evaluate a single condition"""
        condition_type = condition.get('type')
        operator = condition.get('operator')
        value = condition.get('value')
        variable = condition.get('variable')
        
        if condition_type == 'time':
            current_time = datetime.now()
            if operator == 'after':
                target_time = datetime.fromisoformat(value) if isinstance(value, str) else value
                return current_time > target_time
            elif operator == 'before':
                target_time = datetime.fromisoformat(value) if isinstance(value, str) else value
                return current_time < target_time
        
        elif condition_type == 'variable':
            # Check system variables or user preferences
            return self._check_variable_condition(variable, operator, value)
        
        return False
    
    def _check_variable_condition(self, variable: str, operator: str, value: Any) -> bool:
        """Check variable-based condition"""
        # Placeholder for variable checking
        # Could check system state, user preferences, etc.
        return False


class TriggerSystem:
    """
    Multi-trigger reminder system with intelligent trigger management
    and efficient polling for various trigger types.
    """
    
    def __init__(self):
        """Initialize trigger system"""
        self.logger = setup_rich_logging(__name__)
        
        # Trigger registry
        self._triggers: Dict[str, BaseTrigger] = {}
        self._trigger_events: List[TriggerEvent] = []
        
        # Event callbacks
        self._event_handlers: List[Callable[[TriggerEvent], None]] = []
        
        # Trigger types mapping
        self._trigger_classes = {
            TriggerType.TIME_ABSOLUTE: TimeTrigger,
            TriggerType.TIME_RECURRING: RecurringTimeTrigger,
            TriggerType.LOCATION: LocationTrigger,
            TriggerType.EVENT: EventTrigger,
            TriggerType.CONDITIONAL: ConditionalTrigger,
        }
        
        # Threading
        self._lock = threading.RLock()
        self._monitoring_thread = None
        self._running = False
        
        # Performance settings
        self._check_interval = 10  # seconds
        self._batch_size = 50
        
        # Statistics
        self._stats = {
            'total_triggers': 0,
            'active_triggers': 0,
            'triggered_events': 0,
            'checks_performed': 0,
            'avg_check_time': 0.0
        }
        
        self.logger.info("Trigger system initialized")
    
    def start(self):
        """Start trigger monitoring"""
        with self._lock:
            if self._running:
                return
            
            self._running = True
            self._monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self._monitoring_thread.start()
            
            self.logger.info("Trigger monitoring started")
    
    def stop(self):
        """Stop trigger monitoring"""
        with self._lock:
            self._running = False
            if self._monitoring_thread:
                self._monitoring_thread.join(timeout=5.0)
            
            self.logger.info("Trigger monitoring stopped")
    
    def register_trigger(self, reminder: Reminder) -> str:
        """Register a new trigger for a reminder"""
        
        trigger_id = self._generate_trigger_id()
        trigger_type = reminder.trigger_type
        trigger_data = reminder.metadata.copy() if reminder.metadata else {}
        
        # Add trigger-specific data from reminder
        if trigger_type == TriggerType.TIME_ABSOLUTE:
            trigger_data['trigger_time'] = reminder.trigger_value
        elif trigger_type == TriggerType.TIME_RECURRING:
            if isinstance(reminder.trigger_value, dict):
                trigger_data.update(reminder.trigger_value)
            else:
                trigger_data['pattern'] = reminder.trigger_value
        else:
            trigger_data['trigger_value'] = reminder.trigger_value
        
        # Create trigger instance
        trigger_class = self._trigger_classes.get(trigger_type)
        if not trigger_class:
            self.logger.error(f"Unsupported trigger type: {trigger_type}")
            return None
        
        trigger = trigger_class(trigger_id, reminder.id, trigger_data)
        
        with self._lock:
            self._triggers[trigger_id] = trigger
            self._stats['total_triggers'] += 1
            self._update_active_count()
        
        self.logger.info(f"Trigger registered: {trigger_id} for reminder {reminder.id}")
        return trigger_id
    
    def unregister_trigger(self, trigger_id: str) -> bool:
        """Unregister a trigger"""
        with self._lock:
            if trigger_id in self._triggers:
                del self._triggers[trigger_id]
                self._update_active_count()
                self.logger.info(f"Trigger unregistered: {trigger_id}")
                return True
            return False
    
    def add_event_handler(self, handler: Callable[[TriggerEvent], None]):
        """Add event handler for trigger events"""
        with self._lock:
            self._event_handlers.append(handler)
            self.logger.debug(f"Event handler added: {handler.__name__}")
    
    def remove_event_handler(self, handler: Callable[[TriggerEvent], None]):
        """Remove event handler"""
        with self._lock:
            if handler in self._event_handlers:
                self._event_handlers.remove(handler)
                self.logger.debug(f"Event handler removed: {handler.__name__}")
    
    def check_all_triggers(self) -> List[TriggerEvent]:
        """Manually check all triggers"""
        events = []
        
        with self._lock:
            triggers_to_check = list(self._triggers.values())
        
        check_start = time.time()
        
        for trigger in triggers_to_check:
            try:
                if trigger.check_trigger():
                    event = trigger.fire_trigger()
                    events.append(event)
                    self._trigger_events.append(event)
                    
                    # Notify event handlers
                    for handler in self._event_handlers:
                        try:
                            handler(event)
                        except Exception as e:
                            self.logger.error(f"Event handler error: {e}")
                            
            except Exception as e:
                self.logger.error(f"Error checking trigger {trigger.trigger_id}: {e}")
        
        # Update statistics
        check_time = time.time() - check_start
        self._stats['checks_performed'] += 1
        self._update_avg_check_time(check_time)
        
        if events:
            self._stats['triggered_events'] += len(events)
            self.logger.debug(f"Triggers fired: {len(events)}")
        
        return events
    
    def get_trigger_status(self, trigger_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific trigger"""
        with self._lock:
            trigger = self._triggers.get(trigger_id)
            if not trigger:
                return None
            
            return {
                'trigger_id': trigger.trigger_id,
                'reminder_id': trigger.reminder_id,
                'status': trigger.status.value,
                'created_at': trigger.created_at.isoformat(),
                'last_checked': trigger.last_checked.isoformat() if trigger.last_checked else None,
                'trigger_count': trigger.trigger_count,
                'max_triggers': trigger.max_triggers,
                'trigger_data': trigger.trigger_data
            }
    
    def get_all_triggers(self) -> List[Dict[str, Any]]:
        """Get status of all triggers"""
        with self._lock:
            return [self.get_trigger_status(tid) for tid in self._triggers.keys()]
    
    def get_trigger_events(self, 
                          reminder_id: Optional[str] = None,
                          trigger_id: Optional[str] = None,
                          limit: Optional[int] = None) -> List[TriggerEvent]:
        """Get trigger events with optional filtering"""
        with self._lock:
            events = self._trigger_events.copy()
            
            if reminder_id:
                events = [e for e in events if e.reminder_id == reminder_id]
            
            if trigger_id:
                events = [e for e in events if e.trigger_id == trigger_id]
            
            # Sort by triggered_at descending
            events.sort(key=lambda e: e.triggered_at, reverse=True)
            
            if limit:
                events = events[:limit]
            
            return events
    
    def _monitoring_loop(self):
        """Main trigger monitoring loop"""
        while self._running:
            try:
                self.check_all_triggers()
                
                # Clean up old events and expired triggers
                self._cleanup_old_data()
                
                # Sleep until next check
                time.sleep(self._check_interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(30)  # Wait longer on error
    
    def _cleanup_old_data(self):
        """Clean up old events and expired triggers"""
        current_time = datetime.now()
        
        with self._lock:
            # Remove old events (keep last 1000 or 24 hours)
            if len(self._trigger_events) > 1000:
                self._trigger_events = self._trigger_events[-500:]
            else:
                cutoff_time = current_time - timedelta(hours=24)
                self._trigger_events = [
                    e for e in self._trigger_events 
                    if e.triggered_at > cutoff_time
                ]
            
            # Remove expired triggers
            expired_triggers = [
                tid for tid, trigger in self._triggers.items()
                if trigger.status in [TriggerStatus.EXPIRED, TriggerStatus.TRIGGERED]
            ]
            
            for tid in expired_triggers:
                del self._triggers[tid]
            
            if expired_triggers:
                self.logger.debug(f"Cleaned up {len(expired_triggers)} expired triggers")
                self._update_active_count()
    
    def _update_active_count(self):
        """Update active trigger count"""
        active_count = len([
            t for t in self._triggers.values() 
            if t.status == TriggerStatus.ACTIVE
        ])
        self._stats['active_triggers'] = active_count
    
    def _update_avg_check_time(self, new_time: float):
        """Update average check time statistic"""
        current_avg = self._stats['avg_check_time']
        checks_performed = self._stats['checks_performed']
        
        if checks_performed == 1:
            self._stats['avg_check_time'] = new_time
        else:
            # Rolling average
            self._stats['avg_check_time'] = (
                (current_avg * (checks_performed - 1) + new_time) / checks_performed
            )
    
    def _generate_trigger_id(self) -> str:
        """Generate unique trigger ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        return f"trigger_{timestamp}"
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get trigger system statistics"""
        with self._lock:
            stats = self._stats.copy()
            stats.update({
                'is_running': self._running,
                'check_interval': self._check_interval,
                'total_events': len(self._trigger_events)
            })
            return stats


# Factory function for easy instantiation
def create_trigger_system() -> TriggerSystem:
    """Create and return a TriggerSystem instance"""
    return TriggerSystem()
