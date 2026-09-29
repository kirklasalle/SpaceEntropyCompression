#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_dpa\tasks\task_manager.py #command_line #python #source_code  
**Category:** Source Code  
**Status:** Active
"""









# Task Manager

**Created:** 2024-10-15  
**Updated:** 2025-07-26 10:26:57  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_dpa\tasks\task_manager.py #command_line #python #source_code  
**Category:** Source Code  
**Status:** Active

"""
Task Manager for ImpressionCore Personal Assistant

This module provides comprehensive task management functionality including
CRUD operations, categorization, prioritization, and lifecycle management.

Enhanced in Phase 8B with AI-powered scheduling, intelligent reminders,
and productivity analytics integration.

Created: 2025-01-03
Updated: 2025-06-07 (Phase 8B Integration)
Author: GitHub Copilot
Version: 1.1
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from .models import (
    Task, TaskPriority, TaskStatus, RecurrencePattern,
    TaskList, TaskDict
)
# Phase 8B: Lazy import AI components to avoid circular imports
# from .ai_enhanced_scheduler import AIEnhancedTaskScheduler
# from ..reminders.enhanced_reminder_engine import EnhancedReminderEngine
# from ..integration.enhanced_productivity_analytics import EnhancedProductivityAnalytics
from ..core.context_manager import ConversationSession
from ...core.utils.rich_logging import setup_rich_logging
from ...core.utils.rich_status_animation import StatusAnimation


