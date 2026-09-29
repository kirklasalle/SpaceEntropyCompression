#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_dpa\reminders\notification_manager.py #memory_management #python #source_code  
**Category:** Source Code  
**Status:** Active
"""









# Notification Manager

**Created:** 2024-10-15  
**Updated:** 2025-07-26 10:26:57  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_dpa\reminders\notification_manager.py #memory_management #python #source_code  
**Category:** Source Code  
**Status:** Active

"""
Notification Manager for ImpressionCore Personal Assistant

This module provides cross-platform notification delivery with custom formats,
urgency-based delivery, and snooze/reschedule functionality.

Created: 2025-01-06
Author: ImpressionCore Development Team
Version: 1.0
Phase: 8B Week 2 - Task Management & Reminders
"""

import logging
import threading
import time
import platform
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path
import subprocess

from ..tasks.models import NotificationType, Reminder
from ...core.utils.rich_logging import setup_rich_logging
from ...core.utils.rich_status_animation import StatusAnimation

try:
    from ...core.utils.rich_enhancements import RichEnhancer
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# Platform-specific imports
try:
    if platform.system() == "Windows":
        import win10toast
        WINDOWS_TOAST_AVAILABLE = True
    else:
        WINDOWS_TOAST_AVAILABLE = False
except ImportError:
    WINDOWS_TOAST_AVAILABLE = False

try:
    import plyer
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False


class NotificationPriority(Enum):
    """Notification priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5


@dataclass
class NotificationConfig:
    """Configuration for notification delivery"""
    enabled_types: List[NotificationType] = field(default_factory=lambda: [
        NotificationType.POPUP, NotificationType.SYSTEM
    ])
    default_duration: int = 5000  # milliseconds
    sound_enabled: bool = True
    visual_effects: bool = True
    quiet_hours_start: int = 22  # 10 PM
    quiet_hours_end: int = 8     # 8 AM
    max_notifications_per_hour: int = 10
    snooze_duration: int = 10    # minutes


@dataclass
class NotificationMessage:
    """Represents a notification message"""
    id: str
    title: str
    body: str
    type: NotificationType
    priority: NotificationPriority
    reminder_id: Optional[str] = None
    task_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    delivery_time: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    actions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    delivered: bool = False
    acknowledged: bool = False


