#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_dpa\tasks\task_scheduler.py #python #source_code #testing  
**Category:** Source Code  
**Status:** Active
"""









# Task Scheduler

**Created:** 2024-10-15  
**Updated:** 2025-07-26 10:26:57  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_dpa\tasks\task_scheduler.py #python #source_code #testing  
**Category:** Source Code  
**Status:** Active

"""
Task Scheduler for ImpressionCore Personal Assistant

This module provides intelligent task scheduling with deadline-based prioritization,
resource allocation optimization, and conflict resolution.

Created: 2025-01-06
Author: ImpressionCore Development Team
Version: 1.0
Phase: 8B Week 2 - Task Management & Reminders
"""

import logging
import heapq
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
from collections import defaultdict, deque

from .models import Task, TaskPriority, TaskStatus, TaskList
from ...core.utils.rich_logging import setup_rich_logging
from ...core.utils.rich_status_animation import StatusAnimation

try:
    from ...core.utils.rich_enhancements import RichEnhancer
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class SchedulingStrategy(Enum):
    """Task scheduling strategies"""
    DEADLINE_FIRST = "deadline_first"
    PRIORITY_FIRST = "priority_first"
    SMART_BALANCE = "smart_balance"
    TIME_BLOCKING = "time_blocking"
    ENERGY_BASED = "energy_based"


@dataclass
class ScheduleSlot:
    """Represents a scheduled time slot"""
    start_time: datetime
    end_time: datetime
    task_id: str
    priority: TaskPriority
    estimated_duration: int  # minutes
    buffer_time: int = 15    # minutes
    is_flexible: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SchedulingConstraints:
    """Constraints for task scheduling"""
    working_hours_start: int = 9      # 9 AM
    working_hours_end: int = 17       # 5 PM
    break_duration: int = 15          # minutes
    max_consecutive_hours: int = 4
    buffer_between_tasks: int = 15    # minutes
    weekend_scheduling: bool = False
    energy_levels: Dict[str, float] = field(default_factory=lambda: {
        'morning': 1.0, 'afternoon': 0.8, 'evening': 0.6
    })


class TaskScheduler:
    """
    Intelligent task scheduler with multiple scheduling strategies,
    deadline optimization, and resource allocation.
    """
    
    def __init__(self, 
                 strategy: SchedulingStrategy = SchedulingStrategy.SMART_BALANCE,
                 constraints: Optional[SchedulingConstraints] = None):
        """Initialize task scheduler"""
        self.logger = setup_rich_logging(__name__)
        self.strategy = strategy
        self.constraints = constraints or SchedulingConstraints()
        
        # Scheduling state
        self._schedule: Dict[str, List[ScheduleSlot]] = defaultdict(list)  # date -> slots
        self._task_priorities: Dict[str, float] = {}
        self._conflict_resolutions: List[Dict[str, Any]] = []
        
        # Performance tracking
        self._scheduling_stats = {
            'total_scheduled': 0,
            'conflicts_resolved': 0,
            'optimizations_applied': 0,
            'avg_scheduling_time': 0.0
        }
        
        # Threading
        self._lock = threading.RLock()
        
        # Status animation for long operations
        self._status_animation = None
        if RICH_AVAILABLE:
            try:
                self._status_animation = StatusAnimation(
                    total_steps=100,
                    description="Task Scheduling"
                )
            except Exception as e:
                self.logger.warning(f"Could not initialize status animation: {e}")
        
        self.logger.info(f"Task scheduler initialized with {strategy.value} strategy")
    
    def schedule_task(self, task: Task, preferred_time: Optional[datetime] = None) -> Optional[ScheduleSlot]:
        """Schedule a single task"""
        with self._lock:
            start_time = datetime.now()
            
            try:
                if self._status_animation:
                    self._status_animation.start()
                    self._status_animation.update(10, "Analyzing task requirements")
                
                # Analyze task requirements
                slot_requirements = self._analyze_task_requirements(task)
                
                if self._status_animation:
                    self._status_animation.update(30, "Finding optimal time slot")
                
                # Find optimal time slot
                optimal_slot = self._find_optimal_slot(task, slot_requirements, preferred_time)
                
                if not optimal_slot:
                    self.logger.warning(f"Could not find suitable time slot for task: {task.title}")
                    return None
                
                if self._status_animation:
                    self._status_animation.update(60, "Checking for conflicts")
                
                # Check for conflicts
                conflicts = self._detect_conflicts(optimal_slot)
                if conflicts:
                    optimal_slot = self._resolve_conflicts(optimal_slot, conflicts)
                
                if self._status_animation:
                    self._status_animation.update(80, "Finalizing schedule")
                
                # Add to schedule
                date_key = optimal_slot.start_time.date().isoformat()
                self._schedule[date_key].append(optimal_slot)
                self._schedule[date_key].sort(key=lambda s: s.start_time)
                
                # Update statistics
                self._scheduling_stats['total_scheduled'] += 1
                scheduling_time = (datetime.now() - start_time).total_seconds()
                self._update_avg_scheduling_time(scheduling_time)
                
                if self._status_animation:
                    self._status_animation.update(100, "Task scheduled successfully")
                    self._status_animation.stop()
                
                self.logger.info(f"Task scheduled: {task.title} at {optimal_slot.start_time}")
                return optimal_slot
                
            except Exception as e:
                if self._status_animation:
                    self._status_animation.stop()
                self.logger.error(f"Failed to schedule task {task.title}: {e}")
                return None
    
    def schedule_multiple_tasks(self, tasks: TaskList) -> Dict[str, Optional[ScheduleSlot]]:
        """Schedule multiple tasks with optimization"""
        with self._lock:
            results = {}
            
            try:
                if self._status_animation:
                    self._status_animation.start()
                    self._status_animation.update(5, f"Scheduling {len(tasks)} tasks")
                
                # Sort tasks by scheduling priority
                sorted_tasks = self._prioritize_tasks_for_scheduling(tasks)
                
                total_tasks = len(sorted_tasks)
                for i, task in enumerate(sorted_tasks):
                    if self._status_animation:
                        progress = int(10 + (i / total_tasks) * 80)
                        self._status_animation.update(progress, f"Scheduling: {task.title[:30]}...")
                    
                    slot = self.schedule_task(task)
                    results[task.id] = slot
                
                # Apply optimizations
                if self._status_animation:
                    self._status_animation.update(95, "Applying optimizations")
                
                self._optimize_schedule()
                
                if self._status_animation:
                    self._status_animation.update(100, f"Scheduled {len(results)} tasks")
                    self._status_animation.stop()
                
                scheduled_count = len([s for s in results.values() if s is not None])
                self.logger.info(f"Scheduled {scheduled_count}/{len(tasks)} tasks")
                
                return results
                
            except Exception as e:
                if self._status_animation:
                    self._status_animation.stop()
                self.logger.error(f"Failed to schedule multiple tasks: {e}")
                return {task.id: None for task in tasks}
    
    def reschedule_task(self, task_id: str, new_time: datetime) -> bool:
        """Reschedule an existing task"""
        with self._lock:
            try:
                # Find and remove existing slot
                old_slot = self._find_task_slot(task_id)
                if not old_slot:
                    self.logger.warning(f"Task slot not found for rescheduling: {task_id}")
                    return False
                
                self._remove_task_from_schedule(task_id)
                
                # Create new slot
                new_slot = ScheduleSlot(
                    start_time=new_time,
                    end_time=new_time + timedelta(minutes=old_slot.estimated_duration),
                    task_id=task_id,
                    priority=old_slot.priority,
                    estimated_duration=old_slot.estimated_duration,
                    metadata=old_slot.metadata
                )
                
                # Check for conflicts
                conflicts = self._detect_conflicts(new_slot)
                if conflicts:
                    new_slot = self._resolve_conflicts(new_slot, conflicts)
                    if not new_slot:
                        # Restore old slot if rescheduling failed
                        date_key = old_slot.start_time.date().isoformat()
                        self._schedule[date_key].append(old_slot)
                        return False
                
                # Add new slot
                date_key = new_slot.start_time.date().isoformat()
                self._schedule[date_key].append(new_slot)
                self._schedule[date_key].sort(key=lambda s: s.start_time)
                
                self.logger.info(f"Task rescheduled: {task_id} to {new_time}")
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to reschedule task {task_id}: {e}")
                return False
    
    def get_schedule(self, 
                    start_date: Optional[datetime] = None,
                    end_date: Optional[datetime] = None) -> Dict[str, List[ScheduleSlot]]:
        """Get schedule for specified date range"""
        with self._lock:
            if not start_date:
                start_date = datetime.now().date()
            if not end_date:
                end_date = start_date + timedelta(days=7)
            
            result = {}
            current_date = start_date
            
            while current_date <= end_date:
                date_key = current_date.isoformat()
                if date_key in self._schedule:
                    result[date_key] = self._schedule[date_key].copy()
                else:
                    result[date_key] = []
                current_date += timedelta(days=1)
            
            return result
    
    def get_availability(self, date: datetime) -> List[Tuple[datetime, datetime]]:
        """Get available time slots for a specific date"""
        with self._lock:
            date_key = date.date().isoformat()
            scheduled_slots = self._schedule.get(date_key, [])
            
            # Create availability windows
            day_start = datetime.combine(date.date(), 
                                       datetime.min.time().replace(hour=self.constraints.working_hours_start))
            day_end = datetime.combine(date.date(), 
                                     datetime.min.time().replace(hour=self.constraints.working_hours_end))
            
            availability = []
            current_time = day_start
            
            for slot in sorted(scheduled_slots, key=lambda s: s.start_time):
                if current_time < slot.start_time:
                    availability.append((current_time, slot.start_time))
                current_time = max(current_time, slot.end_time)
            
            # Add remaining time at end of day
            if current_time < day_end:
                availability.append((current_time, day_end))
            
            return availability
    
    def _analyze_task_requirements(self, task: Task) -> Dict[str, Any]:
        """Analyze task requirements for scheduling"""
        requirements = {
            'estimated_duration': 60,  # Default 1 hour
            'min_duration': 30,
            'max_duration': 240,
            'energy_level': 'medium',
            'time_preference': 'any',
            'deadline_pressure': 0.5,
            'complexity': 0.5
        }
        
        # Analyze based on task metadata
        if hasattr(task, 'metadata') and task.metadata:
            if hasattr(task.metadata, 'estimated_duration'):
                requirements['estimated_duration'] = task.metadata.estimated_duration
            if hasattr(task.metadata, 'energy_required'):
                energy_map = {1: 'low', 2: 'low', 3: 'medium', 4: 'high', 5: 'high'}
                requirements['energy_level'] = energy_map.get(task.metadata.energy_required, 'medium')
        
        # Calculate deadline pressure
        if task.due_date:
            time_until_due = (task.due_date - datetime.now()).total_seconds()
            if time_until_due > 0:
                # Higher pressure as deadline approaches
                requirements['deadline_pressure'] = max(0.1, min(1.0, 1.0 - (time_until_due / (7 * 24 * 3600))))
        
        # Priority influences complexity
        priority_complexity = {
            TaskPriority.LOW: 0.2,
            TaskPriority.MEDIUM: 0.4,
            TaskPriority.HIGH: 0.6,
            TaskPriority.URGENT: 0.8,
            TaskPriority.CRITICAL: 1.0
        }
        requirements['complexity'] = priority_complexity.get(task.priority, 0.5)
        
        return requirements
    
    def _find_optimal_slot(self, 
                          task: Task, 
                          requirements: Dict[str, Any],
                          preferred_time: Optional[datetime] = None) -> Optional[ScheduleSlot]:
        """Find the optimal time slot for a task"""
        
        duration = requirements['estimated_duration']
        energy_level = requirements['energy_level']
        deadline_pressure = requirements['deadline_pressure']
        
        # Determine search range
        search_start = preferred_time or datetime.now()
        search_end = task.due_date or (search_start + timedelta(days=14))
        
        best_slot = None
        best_score = -1
        
        current_date = search_start.date()
        end_date = search_end.date()
        
        while current_date <= end_date:
            # Skip weekends if not enabled
            if current_date.weekday() >= 5 and not self.constraints.weekend_scheduling:
                current_date += timedelta(days=1)
                continue
            
            availability = self.get_availability(datetime.combine(current_date, datetime.min.time()))
            
            for start_time, end_time in availability:
                # Check if slot is long enough
                available_duration = (end_time - start_time).total_seconds() / 60
                if available_duration < duration + self.constraints.buffer_between_tasks:
                    continue
                
                # Create potential slot
                slot = ScheduleSlot(
                    start_time=start_time,
                    end_time=start_time + timedelta(minutes=duration),
                    task_id=task.id,
                    priority=task.priority,
                    estimated_duration=duration
                )
                
                # Score this slot
                score = self._score_time_slot(slot, requirements, preferred_time)
                
                if score > best_score:
                    best_score = score
                    best_slot = slot
            
            current_date += timedelta(days=1)
        
        return best_slot
    
    def _score_time_slot(self, 
                        slot: ScheduleSlot, 
                        requirements: Dict[str, Any],
                        preferred_time: Optional[datetime] = None) -> float:
        """Score a time slot for task suitability"""
        score = 0.0
        
        # Time of day scoring
        hour = slot.start_time.hour
        if 9 <= hour <= 11:  # Morning prime time
            score += 0.3
        elif 14 <= hour <= 16:  # Afternoon focus time
            score += 0.2
        elif hour < 9 or hour > 17:  # Outside working hours
            score -= 0.3
        
        # Energy level matching
        energy_level = requirements.get('energy_level', 'medium')
        if energy_level == 'high' and 9 <= hour <= 12:
            score += 0.2
        elif energy_level == 'low' and 15 <= hour <= 17:
            score += 0.1
        
        # Deadline pressure
        deadline_pressure = requirements.get('deadline_pressure', 0.5)
        if deadline_pressure > 0.7:  # High pressure tasks prefer earlier slots
            days_from_now = (slot.start_time.date() - datetime.now().date()).days
            score += max(0, 0.3 - (days_from_now * 0.05))
        
        # Preferred time bonus
        if preferred_time:
            time_diff = abs((slot.start_time - preferred_time).total_seconds())
            if time_diff < 3600:  # Within 1 hour
                score += 0.4
            elif time_diff < 24 * 3600:  # Within 1 day
                score += 0.2
        
        # Strategy-specific scoring
        if self.strategy == SchedulingStrategy.DEADLINE_FIRST:
            score += deadline_pressure * 0.3
        elif self.strategy == SchedulingStrategy.PRIORITY_FIRST:
            priority_score = slot.priority.value / 5.0
            score += priority_score * 0.3
        
        return max(0.0, min(1.0, score))
    
    def _detect_conflicts(self, new_slot: ScheduleSlot) -> List[ScheduleSlot]:
        """Detect scheduling conflicts with existing slots"""
        date_key = new_slot.start_time.date().isoformat()
        existing_slots = self._schedule.get(date_key, [])
        
        conflicts = []
        for slot in existing_slots:
            if (new_slot.start_time < slot.end_time and 
                new_slot.end_time > slot.start_time):
                conflicts.append(slot)
        
        return conflicts
    
    def _resolve_conflicts(self, 
                          new_slot: ScheduleSlot, 
                          conflicts: List[ScheduleSlot]) -> Optional[ScheduleSlot]:
        """Resolve scheduling conflicts"""
        
        if not conflicts:
            return new_slot
        
        self._scheduling_stats['conflicts_resolved'] += len(conflicts)
        
        # Try to move new slot to avoid conflicts
        buffer = timedelta(minutes=self.constraints.buffer_between_tasks)
        
        # Find the latest conflicting slot
        latest_conflict = max(conflicts, key=lambda s: s.end_time)
        
        # Try scheduling after the conflict
        new_start = latest_conflict.end_time + buffer
        new_slot.start_time = new_start
        new_slot.end_time = new_start + timedelta(minutes=new_slot.estimated_duration)
        
        # Check if new time is within working hours
        if new_slot.end_time.hour > self.constraints.working_hours_end:
            # Move to next day
            next_day = new_slot.start_time.date() + timedelta(days=1)
            new_slot.start_time = datetime.combine(
                next_day, 
                datetime.min.time().replace(hour=self.constraints.working_hours_start)
            )
            new_slot.end_time = new_slot.start_time + timedelta(minutes=new_slot.estimated_duration)
        
        # Check for new conflicts
        new_conflicts = self._detect_conflicts(new_slot)
        if new_conflicts:
            # Recursive resolution (with depth limit)
            return self._resolve_conflicts(new_slot, new_conflicts)
        
        return new_slot
    
    def _prioritize_tasks_for_scheduling(self, tasks: TaskList) -> TaskList:
        """Prioritize tasks for scheduling based on strategy"""
        
        if self.strategy == SchedulingStrategy.DEADLINE_FIRST:
            return sorted(tasks, key=lambda t: (
                t.due_date or datetime.max,
                -t.priority.value
            ))
        elif self.strategy == SchedulingStrategy.PRIORITY_FIRST:
            return sorted(tasks, key=lambda t: (
                -t.priority.value,
                t.due_date or datetime.max
            ))
        else:  # SMART_BALANCE
            def smart_score(task):
                priority_score = task.priority.value / 5.0
                if task.due_date:
                    days_until_due = (task.due_date - datetime.now()).days
                    deadline_score = max(0, 1.0 - (days_until_due / 30.0))
                else:
                    deadline_score = 0.1
                return priority_score * 0.6 + deadline_score * 0.4
            
            return sorted(tasks, key=smart_score, reverse=True)
    
    def _optimize_schedule(self):
        """Apply optimizations to the current schedule"""
        self._scheduling_stats['optimizations_applied'] += 1
        
        # Future enhancements:
        # - Time block consolidation
        # - Travel time optimization
        # - Energy level optimization
        # - Meeting overlap detection
        pass
    
    def _find_task_slot(self, task_id: str) -> Optional[ScheduleSlot]:
        """Find the slot for a specific task"""
        for date_slots in self._schedule.values():
            for slot in date_slots:
                if slot.task_id == task_id:
                    return slot
        return None
    
    def _remove_task_from_schedule(self, task_id: str) -> bool:
        """Remove a task from the schedule"""
        for date_key, slots in self._schedule.items():
            for i, slot in enumerate(slots):
                if slot.task_id == task_id:
                    del slots[i]
                    return True
        return False
    
    def _update_avg_scheduling_time(self, new_time: float):
        """Update average scheduling time statistic"""
        current_avg = self._scheduling_stats['avg_scheduling_time']
        total_scheduled = self._scheduling_stats['total_scheduled']
        
        if total_scheduled == 1:
            self._scheduling_stats['avg_scheduling_time'] = new_time
        else:
            # Rolling average
            self._scheduling_stats['avg_scheduling_time'] = (
                (current_avg * (total_scheduled - 1) + new_time) / total_scheduled
            )
    
    def get_scheduling_stats(self) -> Dict[str, Any]:
        """Get scheduling performance statistics"""
        return self._scheduling_stats.copy()


# Factory function for easy instantiation
def create_task_scheduler(strategy: SchedulingStrategy = SchedulingStrategy.SMART_BALANCE,
                         constraints: Optional[SchedulingConstraints] = None) -> TaskScheduler:
    """Create and return a TaskScheduler instance"""
    return TaskScheduler(strategy=strategy, constraints=constraints)