class TaskManager:
    """
    Comprehensive task management system with intelligent categorization,
    prioritization, and lifecycle management.
    """
    
    def __init__(self, storage_path: Optional[str] = None, user_id: Optional[str] = None):
        """Initialize task manager with storage and user context"""
        self.logger = setup_rich_logging(__name__)
        self.user_id = user_id
        self.storage_path = Path(storage_path or "src/user_data/tasks")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Task storage
        self._tasks: Dict[str, Task] = {}
        self._categories: Set[str] = set()
        self._projects: Set[str] = set()
        self._tags: Set[str] = set()
        
        # Configuration
        self.auto_categorize = True
        self.smart_prioritization = True
        self.dependency_tracking = True        # Phase 8B: Initialize AI-Enhanced Components (lazy loading)
        self.ai_scheduler = None
        self.reminder_engine = None
        self.analytics = None
        self._ai_components_loaded = False
          # Load existing tasks
        self._load_tasks()
        
        self.logger.info("TaskManager initialized with AI enhancements", extra={
            "storage_path": str(self.storage_path),
            "user_id": self.user_id,
            "task_count": len(self._tasks),
            "ai_enhanced": True
        })
    
    def _load_ai_components(self):
        """Lazy load AI components to avoid circular imports"""
        if self._ai_components_loaded:
            return
        
        try:
            # Import AI components dynamically
            from .ai_enhanced_scheduler import AIEnhancedTaskScheduler
            from ..reminders.enhanced_reminder_engine import EnhancedReminderEngine
            from ..integration.enhanced_productivity_analytics import EnhancedProductivityAnalytics
            
            self.ai_scheduler = AIEnhancedTaskScheduler()
            self.reminder_engine = EnhancedReminderEngine()
            self.analytics = EnhancedProductivityAnalytics()
            self._ai_components_loaded = True
            
            self.logger.info("AI components loaded successfully")
            
        except ImportError as e:
            self.logger.warning(f"AI components not available: {e}")
            # Create mock objects to prevent errors
            self.ai_scheduler = None
            self.reminder_engine = None
            self.analytics = None
    
    def create_task(self, 
                   title: str,
                   description: Optional[str] = None,
                   category: Optional[str] = None,
                   priority: Optional[TaskPriority] = None,
                   due_date: Optional[datetime] = None,
                   tags: Optional[List[str]] = None,
                   project: Optional[str] = None,
                   **kwargs) -> Task:
        """
        Create a new task with intelligent categorization and prioritization
        
        Args:
            title: Task title (required)
            description: Detailed task description
            category: Task category (auto-detected if None)
            priority: Task priority (auto-calculated if None)
            due_date: Task due date
            tags: List of tags
            project: Project association
            **kwargs: Additional task parameters
        
        Returns:
            Created Task object
        """
        animation = StatusAnimation(
            total_steps=5,
            description="Creating task"
        )
        
        try:
            animation.start()
            
            # Step 1: Validate input
            animation.update(1, "Validating input")
            if not title or not title.strip():
                raise ValueError("Task title cannot be empty")
            
            # Step 2: Create base task
            animation.update(2, "Creating base task")
            task = Task(
                title=title.strip(),
                description=description,
                user_id=self.user_id,
                **kwargs
            )
            
            # Step 3: Auto-categorize if needed
            animation.update(3, "Processing categorization")
            if category:
                task.category = category
            elif self.auto_categorize:
                task.category = self._auto_categorize(title, description)
            
            # Step 4: Auto-prioritize if needed
            animation.update(4, "Calculating priority")
            if priority:
                task.priority = priority
            elif self.smart_prioritization:
                task.priority = self._auto_prioritize(task, due_date)
            
            # Step 5: Set additional properties
            animation.update(5, "Finalizing task")
            if due_date:
                task.due_date = due_date
            
            if tags:
                task.tags = list(set(tags))  # Remove duplicates
                self._tags.update(task.tags)
            
            if project:
                task.project = project
                self._projects.add(project)
              # Store task
            self._tasks[task.id] = task
            self._categories.add(task.category)
              # Phase 8B: AI-Enhanced Features Integration
            self._load_ai_components()  # Lazy load AI components
            
            try:
                # 1. Intelligent scheduling optimization
                if due_date and self.ai_scheduler:
                    optimized_schedule = self.ai_scheduler.optimize_task_schedule(
                        task, list(self._tasks.values())
                    )
                    if optimized_schedule:
                        task.ai_schedule_data = optimized_schedule
                
                # 2. Create intelligent reminders
                if self.reminder_engine:
                    reminder_config = self.reminder_engine.create_smart_reminders(task)
                    if reminder_config:
                        task.reminder_config = reminder_config
                
                # 3. Update productivity analytics
                if self.analytics:
                    self.analytics.track_task_creation(task)
                
            except Exception as ai_error:
                self.logger.warning("AI enhancement failed, continuing with basic task", 
                                  extra={"task_id": task.id, "error": str(ai_error)})
            
            # Save to storage
            self._save_task(task)
            
            animation.complete("Task created successfully")
            
            self.logger.info("Task created", extra={
                "task_id": task.id,
                "title": task.title,
                "category": task.category,
                "priority": task.priority.name
            })
            
            return task
            
        except Exception as e:
            animation.fail(f"Failed to create task: {str(e)}")
            self.logger.error("Task creation failed", extra={
                "title": title,
                "error": str(e)
            })
            raise
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Retrieve a task by ID"""
        return self._tasks.get(task_id)
    
    def update_task(self, task_id: str, **updates) -> bool:
        """
        Update a task with new information
        
        Args:
            task_id: Task identifier
            **updates: Fields to update
        
        Returns:
            True if task was updated, False if not found
        """
        task = self._tasks.get(task_id)
        if not task:
            self.logger.warning("Task not found for update", extra={"task_id": task_id})
            return False
        
        # Track what changed
        changes = {}
        
        # Update allowed fields
        updatable_fields = {
            'title', 'description', 'category', 'priority', 'due_date',
            'start_date', 'tags', 'project', 'progress_percentage'
        }
        
        for field, value in updates.items():
            if field in updatable_fields and hasattr(task, field):
                old_value = getattr(task, field)
                if old_value != value:
                    setattr(task, field, value)
                    changes[field] = {'old': old_value, 'new': value}
        
        if changes:
            task.updated_at = datetime.now()
            self._save_task(task)
            
            self.logger.info("Task updated", extra={
                "task_id": task_id,
                "changes": changes
            })
        
        return True
    
    def complete_task(self, task_id: str) -> bool:
        """Mark a task as completed"""
        task = self._tasks.get(task_id)
        if not task:
            return False
        
        task.update_status(TaskStatus.COMPLETED)
        task.progress_percentage = 100
        
        self._save_task(task)
        
        self.logger.info("Task completed", extra={
            "task_id": task_id,
            "title": task.title,
            "completed_at": task.completed_at.isoformat()
        })
        
        # Handle recurring tasks
        if task.is_recurring and task.recurrence_pattern:
            self._create_recurring_instance(task)
        
        return True
    
    def delete_task(self, task_id: str, soft_delete: bool = True) -> bool:
        """Delete a task (soft delete by default)"""
        task = self._tasks.get(task_id)
        if not task:
            return False
        
        if soft_delete:
            task.is_deleted = True
            task.updated_at = datetime.now()
            self._save_task(task)
        else:
            del self._tasks[task_id]
            self._remove_task_file(task_id)
        
        self.logger.info("Task deleted", extra={
            "task_id": task_id,
            "soft_delete": soft_delete
        })
        
        return True
    
    def list_tasks(self,
                  category: Optional[str] = None,
                  status: Optional[TaskStatus] = None,
                  priority: Optional[TaskPriority] = None,
                  project: Optional[str] = None,
                  tags: Optional[List[str]] = None,
                  due_before: Optional[datetime] = None,
                  include_completed: bool = False,
                  include_deleted: bool = False) -> TaskList:
        """
        List tasks with filtering options
        
        Args:
            category: Filter by category
            status: Filter by status
            priority: Filter by priority
            project: Filter by project
            tags: Filter by tags (must have all specified tags)
            due_before: Filter by due date
            include_completed: Include completed tasks
            include_deleted: Include deleted tasks
        
        Returns:
            List of matching tasks
        """
        tasks = []
        
        for task in self._tasks.values():
            # Skip deleted tasks unless explicitly requested
            if task.is_deleted and not include_deleted:
                continue
            
            # Skip completed tasks unless explicitly requested
            if task.status == TaskStatus.COMPLETED and not include_completed:
                continue
            
            # Apply filters
            if category and task.category != category:
                continue
            
            if status and task.status != status:
                continue
            
            if priority and task.priority != priority:
                continue
            
            if project and task.project != project:
                continue
            
            if tags and not all(tag in task.tags for tag in tags):
                continue
            
            if due_before and task.due_date and task.due_date > due_before:
                continue
            
            tasks.append(task)
        
        # Sort by priority and due date
        tasks.sort(key=lambda t: (
            -t.priority.value,  # Higher priority first
            t.due_date or datetime.max,  # Due date (None treated as far future)
            t.created_at  # Creation date as tiebreaker
        ))
        
        return tasks
    
    def get_overdue_tasks(self) -> TaskList:
        """Get all overdue tasks"""
        return [task for task in self._tasks.values() 
                if task.is_overdue() and not task.is_deleted]
    
    def get_upcoming_tasks(self, days: int = 7) -> TaskList:
        """Get tasks due within specified days"""
        cutoff = datetime.now() + timedelta(days=days)
        return self.list_tasks(due_before=cutoff, include_completed=False)
    
    def search_tasks(self, query: str) -> TaskList:
        """Search tasks by title, description, and tags"""
        query_lower = query.lower()
        results = []
        
        for task in self._tasks.values():
            if task.is_deleted:
                continue
            
            # Search in title
            if query_lower in task.title.lower():
                results.append(task)
                continue
            
            # Search in description
            if task.description and query_lower in task.description.lower():
                results.append(task)
                continue
            
            # Search in tags
            if any(query_lower in tag.lower() for tag in task.tags):
                results.append(task)
                continue
        
        return results
      # Phase 8B: AI-Enhanced Methods
    
    def get_ai_task_recommendations(self, context: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Get AI-powered task recommendations based on current context and user patterns
        
        Args:
            context: Optional context information (time of day, location, etc.)
        
        Returns:
            List of task recommendations with reasoning
        """
        self._load_ai_components()
        
        try:
            # Get current task context
            active_tasks = [t for t in self._tasks.values() if not t.is_deleted and t.status != TaskStatus.COMPLETED]
            
            # Use AI scheduler for intelligent recommendations
            if self.ai_scheduler:
                recommendations = self.ai_scheduler.generate_task_recommendations(
                    active_tasks, context or {}
                )
                
                # Track analytics
                if self.analytics:
                    self.analytics.track_recommendation_request(len(recommendations))
                
                return recommendations
            else:
                # Fallback to basic recommendations
                return self._get_basic_recommendations(active_tasks)
                
        except Exception as e:
            self.logger.error("Failed to get AI recommendations", extra={"error": str(e)})
            return []
    
    def optimize_task_schedule(self, time_window_hours: int = 24) -> Dict[str, Any]:
        """
        Get optimized task schedule using AI-enhanced scheduling
        
        Args:
            time_window_hours: Hours to optimize for
        
        Returns:
            Optimized schedule with task priorities and timing
        """
        self._load_ai_components()
        
        try:
            active_tasks = [t for t in self._tasks.values() 
                          if not t.is_deleted and t.status != TaskStatus.COMPLETED]
            
            if self.ai_scheduler:
                schedule = self.ai_scheduler.optimize_schedule(active_tasks, time_window_hours)
                
                # Update analytics
                if self.analytics:
                    self.analytics.track_schedule_optimization(len(active_tasks), schedule)
                
                return schedule
            else:
                # Fallback to basic scheduling
                return self._get_basic_schedule(active_tasks, time_window_hours)
                
        except Exception as e:
            self.logger.error("Failed to optimize schedule", extra={"error": str(e)})
            return {}
    
    def get_productivity_insights(self) -> Dict[str, Any]:
        """
        Get comprehensive productivity insights from analytics engine
        
        Returns:
            Productivity metrics, trends, and recommendations
        """
        try:
            # Get all tasks for analysis
            all_tasks = list(self._tasks.values())
            
            # Generate insights using analytics engine
            insights = self.analytics.generate_productivity_insights(all_tasks)
            
            return insights
        except Exception as e:
            self.logger.error("Failed to generate insights", extra={"error": str(e)})
            return {}
    
    def update_task_with_ai_enhancements(self, task_id: str) -> bool:
        """
        Update existing task with AI enhancements (reminders, schedule optimization)
        
        Args:
            task_id: Task to enhance
        
        Returns:
            True if successfully enhanced
        """
        task = self.get_task(task_id)
        if not task:
            return False
        
        try:
            # Add intelligent reminders if not present
            if not hasattr(task, 'reminder_config'):
                reminder_config = self.reminder_engine.create_smart_reminders(task)
                if reminder_config:
                    task.reminder_config = reminder_config
            
            # Update AI schedule data
            all_tasks = list(self._tasks.values())
            optimized_schedule = self.ai_scheduler.optimize_task_schedule(task, all_tasks)
            if optimized_schedule:
                task.ai_schedule_data = optimized_schedule
            
            # Update analytics
            self.analytics.track_task_enhancement(task)
            
            # Save updated task
            self._save_task(task)
            
            self.logger.info("Task enhanced with AI features", extra={"task_id": task_id})
            return True
            
        except Exception as e:
            self.logger.error("Failed to enhance task", extra={"task_id": task_id, "error": str(e)})
            return False
    
    # End Phase 8B AI-Enhanced Methods
    
    def _auto_categorize(self, title: str, description: Optional[str] = None) -> str:
        """Automatically categorize task based on content"""
        text = f"{title} {description or ''}".lower()
        
        # Category keywords mapping
        category_keywords = {
            'work': ['meeting', 'project', 'deadline', 'presentation', 'client', 'email', 'call'],
            'personal': ['family', 'friend', 'birthday', 'anniversary', 'personal', 'self'],
            'health': ['doctor', 'appointment', 'exercise', 'gym', 'medication', 'health'],
            'shopping': ['buy', 'purchase', 'store', 'shop', 'groceries', 'amazon'],
            'finance': ['pay', 'bill', 'bank', 'money', 'budget', 'tax', 'invoice'],
            'learning': ['study', 'course', 'book', 'learn', 'read', 'tutorial'],
            'maintenance': ['fix', 'repair', 'clean', 'organize', 'maintenance', 'update']
        }
        
        # Score each category
        category_scores = {}
        for category, keywords in category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                category_scores[category] = score
        
        # Return highest scoring category or default
        if category_scores:
            return max(category_scores.items(), key=lambda x: x[1])[0]
        
        return 'general'
    
    def _auto_prioritize(self, task: Task, due_date: Optional[datetime] = None) -> TaskPriority:
        """Automatically determine task priority based on content and due date"""
        priority_score = 2  # Start with MEDIUM
        
        title_lower = task.title.lower()
        desc_lower = (task.description or '').lower()
        text = f"{title_lower} {desc_lower}"
        
        # Urgency keywords
        urgent_keywords = ['urgent', 'asap', 'emergency', 'critical', 'important', 'deadline']
        high_keywords = ['meeting', 'presentation', 'client', 'boss', 'interview']
        low_keywords = ['maybe', 'someday', 'optional', 'nice to have']
        
        # Adjust based on keywords
        if any(keyword in text for keyword in urgent_keywords):
            priority_score += 2
        elif any(keyword in text for keyword in high_keywords):
            priority_score += 1
        elif any(keyword in text for keyword in low_keywords):
            priority_score -= 1
        
        # Adjust based on due date
        if due_date:
            days_until_due = (due_date - datetime.now()).days
            if days_until_due <= 1:
                priority_score += 2
            elif days_until_due <= 3:
                priority_score += 1
            elif days_until_due > 30:
                priority_score -= 1
        
        # Clamp to valid range
        priority_score = max(1, min(5, priority_score))
        
        return TaskPriority(priority_score)
    
    def _create_recurring_instance(self, completed_task: Task):
        """Create next instance of a recurring task"""
        if not completed_task.recurrence_pattern:
            return
        
        # Calculate next due date
        next_due_date = None
        if completed_task.due_date and completed_task.recurrence_interval:
            if completed_task.recurrence_pattern == RecurrencePattern.DAILY:
                next_due_date = completed_task.due_date + timedelta(days=completed_task.recurrence_interval)
            elif completed_task.recurrence_pattern == RecurrencePattern.WEEKLY:
                next_due_date = completed_task.due_date + timedelta(weeks=completed_task.recurrence_interval)
            elif completed_task.recurrence_pattern == RecurrencePattern.MONTHLY:
                # Approximate monthly recurrence
                next_due_date = completed_task.due_date + timedelta(days=30 * completed_task.recurrence_interval)
        
        # Create new task instance
        new_task = self.create_task(
            title=completed_task.title,
            description=completed_task.description,
            category=completed_task.category,
            priority=completed_task.priority,
            due_date=next_due_date,
            tags=completed_task.tags.copy(),
            project=completed_task.project
        )
        
        # Copy recurring properties
        new_task.is_recurring = True
        new_task.recurrence_pattern = completed_task.recurrence_pattern
        new_task.recurrence_interval = completed_task.recurrence_interval
        
        self._save_task(new_task)
        
        self.logger.info("Recurring task instance created", extra={
            "original_task_id": completed_task.id,
            "new_task_id": new_task.id,
            "next_due_date": next_due_date.isoformat() if next_due_date else None
        })
    
    def _load_tasks(self):
        """Load tasks from storage"""
        try:
            tasks_file = self.storage_path / "tasks.json"
            if tasks_file.exists():
                with open(tasks_file, 'r', encoding='utf-8') as f:
                    tasks_data = json.load(f)
                
                for task_data in tasks_data.get('tasks', []):
                    task = self._dict_to_task(task_data)
                    self._tasks[task.id] = task
                    self._categories.add(task.category)
                    if task.project:
                        self._projects.add(task.project)
                    self._tags.update(task.tags)
                
                self.logger.info("Tasks loaded from storage", extra={
                    "task_count": len(self._tasks)
                })
        
        except Exception as e:
            self.logger.error("Failed to load tasks", extra={"error": str(e)})
    
    def _save_task(self, task: Task):
        """Save a single task to storage"""
        try:
            # Save to main tasks file
            self._save_all_tasks()
        except Exception as e:
            self.logger.error("Failed to save task", extra={
                "task_id": task.id,
                "error": str(e)
            })
    
    def _save_all_tasks(self):
        """Save all tasks to storage"""
        try:
            tasks_file = self.storage_path / "tasks.json"
            
            tasks_data = {
                'tasks': [task.to_dict() for task in self._tasks.values()],
                'metadata': {
                    'last_updated': datetime.now().isoformat(),
                    'task_count': len(self._tasks),
                    'categories': list(self._categories),
                    'projects': list(self._projects),
                    'tags': list(self._tags)
                }
            }
            
            with open(tasks_file, 'w', encoding='utf-8') as f:
                json.dump(tasks_data, f, indent=2, ensure_ascii=False)
        
        except Exception as e:
            self.logger.error("Failed to save tasks", extra={"error": str(e)})
    
    def _remove_task_file(self, task_id: str):
        """Remove task file from storage (for hard delete)"""
        # For individual task files (future enhancement)
        pass
    
    def _dict_to_task(self, task_data: Dict[str, Any]) -> Task:
        """Convert dictionary to Task object"""
        # Convert enum values back to enums
        if 'priority' in task_data:
            task_data['priority'] = TaskPriority(task_data['priority'])
        
        if 'status' in task_data:
            task_data['status'] = TaskStatus(task_data['status'])
        
        if 'recurrence_pattern' in task_data and task_data['recurrence_pattern']:
            task_data['recurrence_pattern'] = RecurrencePattern(task_data['recurrence_pattern'])
        
        # Convert datetime strings back to datetime objects
        datetime_fields = ['created_at', 'updated_at', 'due_date', 'start_date', 'completed_at']
        for field in datetime_fields:
            if field in task_data and task_data[field]:
                task_data[field] = datetime.fromisoformat(task_data[field])
        
        # Handle metadata
        if 'metadata' in task_data:
            from .models import TaskMetadata
            metadata_dict = task_data.pop('metadata')
            task_data['metadata'] = TaskMetadata(**metadata_dict)
        
        return Task(**task_data)
    
    def _get_basic_recommendations(self, active_tasks: List[Task]) -> List[Dict[str, Any]]:
        """Fallback method for basic task recommendations when AI is not available"""
        recommendations = []
        
        # Recommend overdue tasks
        overdue_tasks = [t for t in active_tasks if t.due_date and t.due_date < datetime.now()]
        for task in overdue_tasks[:3]:  # Top 3 overdue
            recommendations.append({
                "task_id": task.id,
                "title": task.title,
                "reasoning": "This task is overdue",
                "priority_score": 0.9,
                "recommended_action": "complete_immediately"
            })
        
        # Recommend high priority tasks due soon
        upcoming_high_priority = [
            t for t in active_tasks 
            if t.priority == TaskPriority.HIGH and t.due_date and 
            t.due_date > datetime.now() and 
            t.due_date < datetime.now() + timedelta(days=1)
        ]
        for task in upcoming_high_priority[:2]:  # Top 2
            recommendations.append({
                "task_id": task.id,
                "title": task.title,
                "reasoning": "High priority task due soon",
                "priority_score": 0.8,
                "recommended_action": "schedule_today"
            })
        
        return recommendations
    
    def _get_basic_schedule(self, active_tasks: List[Task], time_window_hours: int) -> Dict[str, Any]:
        """Fallback method for basic scheduling when AI is not available"""
        schedule = {
            "time_blocks": [],
            "optimization_score": 0.5,
            "generated_at": datetime.now().isoformat()
        }
        
        # Sort tasks by priority and due date
        sorted_tasks = sorted(
            active_tasks,
            key=lambda t: (
                t.priority.value if t.priority else 5,
                t.due_date if t.due_date else datetime.max
            )
        )
        
        # Create basic time blocks
        current_time = datetime.now()
        for i, task in enumerate(sorted_tasks[:10]):  # Limit to 10 tasks
            start_time = current_time + timedelta(hours=i * 2)
            schedule["time_blocks"].append({
                "task_id": task.id,
                "task_title": task.title,
                "start_time": start_time.strftime("%H:%M"),
                "duration_minutes": 120,  # 2 hours default
                "priority": task.priority.name if task.priority else "MEDIUM"
            })
        
        return schedule