class NotificationManager:
    """
    Cross-platform notification manager with intelligent delivery,
    urgency handling, and user preference management.
    """
    
    def __init__(self, config: Optional[NotificationConfig] = None):
        """Initialize notification manager"""
        self.logger = setup_rich_logging(__name__)
        self.config = config or NotificationConfig()
        
        # Notification state
        self._pending_notifications: Dict[str, NotificationMessage] = {}
        self._delivered_notifications: Dict[str, NotificationMessage] = {}
        self._notification_queue: List[NotificationMessage] = []
        self._notification_history: List[NotificationMessage] = []
        
        # Rate limiting
        self._notification_timestamps: List[datetime] = []
        
        # Platform capabilities
        self._platform_capabilities = self._detect_platform_capabilities()
        
        # Delivery handlers
        self._delivery_handlers: Dict[NotificationType, Callable] = {
            NotificationType.POPUP: self._deliver_popup,
            NotificationType.SYSTEM: self._deliver_system,
            NotificationType.SOUND: self._deliver_sound,
            NotificationType.VISUAL: self._deliver_visual,
        }
        
        # Threading
        self._lock = threading.RLock()
        self._delivery_thread = None
        self._running = False
        
        # Statistics
        self._stats = {
            'total_notifications': 0,
            'delivered_notifications': 0,
            'failed_notifications': 0,
            'acknowledged_notifications': 0,
            'snoozed_notifications': 0
        }
        
        self.logger.info(f"Notification manager initialized with {len(self._platform_capabilities)} capabilities")
    
    def start(self):
        """Start the notification delivery service"""
        with self._lock:
            if self._running:
                return
            
            self._running = True
            self._delivery_thread = threading.Thread(target=self._delivery_loop, daemon=True)
            self._delivery_thread.start()
            
            self.logger.info("Notification delivery service started")
    
    def stop(self):
        """Stop the notification delivery service"""
        with self._lock:
            self._running = False
            if self._delivery_thread:
                self._delivery_thread.join(timeout=5.0)
            
            self.logger.info("Notification delivery service stopped")
    
    def send_notification(self, 
                         title: str,
                         body: str,
                         notification_type: NotificationType = NotificationType.POPUP,
                         priority: NotificationPriority = NotificationPriority.NORMAL,
                         reminder_id: Optional[str] = None,
                         task_id: Optional[str] = None,
                         actions: Optional[List[str]] = None,
                         delay: Optional[timedelta] = None) -> str:
        """Send a notification"""
        
        notification = NotificationMessage(
            id=self._generate_notification_id(),
            title=title,
            body=body,
            type=notification_type,
            priority=priority,
            reminder_id=reminder_id,
            task_id=task_id,
            actions=actions or [],
            delivery_time=datetime.now() + (delay or timedelta(0))
        )
        
        with self._lock:
            self._pending_notifications[notification.id] = notification
            self._notification_queue.append(notification)
            self._notification_queue.sort(key=lambda n: (n.delivery_time, -n.priority.value))
            
            self._stats['total_notifications'] += 1
        
        self.logger.debug(f"Notification queued: {notification.id} - {title}")
        return notification.id
    
    def send_reminder_notification(self, reminder: Reminder) -> str:
        """Send a notification for a reminder"""
        
        # Determine notification type based on reminder metadata
        notification_type = NotificationType.POPUP
        if hasattr(reminder, 'notification_type'):
            notification_type = reminder.notification_type
        
        # Set priority based on task priority or reminder urgency
        priority = NotificationPriority.NORMAL
        if hasattr(reminder, 'metadata') and reminder.metadata:
            urgency = reminder.metadata.get('urgency', 'normal')
            priority_map = {
                'low': NotificationPriority.LOW,
                'normal': NotificationPriority.NORMAL,
                'high': NotificationPriority.HIGH,
                'urgent': NotificationPriority.URGENT,
                'critical': NotificationPriority.CRITICAL
            }
            priority = priority_map.get(urgency, NotificationPriority.NORMAL)
        
        return self.send_notification(
            title="Reminder",
            body=reminder.message,
            notification_type=notification_type,
            priority=priority,
            reminder_id=reminder.id,
            task_id=reminder.task_id,
            actions=["Snooze", "Dismiss", "Mark Complete"]
        )
    
    def snooze_notification(self, notification_id: str, 
                           snooze_duration: Optional[timedelta] = None) -> bool:
        """Snooze a notification"""
        with self._lock:
            notification = self._delivered_notifications.get(notification_id)
            if not notification:
                return False
            
            # Remove from delivered and add back to pending
            del self._delivered_notifications[notification_id]
            
            # Update delivery time
            snooze_time = snooze_duration or timedelta(minutes=self.config.snooze_duration)
            notification.delivery_time = datetime.now() + snooze_time
            notification.delivered = False
            notification.acknowledged = False
            
            # Add back to queue
            self._pending_notifications[notification_id] = notification
            self._notification_queue.append(notification)
            self._notification_queue.sort(key=lambda n: (n.delivery_time, -n.priority.value))
            
            self._stats['snoozed_notifications'] += 1
            
            self.logger.info(f"Notification snoozed: {notification_id} for {snooze_time}")
            return True
    
    def acknowledge_notification(self, notification_id: str) -> bool:
        """Acknowledge a notification"""
        with self._lock:
            notification = self._delivered_notifications.get(notification_id)
            if not notification:
                return False
            
            notification.acknowledged = True
            self._stats['acknowledged_notifications'] += 1
            
            self.logger.debug(f"Notification acknowledged: {notification_id}")
            return True
    
    def dismiss_notification(self, notification_id: str) -> bool:
        """Dismiss a notification"""
        with self._lock:
            if notification_id in self._delivered_notifications:
                del self._delivered_notifications[notification_id]
                self.logger.debug(f"Notification dismissed: {notification_id}")
                return True
            return False
    
    def get_pending_notifications(self) -> List[NotificationMessage]:
        """Get all pending notifications"""
        with self._lock:
            return list(self._pending_notifications.values())
    
    def get_delivered_notifications(self) -> List[NotificationMessage]:
        """Get all delivered notifications"""
        with self._lock:
            return list(self._delivered_notifications.values())
    
    def _delivery_loop(self):
        """Main notification delivery loop"""
        while self._running:
            try:
                current_time = datetime.now()
                
                with self._lock:
                    # Find notifications ready for delivery
                    ready_notifications = [
                        n for n in self._notification_queue
                        if n.delivery_time <= current_time and not n.delivered
                    ]
                
                for notification in ready_notifications:
                    if not self._running:
                        break
                    
                    self._deliver_notification(notification)
                
                # Clean up old notifications
                self._cleanup_old_notifications()
                
                # Sleep briefly before next check
                time.sleep(1.0)
                
            except Exception as e:
                self.logger.error(f"Error in delivery loop: {e}")
                time.sleep(5.0)  # Wait longer on error
    
    def _deliver_notification(self, notification: NotificationMessage):
        """Deliver a single notification"""
        try:
            # Check rate limiting
            if not self._check_rate_limit():
                self.logger.warning(f"Rate limit exceeded, delaying notification: {notification.id}")
                notification.delivery_time = datetime.now() + timedelta(minutes=1)
                return
            
            # Check quiet hours
            if self._is_quiet_hours():
                if notification.priority.value < NotificationPriority.URGENT.value:
                    self.logger.debug(f"Delaying notification due to quiet hours: {notification.id}")
                    # Schedule for end of quiet hours
                    next_delivery = datetime.now().replace(
                        hour=self.config.quiet_hours_end, minute=0, second=0, microsecond=0
                    )
                    if next_delivery <= datetime.now():
                        next_delivery += timedelta(days=1)
                    notification.delivery_time = next_delivery
                    return
            
            # Check if notification type is enabled
            if notification.type not in self.config.enabled_types:
                self.logger.debug(f"Notification type disabled: {notification.type}")
                self._mark_notification_delivered(notification, False)
                return
            
            # Deliver via appropriate handler
            handler = self._delivery_handlers.get(notification.type)
            if handler and notification.type in self._platform_capabilities:
                success = handler(notification)
                self._mark_notification_delivered(notification, success)
            else:
                # Fallback to system notification
                success = self._deliver_system(notification)
                self._mark_notification_delivered(notification, success)
                
        except Exception as e:
            self.logger.error(f"Failed to deliver notification {notification.id}: {e}")
            self._mark_notification_delivered(notification, False)
    
    def _deliver_popup(self, notification: NotificationMessage) -> bool:
        """Deliver popup notification"""
        try:
            if WINDOWS_TOAST_AVAILABLE and platform.system() == "Windows":
                toaster = win10toast.ToastNotifier()
                toaster.show_toast(
                    title=notification.title,
                    msg=notification.body,
                    duration=self.config.default_duration // 1000,
                    threaded=True
                )
                return True
            elif PLYER_AVAILABLE:
                plyer.notification.notify(
                    title=notification.title,
                    message=notification.body,
                    timeout=self.config.default_duration // 1000
                )
                return True
            else:
                return self._deliver_console(notification)
                
        except Exception as e:
            self.logger.error(f"Popup delivery failed: {e}")
            return False
    
    def _deliver_system(self, notification: NotificationMessage) -> bool:
        """Deliver system notification"""
        try:
            if platform.system() == "Windows":
                # Use Windows notification system
                cmd = [
                    'powershell', '-Command',
                    f'''
                    Add-Type -AssemblyName System.Windows.Forms
                    $notification = New-Object System.Windows.Forms.NotifyIcon
                    $notification.Icon = [System.Drawing.SystemIcons]::Information
                    $notification.BalloonTipTitle = "{notification.title}"
                    $notification.BalloonTipText = "{notification.body}"
                    $notification.Visible = $true
                    $notification.ShowBalloonTip(5000)
                    '''
                ]
                subprocess.run(cmd, capture_output=True, check=True)
                return True
                
            elif platform.system() == "Darwin":  # macOS
                cmd = [
                    'osascript', '-e',
                    f'display notification "{notification.body}" with title "{notification.title}"'
                ]
                subprocess.run(cmd, capture_output=True, check=True)
                return True
                
            elif platform.system() == "Linux":
                cmd = ['notify-send', notification.title, notification.body]
                subprocess.run(cmd, capture_output=True, check=True)
                return True
            else:
                return self._deliver_console(notification)
                
        except Exception as e:
            self.logger.error(f"System notification failed: {e}")
            return self._deliver_console(notification)
    
    def _deliver_sound(self, notification: NotificationMessage) -> bool:
        """Deliver sound notification"""
        if not self.config.sound_enabled:
            return True
        
        try:
            if platform.system() == "Windows":
                import winsound
                winsound.MessageBeep(winsound.MB_ICONINFORMATION)
                return True
            elif platform.system() == "Darwin":
                subprocess.run(['afplay', '/System/Library/Sounds/Glass.aiff'], 
                             capture_output=True)
                return True
            elif platform.system() == "Linux":
                subprocess.run(['aplay', '/usr/share/sounds/alsa/Front_Left.wav'], 
                             capture_output=True)
                return True
            return True
            
        except Exception as e:
            self.logger.error(f"Sound notification failed: {e}")
            return False
    
    def _deliver_visual(self, notification: NotificationMessage) -> bool:
        """Deliver visual notification effects"""
        if not self.config.visual_effects:
            return True
        
        # Future enhancement: implement visual effects
        # - Screen flash
        # - Colored borders
        # - Animated elements
        return True
    
    def _deliver_console(self, notification: NotificationMessage) -> bool:
        """Fallback console notification"""
        try:
            print(f"\n🔔 NOTIFICATION: {notification.title}")
            print(f"   {notification.body}")
            print(f"   Priority: {notification.priority.name}")
            print(f"   Time: {notification.delivery_time.strftime('%H:%M:%S')}")
            if notification.actions:
                print(f"   Actions: {', '.join(notification.actions)}")
            print()
            return True
        except Exception as e:
            self.logger.error(f"Console notification failed: {e}")
            return False
    
    def _mark_notification_delivered(self, notification: NotificationMessage, success: bool):
        """Mark notification as delivered"""
        with self._lock:
            notification.delivered = True
            
            # Remove from pending and queue
            if notification.id in self._pending_notifications:
                del self._pending_notifications[notification.id]
            
            if notification in self._notification_queue:
                self._notification_queue.remove(notification)
            
            # Add to delivered or failed
            if success:
                self._delivered_notifications[notification.id] = notification
                self._stats['delivered_notifications'] += 1
                self._notification_timestamps.append(datetime.now())
            else:
                self._stats['failed_notifications'] += 1
            
            # Add to history
            self._notification_history.append(notification)
    
    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits"""
        current_time = datetime.now()
        one_hour_ago = current_time - timedelta(hours=1)
        
        # Remove old timestamps
        self._notification_timestamps = [
            ts for ts in self._notification_timestamps if ts > one_hour_ago
        ]
        
        return len(self._notification_timestamps) < self.config.max_notifications_per_hour
    
    def _is_quiet_hours(self) -> bool:
        """Check if current time is within quiet hours"""
        current_hour = datetime.now().hour
        
        if self.config.quiet_hours_start < self.config.quiet_hours_end:
            # Same day quiet hours (e.g., 22:00 - 8:00 next day)
            return (current_hour >= self.config.quiet_hours_start or 
                   current_hour < self.config.quiet_hours_end)
        else:
            # Overnight quiet hours (e.g., 8:00 - 22:00)
            return (self.config.quiet_hours_start <= current_hour < self.config.quiet_hours_end)
    
    def _detect_platform_capabilities(self) -> List[NotificationType]:
        """Detect available notification capabilities"""
        capabilities = [NotificationType.SYSTEM]  # Always available as fallback
        
        # Check for popup capabilities
        if WINDOWS_TOAST_AVAILABLE or PLYER_AVAILABLE:
            capabilities.append(NotificationType.POPUP)
        
        # Check for sound capabilities
        try:
            if platform.system() == "Windows":
                import winsound
                capabilities.append(NotificationType.SOUND)
            elif platform.system() in ["Darwin", "Linux"]:
                capabilities.append(NotificationType.SOUND)
        except ImportError:
            pass
        
        # Visual effects always available (basic implementation)
        capabilities.append(NotificationType.VISUAL)
        
        return capabilities
    
    def _generate_notification_id(self) -> str:
        """Generate a unique notification ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        return f"notif_{timestamp}"
    
    def _cleanup_old_notifications(self):
        """Clean up old notifications from memory"""
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        with self._lock:
            # Clean delivered notifications
            expired_ids = [
                nid for nid, notification in self._delivered_notifications.items()
                if notification.delivery_time < cutoff_time and notification.acknowledged
            ]
            
            for nid in expired_ids:
                del self._delivered_notifications[nid]
            
            # Limit history size
            if len(self._notification_history) > 1000:
                self._notification_history = self._notification_history[-500:]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get notification statistics"""
        with self._lock:
            stats = self._stats.copy()
            stats.update({
                'pending_count': len(self._pending_notifications),
                'delivered_count': len(self._delivered_notifications),
                'queue_size': len(self._notification_queue),
                'platform_capabilities': [cap.value for cap in self._platform_capabilities],
                'rate_limit_remaining': max(0, self.config.max_notifications_per_hour - len(self._notification_timestamps))
            })
            return stats


# Factory function for easy instantiation
def create_notification_manager(config: Optional[NotificationConfig] = None) -> NotificationManager:
    """Create and return a NotificationManager instance"""
    return NotificationManager(config=config)
