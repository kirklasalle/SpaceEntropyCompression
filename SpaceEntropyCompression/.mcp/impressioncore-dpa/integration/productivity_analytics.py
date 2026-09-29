#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_dpa\integration\productivity_analytics.py #command_line #python #source_code  
**Category:** Source Code  
**Status:** Active
"""









# Productivity Analytics

**Created:** 2024-10-15  
**Updated:** 2025-07-26 10:26:57  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_dpa\integration\productivity_analytics.py #command_line #python #source_code  
**Category:** Source Code  
**Status:** Active

"""
Productivity Analytics for ImpressionCore Assistant

This module provides comprehensive analytics and insights for task completion,
time tracking, and productivity patterns to help users optimize their workflow.

Created: June 6, 2025
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
from collections import defaultdict, Counter
import statistics

from ..tasks.models import Task, TaskPriority, TaskStatus
from ..reminders.reminder_engine import Reminder

# Configure logging
logger = logging.getLogger(__name__)

class AnalyticsTimeframe(Enum):
    """Time frames for analytics reporting."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

class ProductivityMetric(Enum):
    """Types of productivity metrics."""
    COMPLETION_RATE = "completion_rate"
    AVERAGE_COMPLETION_TIME = "average_completion_time"
    TASKS_PER_DAY = "tasks_per_day"
    PRIORITY_DISTRIBUTION = "priority_distribution"
    OVERDUE_RATE = "overdue_rate"
    TIME_TO_START = "time_to_start"
    FOCUS_SCORE = "focus_score"

@dataclass
class ProductivityStats:
    """Represents productivity statistics for a given period."""
    timeframe: AnalyticsTimeframe
    start_date: datetime
    end_date: datetime
    total_tasks: int = 0
    completed_tasks: int = 0
    overdue_tasks: int = 0
    average_completion_time: float = 0.0  # in hours
    completion_rate: float = 0.0  # percentage
    tasks_per_day: float = 0.0
    priority_distribution: Dict[str, int] = field(default_factory=dict)
    category_performance: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    time_patterns: Dict[str, Any] = field(default_factory=dict)
    focus_score: float = 0.0  # 0-100 scale
    productivity_trend: str = "stable"  # improving, declining, stable
    insights: List[str] = field(default_factory=list)

@dataclass
class TaskAnalytics:
    """Analytics for individual task performance."""
    task_id: str
    title: str
    category: str
    priority: TaskPriority
    created_at: datetime
    completed_at: Optional[datetime] = None
    due_date: Optional[datetime] = None
    time_to_complete: Optional[float] = None  # in hours
    time_to_start: Optional[float] = None  # in hours
    was_overdue: bool = False
    completion_score: float = 0.0  # 0-100 scale

class ProductivityAnalytics:
    """
    Main analytics engine for tracking and analyzing productivity metrics.
    """
    
    def __init__(self, data_storage_path: str = None):
        """
        Initialize productivity analytics.
        
        Args:
            data_storage_path: Path to store analytics data
        """
        self.data_storage_path = data_storage_path or "analytics_data.json"
        self.task_history: List[TaskAnalytics] = []
        self.reminder_history: List[Dict[str, Any]] = []
        self.session_data: Dict[str, Any] = {}
        
        # Load existing data
        self._load_analytics_data()
        
        logger.info("Productivity analytics initialized")
    
    def _load_analytics_data(self):
        """Load existing analytics data from storage."""
        try:
            with open(self.data_storage_path, 'r') as f:
                data = json.load(f)
                # Convert stored data back to objects
                self._deserialize_data(data)
                logger.info("Loaded existing analytics data")
        except (FileNotFoundError, json.JSONDecodeError):
            logger.info("Starting with fresh analytics data")
    
    def _save_analytics_data(self):
        """Save analytics data to storage."""
        try:
            data = self._serialize_data()
            with open(self.data_storage_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            logger.debug("Saved analytics data")
        except Exception as e:
            logger.error(f"Failed to save analytics data: {e}")
    
    def _serialize_data(self) -> Dict[str, Any]:
        """Serialize analytics data for storage."""
        return {
            'task_history': [
                {
                    'task_id': ta.task_id,
                    'title': ta.title,
                    'category': ta.category,
                    'priority': ta.priority.value,
                    'created_at': ta.created_at.isoformat(),
                    'completed_at': ta.completed_at.isoformat() if ta.completed_at else None,
                    'due_date': ta.due_date.isoformat() if ta.due_date else None,
                    'time_to_complete': ta.time_to_complete,
                    'time_to_start': ta.time_to_start,
                    'was_overdue': ta.was_overdue,
                    'completion_score': ta.completion_score
                }
                for ta in self.task_history
            ],
            'reminder_history': self.reminder_history,
            'session_data': self.session_data
        }
    
    def _deserialize_data(self, data: Dict[str, Any]):
        """Deserialize analytics data from storage."""
        self.task_history = []
        for task_data in data.get('task_history', []):
            self.task_history.append(TaskAnalytics(
                task_id=task_data['task_id'],
                title=task_data['title'],
                category=task_data['category'],
                priority=TaskPriority(task_data['priority']),
                created_at=datetime.fromisoformat(task_data['created_at']),
                completed_at=datetime.fromisoformat(task_data['completed_at']) if task_data['completed_at'] else None,
                due_date=datetime.fromisoformat(task_data['due_date']) if task_data['due_date'] else None,
                time_to_complete=task_data.get('time_to_complete'),
                time_to_start=task_data.get('time_to_start'),
                was_overdue=task_data.get('was_overdue', False),
                completion_score=task_data.get('completion_score', 0.0)
            ))
        
        self.reminder_history = data.get('reminder_history', [])
        self.session_data = data.get('session_data', {})
    
    def track_task_creation(self, task: Task):
        """
        Track when a task is created.
        
        Args:
            task: Task that was created
        """
        task_analytics = TaskAnalytics(
            task_id=task.id,
            title=task.title,
            category=task.category or "uncategorized",
            priority=task.priority,
            created_at=task.created_at,
            due_date=task.due_date
        )
        
        self.task_history.append(task_analytics)
        self._save_analytics_data()
        
        logger.debug(f"Tracked creation of task {task.id}")
    
    def track_task_completion(self, task: Task, completion_time: datetime = None):
        """
        Track when a task is completed.
        
        Args:
            task: Task that was completed
            completion_time: When the task was completed (defaults to now)
        """
        completion_time = completion_time or datetime.now()
        
        # Find the task in history
        for task_analytics in self.task_history:
            if task_analytics.task_id == task.id:
                task_analytics.completed_at = completion_time
                task_analytics.time_to_complete = (
                    (completion_time - task_analytics.created_at).total_seconds() / 3600
                )
                
                # Check if task was overdue
                if task_analytics.due_date and completion_time > task_analytics.due_date:
                    task_analytics.was_overdue = True
                
                # Calculate completion score
                task_analytics.completion_score = self._calculate_completion_score(task_analytics)
                
                self._save_analytics_data()
                logger.debug(f"Tracked completion of task {task.id}")
                break
    
    def track_task_start(self, task_id: str, start_time: datetime = None):
        """
        Track when work on a task is started.
        
        Args:
            task_id: ID of the task being started
            start_time: When work started (defaults to now)
        """
        start_time = start_time or datetime.now()
        
        # Find the task in history
        for task_analytics in self.task_history:
            if task_analytics.task_id == task_id:
                task_analytics.time_to_start = (
                    (start_time - task_analytics.created_at).total_seconds() / 3600
                )
                self._save_analytics_data()
                logger.debug(f"Tracked start of work on task {task_id}")
                break
    
    def track_reminder_interaction(self, reminder: Reminder, action: str, timestamp: datetime = None):
        """
        Track reminder interactions.
        
        Args:
            reminder: Reminder that was interacted with
            action: Action taken (dismissed, snoozed, completed, etc.)
            timestamp: When the interaction occurred
        """
        timestamp = timestamp or datetime.now()
        
        interaction = {
            'reminder_id': reminder.id,
            'reminder_type': reminder.reminder_type,
            'action': action,
            'timestamp': timestamp.isoformat(),
            'message': reminder.message
        }
        
        self.reminder_history.append(interaction)
        self._save_analytics_data()
        
        logger.debug(f"Tracked reminder interaction: {action} for reminder {reminder.id}")
    
    def _calculate_completion_score(self, task_analytics: TaskAnalytics) -> float:
        """
        Calculate a completion score for a task based on various factors.
        
        Args:
            task_analytics: Task analytics data
            
        Returns:
            Completion score (0-100)
        """
        score = 100.0
        
        # Penalize overdue completion
        if task_analytics.was_overdue:
            score -= 20.0
        
        # Reward quick completion for high priority tasks
        if task_analytics.priority == TaskPriority.HIGH and task_analytics.time_to_complete:
            if task_analytics.time_to_complete < 24:  # Completed within a day
                score += 10.0
        
        # Penalize long time to start
        if task_analytics.time_to_start and task_analytics.time_to_start > 48:  # More than 2 days to start
            score -= 15.0
        
        return max(0.0, min(100.0, score))
    
    def generate_productivity_stats(self, timeframe: AnalyticsTimeframe, 
                                  end_date: datetime = None) -> ProductivityStats:
        """
        Generate productivity statistics for a given timeframe.
        
        Args:
            timeframe: Time period to analyze
            end_date: End date for analysis (defaults to now)
            
        Returns:
            ProductivityStats object with analysis results
        """
        end_date = end_date or datetime.now()
        start_date = self._get_start_date(timeframe, end_date)
        
        # Filter tasks within the timeframe
        relevant_tasks = [
            ta for ta in self.task_history
            if start_date <= ta.created_at <= end_date
        ]
        
        if not relevant_tasks:
            return ProductivityStats(
                timeframe=timeframe,
                start_date=start_date,
                end_date=end_date
            )
        
        # Calculate basic stats
        total_tasks = len(relevant_tasks)
        completed_tasks = len([ta for ta in relevant_tasks if ta.completed_at])
        overdue_tasks = len([ta for ta in relevant_tasks if ta.was_overdue])
        
        completion_rate = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0
        
        # Calculate average completion time
        completion_times = [ta.time_to_complete for ta in relevant_tasks if ta.time_to_complete]
        avg_completion_time = statistics.mean(completion_times) if completion_times else 0
        
        # Calculate tasks per day
        days_in_period = (end_date - start_date).days + 1
        tasks_per_day = total_tasks / days_in_period if days_in_period > 0 else 0
        
        # Priority distribution
        priority_dist = Counter(ta.priority.value for ta in relevant_tasks)
        
        # Category performance
        category_perf = self._analyze_category_performance(relevant_tasks)
        
        # Time patterns
        time_patterns = self._analyze_time_patterns(relevant_tasks)
        
        # Focus score
        focus_score = self._calculate_focus_score(relevant_tasks)
        
        # Productivity trend
        trend = self._analyze_productivity_trend(timeframe, end_date)
        
        # Generate insights
        insights = self._generate_insights(relevant_tasks, completion_rate, avg_completion_time)
        
        return ProductivityStats(
            timeframe=timeframe,
            start_date=start_date,
            end_date=end_date,
            total_tasks=total_tasks,
            completed_tasks=completed_tasks,
            overdue_tasks=overdue_tasks,
            average_completion_time=avg_completion_time,
            completion_rate=completion_rate,
            tasks_per_day=tasks_per_day,
            priority_distribution=dict(priority_dist),
            category_performance=category_perf,
            time_patterns=time_patterns,
            focus_score=focus_score,
            productivity_trend=trend,
            insights=insights
        )
    
    def _get_start_date(self, timeframe: AnalyticsTimeframe, end_date: datetime) -> datetime:
        """Calculate start date based on timeframe."""
        if timeframe == AnalyticsTimeframe.DAILY:
            return end_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif timeframe == AnalyticsTimeframe.WEEKLY:
            return end_date - timedelta(days=7)
        elif timeframe == AnalyticsTimeframe.MONTHLY:
            return end_date - timedelta(days=30)
        elif timeframe == AnalyticsTimeframe.QUARTERLY:
            return end_date - timedelta(days=90)
        elif timeframe == AnalyticsTimeframe.YEARLY:
            return end_date - timedelta(days=365)
        else:
            return end_date - timedelta(days=7)  # Default to weekly
    
    def _analyze_category_performance(self, tasks: List[TaskAnalytics]) -> Dict[str, Dict[str, Any]]:
        """Analyze performance by task category."""
        category_stats = defaultdict(lambda: {
            'total': 0,
            'completed': 0,
            'avg_completion_time': 0,
            'completion_rate': 0
        })
        
        for task in tasks:
            category = task.category
            category_stats[category]['total'] += 1
            
            if task.completed_at:
                category_stats[category]['completed'] += 1
            
            if task.time_to_complete:
                current_avg = category_stats[category]['avg_completion_time']
                current_count = category_stats[category]['completed']
                if current_count > 0:
                    category_stats[category]['avg_completion_time'] = (
                        (current_avg * (current_count - 1) + task.time_to_complete) / current_count
                    )
                else:
                    category_stats[category]['avg_completion_time'] = task.time_to_complete
        
        # Calculate completion rates
        for category, stats in category_stats.items():
            if stats['total'] > 0:
                stats['completion_rate'] = (stats['completed'] / stats['total']) * 100
        
        return dict(category_stats)
    
    def _analyze_time_patterns(self, tasks: List[TaskAnalytics]) -> Dict[str, Any]:
        """Analyze time-based patterns in task completion."""
        completion_hours = []
        creation_hours = []
        
        for task in tasks:
            creation_hours.append(task.created_at.hour)
            if task.completed_at:
                completion_hours.append(task.completed_at.hour)
        
        return {
            'most_productive_hour': statistics.mode(completion_hours) if completion_hours else None,
            'most_active_creation_hour': statistics.mode(creation_hours) if creation_hours else None,
            'completion_hour_distribution': Counter(completion_hours),
            'creation_hour_distribution': Counter(creation_hours)
        }
    
    def _calculate_focus_score(self, tasks: List[TaskAnalytics]) -> float:
        """Calculate a focus score based on task completion patterns."""
        if not tasks:
            return 0.0
        
        # Factors that contribute to focus score
        completed_tasks = [t for t in tasks if t.completed_at]
        if not completed_tasks:
            return 0.0
        
        # Higher score for better completion rate
        completion_rate = len(completed_tasks) / len(tasks)
        
        # Higher score for fewer overdue tasks
        overdue_penalty = len([t for t in tasks if t.was_overdue]) / len(tasks)
        
        # Higher score for consistent completion times
        completion_times = [t.time_to_complete for t in completed_tasks if t.time_to_complete]
        consistency_score = 1.0
        if len(completion_times) > 1:
            time_variance = statistics.stdev(completion_times) / statistics.mean(completion_times)
            consistency_score = max(0, 1 - time_variance)
        
        # Calculate final focus score
        focus_score = (completion_rate * 0.4 + 
                      (1 - overdue_penalty) * 0.3 + 
                      consistency_score * 0.3) * 100
        
        return min(100.0, max(0.0, focus_score))
    
    def _analyze_productivity_trend(self, timeframe: AnalyticsTimeframe, end_date: datetime) -> str:
        """Analyze productivity trend by comparing with previous period."""
        current_stats = self.generate_productivity_stats(timeframe, end_date)
        
        # Get previous period
        period_delta = self._get_period_delta(timeframe)
        previous_end = end_date - period_delta
        previous_stats = self.generate_productivity_stats(timeframe, previous_end)
        
        if previous_stats.total_tasks == 0:
            return "stable"
        
        # Compare completion rates
        rate_change = current_stats.completion_rate - previous_stats.completion_rate
        
        if rate_change > 5:
            return "improving"
        elif rate_change < -5:
            return "declining"
        else:
            return "stable"
    
    def _get_period_delta(self, timeframe: AnalyticsTimeframe) -> timedelta:
        """Get timedelta for the specified timeframe."""
        if timeframe == AnalyticsTimeframe.DAILY:
            return timedelta(days=1)
        elif timeframe == AnalyticsTimeframe.WEEKLY:
            return timedelta(days=7)
        elif timeframe == AnalyticsTimeframe.MONTHLY:
            return timedelta(days=30)
        elif timeframe == AnalyticsTimeframe.QUARTERLY:
            return timedelta(days=90)
        elif timeframe == AnalyticsTimeframe.YEARLY:
            return timedelta(days=365)
        else:
            return timedelta(days=7)
    
    def _generate_insights(self, tasks: List[TaskAnalytics], completion_rate: float, 
                          avg_completion_time: float) -> List[str]:
        """Generate actionable insights based on the data."""
        insights = []
        
        if completion_rate < 70:
            insights.append("Your task completion rate is below 70%. Consider breaking down large tasks into smaller, more manageable pieces.")
        
        if completion_rate > 90:
            insights.append("Excellent completion rate! You're staying on top of your tasks well.")
        
        overdue_count = len([t for t in tasks if t.was_overdue])
        if overdue_count > len(tasks) * 0.2:  # More than 20% overdue
            insights.append("You have a high rate of overdue tasks. Consider adjusting your deadline estimates or workload.")
        
        high_priority_tasks = [t for t in tasks if t.priority == TaskPriority.HIGH]
        if high_priority_tasks:
            high_priority_completion = len([t for t in high_priority_tasks if t.completed_at]) / len(high_priority_tasks)
            if high_priority_completion < 0.8:
                insights.append("Focus on completing high-priority tasks first to improve overall productivity.")
        
        if avg_completion_time > 0:
            quick_tasks = [t for t in tasks if t.time_to_complete and t.time_to_complete < 1]  # Less than 1 hour
            if len(quick_tasks) > len(tasks) * 0.3:  # More than 30% are quick tasks
                insights.append("You have many quick tasks. Consider batching similar small tasks together for better efficiency.")
        
        return insights
    
    def get_task_recommendations(self, current_tasks: List[Task]) -> List[str]:
        """
        Get recommendations for current tasks based on historical data.
        
        Args:
            current_tasks: List of current pending tasks
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        if not self.task_history:
            return ["Start tracking your task completion to get personalized recommendations!"]
        
        # Analyze patterns for recommendations
        completed_tasks = [t for t in self.task_history if t.completed_at]
        
        if completed_tasks:
            # Category-based recommendations
            category_performance = self._analyze_category_performance(self.task_history)
            best_category = max(category_performance.items(), key=lambda x: x[1]['completion_rate'])
            
            recommendations.append(f"You perform best with {best_category[0]} tasks. Consider tackling those first.")
            
            # Time-based recommendations
            time_patterns = self._analyze_time_patterns(self.task_history)
            if time_patterns['most_productive_hour']:
                recommendations.append(
                    f"You're most productive around {time_patterns['most_productive_hour']}:00. "
                    "Schedule important tasks during this time."
                )
            
            # Priority-based recommendations
            for task in current_tasks:
                if task.priority == TaskPriority.HIGH and task.due_date:
                    days_until_due = (task.due_date - datetime.now()).days
                    if days_until_due <= 1:
                        recommendations.append(f"High priority task '{task.title}' is due soon. Consider prioritizing it.")
        
        return recommendations or ["Keep up the good work! Track more tasks to get better recommendations."]
    
    def export_analytics_report(self, timeframe: AnalyticsTimeframe, 
                              format: str = "json") -> Dict[str, Any]:
        """
        Export a comprehensive analytics report.
        
        Args:
            timeframe: Time period for the report
            format: Export format (json, csv, etc.)
            
        Returns:
            Report data
        """
        stats = self.generate_productivity_stats(timeframe)
        
        report = {
            'report_generated': datetime.now().isoformat(),
            'timeframe': timeframe.value,
            'period': {
                'start': stats.start_date.isoformat(),
                'end': stats.end_date.isoformat()
            },
            'summary': {
                'total_tasks': stats.total_tasks,
                'completed_tasks': stats.completed_tasks,
                'completion_rate': stats.completion_rate,
                'average_completion_time_hours': stats.average_completion_time,
                'tasks_per_day': stats.tasks_per_day,
                'focus_score': stats.focus_score,
                'productivity_trend': stats.productivity_trend
            },
            'detailed_metrics': {
                'priority_distribution': stats.priority_distribution,
                'category_performance': stats.category_performance,
                'time_patterns': stats.time_patterns
            },
            'insights': stats.insights,
            'recommendations': self.get_task_recommendations([])
        }
        
        return report
