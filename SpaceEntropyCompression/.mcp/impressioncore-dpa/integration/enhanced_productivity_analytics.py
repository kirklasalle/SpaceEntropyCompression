#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_dpa\integration\enhanced_productivity_analytics.py #memory_management #python #source_code  
**Category:** Source Code  
**Status:** Active
"""









# Enhanced Productivity Analytics

**Created:** 2024-10-15  
**Updated:** 2025-07-26 10:26:57  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_dpa\integration\enhanced_productivity_analytics.py #memory_management #python #source_code  
**Category:** Source Code  
**Status:** Active

"""
Enhanced Productivity Analytics Dashboard for ImpressionCore Personal Assistant

This module provides real-time productivity insights, goal tracking, and performance
optimization recommendations optimized for GTX 1050 Ti hardware constraints.

Phase 8B Enhancement Features:
- Real-time productivity metrics calculation
- Advanced goal tracking with prediction algorithms
- Trend analysis and pattern recognition
- AI-powered productivity recommendations
- Rich dashboard visualization
- Memory-optimized data processing

Created: 2025-06-07
Author: GitHub Copilot
Version: 2.0 (Phase 8B Enhancement)
"""

import json
import logging
import time
from datetime import datetime, timedelta, date
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from collections import defaultdict, deque
from pathlib import Path
import statistics
import math

# Core utilities and rich enhancements
from src.core.utils.rich_enhancements import create_panel, create_table, RichEnhancer
from src.core.utils.rich_logging import get_rich_logger
from src.core.utils.rich_status_animation import StatusAnimation

# Memory management for GTX 1050 Ti optimization
import psutil
import gc


@dataclass
class ProductivityMetric:
    """Individual productivity metric data"""
    name: str
    value: float
    unit: str
    trend: str  # 'up', 'down', 'stable'
    change_percent: float
    target: Optional[float] = None
    category: str = "general"
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class GoalProgress:
    """Goal tracking and progress data"""
    goal_id: str
    title: str
    description: str
    target_value: float
    current_value: float
    unit: str
    due_date: datetime
    category: str
    priority: str  # 'high', 'medium', 'low'
    completion_prediction: Optional[datetime] = None
    confidence_score: float = 0.0
    milestones: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ProductivityInsight:
    """AI-generated productivity insight"""
    insight_id: str
    type: str  # 'recommendation', 'warning', 'achievement', 'trend'
    title: str
    description: str
    impact_score: float  # 0.0 to 1.0
    actionable_steps: List[str]
    category: str
    timestamp: datetime = field(default_factory=datetime.now)


class EnhancedProductivityAnalytics:
    """
    Enhanced productivity analytics with AI-powered insights and predictions
    optimized for GTX 1050 Ti hardware constraints.
    """
    
    def __init__(self, 
                 user_id: str,
                 data_path: Optional[str] = None,
                 memory_limit_mb: int = 100):
        """Initialize enhanced productivity analytics"""
        self.logger = get_rich_logger(__name__)
        self.user_id = user_id
        self.memory_limit_mb = memory_limit_mb
        
        # Storage paths
        self.data_path = Path(data_path or f"src/user_data/analytics/{user_id}")
        self.data_path.mkdir(parents=True, exist_ok=True)
        
        # Analytics data
        self._metrics_history: deque = deque(maxlen=1000)  # Memory optimization
        self._goals: Dict[str, GoalProgress] = {}
        self._insights: deque = deque(maxlen=50)  # Keep recent insights
        self._daily_summaries: Dict[str, Dict[str, Any]] = {}
        
        # Real-time tracking
        self._session_start = datetime.now()
        self._current_session_data = defaultdict(list)
        
        # Prediction models (lightweight for GTX 1050 Ti)
        self._trend_analysis = TrendAnalyzer(memory_limit_mb=25)
        self._goal_predictor = GoalPredictor(memory_limit_mb=25)
        
        # Rich UI enhancer
        self.rich_enhancer = RichEnhancer()
        
        # Load existing data
        self._load_analytics_data()
        
        self.logger.info("Enhanced Productivity Analytics initialized", extra={
            "user_id": user_id,
            "memory_limit": f"{memory_limit_mb}MB",
            "metrics_loaded": len(self._metrics_history),
            "goals_loaded": len(self._goals)
        })
    
    def track_task_completion(self, 
                            task_id: str,
                            task_title: str,
                            completion_time: datetime,
                            estimated_duration: int,
                            actual_duration: int,
                            difficulty_rating: float = 5.0) -> None:
        """Track task completion for analytics"""
        animation = StatusAnimation(
            total_steps=4,
            description="Tracking task completion"
        )
        
        try:
            animation.start()
            
            # Step 1: Calculate efficiency metrics
            animation.update(1, "Calculating efficiency")
            efficiency = estimated_duration / actual_duration if actual_duration > 0 else 1.0
            
            # Step 2: Update metrics
            animation.update(2, "Updating metrics")
            self._record_metric("task_completion_rate", 1.0, "tasks/hour")
            self._record_metric("time_estimation_accuracy", efficiency, "ratio")
            self._record_metric("difficulty_handled", difficulty_rating, "points")
            
            # Step 3: Update session data
            animation.update(3, "Updating session data")
            self._current_session_data['completed_tasks'].append({
                'task_id': task_id,
                'title': task_title,
                'completion_time': completion_time.isoformat(),
                'estimated_duration': estimated_duration,
                'actual_duration': actual_duration,
                'efficiency': efficiency,
                'difficulty': difficulty_rating
            })
            
            # Step 4: Generate insights
            animation.update(4, "Generating insights")
            self._generate_completion_insights(efficiency, difficulty_rating)
            
            animation.complete("Task completion tracked successfully")
            
        except Exception as e:
            animation.error(f"Error tracking task completion: {e}")
            self.logger.error(f"Task completion tracking failed: {e}")
    
    def get_real_time_dashboard(self) -> Dict[str, Any]:
        """Generate real-time productivity dashboard data"""
        animation = StatusAnimation(
            total_steps=6,
            description="Generating dashboard"
        )
        
        try:
            animation.start()
            
            # Step 1: Calculate current metrics
            animation.update(1, "Calculating metrics")
            current_metrics = self._calculate_current_metrics()
            
            # Step 2: Analyze trends
            animation.update(2, "Analyzing trends")
            trends = self._trend_analysis.analyze_recent_trends(self._metrics_history)
            
            # Step 3: Update goal progress
            animation.update(3, "Updating goals")
            goals_status = self._update_goal_progress()
            
            # Step 4: Generate recommendations
            animation.update(4, "Generating recommendations")
            recommendations = self._generate_recommendations()
            
            # Step 5: Create visualizations
            animation.update(5, "Creating visualizations")
            charts = self._create_dashboard_charts()
            
            # Step 6: Compile dashboard
            animation.update(6, "Compiling dashboard")
            dashboard = {
                'timestamp': datetime.now().isoformat(),
                'session_duration': self._get_session_duration(),
                'metrics': current_metrics,
                'trends': trends,
                'goals': goals_status,
                'recommendations': recommendations,
                'charts': charts,
                'insights': list(self._insights)[-5:],  # Recent insights
                'performance_score': self._calculate_performance_score()
            }
            
            animation.complete("Dashboard generated successfully")
            return dashboard
            
        except Exception as e:
            animation.error(f"Dashboard generation failed: {e}")
            self.logger.error(f"Dashboard generation error: {e}")
            return self._get_fallback_dashboard()
    
    def create_goal(self,
                   title: str,
                   description: str,
                   target_value: float,
                   unit: str,
                   due_date: datetime,
                   category: str = "productivity",
                   priority: str = "medium") -> str:
        """Create a new productivity goal"""
        goal_id = f"goal_{int(time.time())}_{hash(title) % 10000}"
        
        goal = GoalProgress(
            goal_id=goal_id,
            title=title,
            description=description,
            target_value=target_value,
            current_value=0.0,
            unit=unit,
            due_date=due_date,
            category=category,
            priority=priority
        )
        
        self._goals[goal_id] = goal
        self._save_analytics_data()
        
        # Generate prediction
        prediction = self._goal_predictor.predict_completion(goal, self._metrics_history)
        goal.completion_prediction = prediction.get('predicted_date')
        goal.confidence_score = prediction.get('confidence', 0.0)
        
        self.logger.info(f"Goal created: {title}", extra={
            "goal_id": goal_id,
            "target": f"{target_value} {unit}",
            "due_date": due_date.strftime("%Y-%m-%d")
        })
        
        return goal_id
    
    def _calculate_current_metrics(self) -> List[ProductivityMetric]:
        """Calculate current productivity metrics"""
        metrics = []
        
        # Tasks completed today
        today_tasks = [
            task for task in self._current_session_data.get('completed_tasks', [])
            if datetime.fromisoformat(task['completion_time']).date() == date.today()
        ]
        
        metrics.append(ProductivityMetric(
            name="Tasks Completed Today",
            value=len(today_tasks),
            unit="tasks",
            trend=self._calculate_trend("daily_tasks"),
            change_percent=self._calculate_change_percent("daily_tasks"),
            category="completion"
        ))
        
        # Average efficiency
        if today_tasks:
            avg_efficiency = statistics.mean([task['efficiency'] for task in today_tasks])
            metrics.append(ProductivityMetric(
                name="Time Estimation Accuracy",
                value=avg_efficiency,
                unit="ratio",
                trend=self._calculate_trend("efficiency"),
                change_percent=self._calculate_change_percent("efficiency"),
                category="efficiency"
            ))
        
        # Focus time
        session_duration = self._get_session_duration()
        metrics.append(ProductivityMetric(
            name="Focus Time Today",
            value=session_duration,
            unit="minutes",
            trend=self._calculate_trend("focus_time"),
            change_percent=self._calculate_change_percent("focus_time"),
            category="focus"
        ))
        
        return metrics
    
    def _generate_recommendations(self) -> List[ProductivityInsight]:
        """Generate AI-powered productivity recommendations"""
        recommendations = []
        
        # Analyze recent patterns
        recent_metrics = list(self._metrics_history)[-20:] if self._metrics_history else []
        
        if recent_metrics:
            # Efficiency recommendation
            efficiency_values = [
                m.value for m in recent_metrics 
                if m.name == "Time Estimation Accuracy"
            ]
            
            if efficiency_values and statistics.mean(efficiency_values) < 0.8:
                recommendations.append(ProductivityInsight(
                    insight_id=f"rec_{int(time.time())}_efficiency",
                    type="recommendation",
                    title="Improve Time Estimation",
                    description="Your time estimates have been consistently optimistic. Consider adding buffer time.",
                    impact_score=0.7,
                    actionable_steps=[
                        "Add 20% buffer time to task estimates",
                        "Review completed tasks to calibrate estimates",
                        "Use time tracking for better accuracy"
                    ],
                    category="efficiency"
                ))
        
        # Goal progress recommendations
        for goal in self._goals.values():
            if goal.completion_prediction and goal.completion_prediction > goal.due_date:
                recommendations.append(ProductivityInsight(
                    insight_id=f"rec_{int(time.time())}_goal_{goal.goal_id}",
                    type="warning",
                    title=f"Goal '{goal.title}' at Risk",
                    description=f"Current progress suggests completion after due date.",
                    impact_score=0.8,
                    actionable_steps=[
                        "Increase daily effort allocation",
                        "Break goal into smaller milestones",
                        "Consider extending deadline if appropriate"
                    ],
                    category="goals"
                ))
        
        return recommendations
    
    def _create_dashboard_charts(self) -> Dict[str, Any]:
        """Create chart data for dashboard visualization"""
        charts = {}
        
        # Completion trend chart
        daily_completions = self._get_daily_completion_trend()
        charts['completion_trend'] = {
            'type': 'line',
            'title': 'Daily Task Completion Trend',
            'data': daily_completions,
            'color': '#4ade80'
        }
        
        # Efficiency distribution
        efficiency_data = self._get_efficiency_distribution()
        charts['efficiency_distribution'] = {
            'type': 'histogram',
            'title': 'Time Estimation Accuracy Distribution',
            'data': efficiency_data,
            'color': '#3b82f6'
        }
        
        # Goal progress
        goal_progress_data = self._get_goal_progress_chart_data()
        charts['goal_progress'] = {
            'type': 'progress',
            'title': 'Goal Progress Overview',
            'data': goal_progress_data,
            'color': '#8b5cf6'
        }
        
        return charts
    
    def _record_metric(self, name: str, value: float, unit: str, category: str = "general") -> None:
        """Record a productivity metric"""
        metric = ProductivityMetric(
            name=name,
            value=value,
            unit=unit,
            trend=self._calculate_trend(name),
            change_percent=self._calculate_change_percent(name),
            category=category
        )
        
        self._metrics_history.append(metric)
        
        # Memory management
        if len(self._metrics_history) > 1000:
            # Remove oldest 100 entries to maintain memory limit
            for _ in range(100):
                self._metrics_history.popleft()
            gc.collect()
    
    def _calculate_performance_score(self) -> float:
        """Calculate overall performance score (0-100)"""
        if not self._metrics_history:
            return 50.0
        
        # Get recent metrics
        recent_metrics = list(self._metrics_history)[-10:]
        
        # Calculate weighted scores
        completion_score = min(len([m for m in recent_metrics if m.name == "task_completion_rate"]) * 10, 30)
        efficiency_score = min(statistics.mean([
            m.value for m in recent_metrics 
            if m.name == "Time Estimation Accuracy"
        ]) * 25, 25) if any(m.name == "Time Estimation Accuracy" for m in recent_metrics) else 15
        
        goal_score = min(len([g for g in self._goals.values() if g.current_value / g.target_value > 0.5]) * 15, 30)
        consistency_score = min(len(recent_metrics), 15)
        
        return completion_score + efficiency_score + goal_score + consistency_score
    
    def _get_session_duration(self) -> int:
        """Get current session duration in minutes"""
        duration = datetime.now() - self._session_start
        return int(duration.total_seconds() / 60)
    
    def _calculate_trend(self, metric_name: str) -> str:
        """Calculate trend for a metric"""
        recent_values = [
            m.value for m in list(self._metrics_history)[-10:]
            if m.name == metric_name
        ]
        
        if len(recent_values) < 2:
            return "stable"
        
        recent_avg = statistics.mean(recent_values[-3:]) if len(recent_values) >= 3 else recent_values[-1]
        older_avg = statistics.mean(recent_values[:-3]) if len(recent_values) >= 6 else recent_values[0]
        
        change = (recent_avg - older_avg) / older_avg if older_avg != 0 else 0
        
        if change > 0.05:
            return "up"
        elif change < -0.05:
            return "down"
        return "stable"
    
    def _calculate_change_percent(self, metric_name: str) -> float:
        """Calculate percentage change for a metric"""
        recent_values = [
            m.value for m in list(self._metrics_history)[-10:]
            if m.name == metric_name
        ]
        
        if len(recent_values) < 2:
            return 0.0
        
        if len(recent_values) >= 6:
            recent_avg = statistics.mean(recent_values[-3:])
            older_avg = statistics.mean(recent_values[:-3])
        else:
            recent_avg = recent_values[-1]
            older_avg = recent_values[0]
        
        if older_avg == 0:
            return 0.0
        
        return ((recent_avg - older_avg) / older_avg) * 100
    
    def _update_goal_progress(self) -> List[Dict[str, Any]]:
        """Update and return goal progress status"""
        goals_status = []
        
        for goal in self._goals.values():
            # Update current value based on related metrics
            self._update_goal_current_value(goal)
            
            # Calculate progress percentage
            progress_percent = min((goal.current_value / goal.target_value) * 100, 100) if goal.target_value > 0 else 0
            
            # Calculate days remaining
            days_remaining = (goal.due_date - datetime.now()).days
            
            goals_status.append({
                'goal_id': goal.goal_id,
                'title': goal.title,
                'progress_percent': progress_percent,
                'current_value': goal.current_value,
                'target_value': goal.target_value,
                'unit': goal.unit,
                'days_remaining': days_remaining,
                'status': self._get_goal_status(goal),
                'prediction': goal.completion_prediction.isoformat() if goal.completion_prediction else None,
                'confidence': goal.confidence_score
            })
        
        return goals_status
    
    def _get_goal_status(self, goal: GoalProgress) -> str:
        """Determine goal status"""
        progress_ratio = goal.current_value / goal.target_value if goal.target_value > 0 else 0
        days_remaining = (goal.due_date - datetime.now()).days
        
        if progress_ratio >= 1.0:
            return "completed"
        elif days_remaining < 0:
            return "overdue"
        elif progress_ratio >= 0.8:
            return "on_track"
        elif days_remaining <= 7 and progress_ratio < 0.5:
            return "at_risk"
        else:
            return "in_progress"
    
    def _load_analytics_data(self) -> None:
        """Load analytics data from storage"""
        try:
            # Load metrics history
            metrics_file = self.data_path / "metrics_history.json"
            if metrics_file.exists():
                with open(metrics_file, 'r') as f:
                    metrics_data = json.load(f)
                    for metric_dict in metrics_data[-1000:]:  # Memory optimization
                        metric = ProductivityMetric(**metric_dict)
                        self._metrics_history.append(metric)
            
            # Load goals
            goals_file = self.data_path / "goals.json"
            if goals_file.exists():
                with open(goals_file, 'r') as f:
                    goals_data = json.load(f)
                    for goal_id, goal_dict in goals_data.items():
                        # Convert datetime strings back to datetime objects
                        goal_dict['due_date'] = datetime.fromisoformat(goal_dict['due_date'])
                        if goal_dict.get('completion_prediction'):
                            goal_dict['completion_prediction'] = datetime.fromisoformat(goal_dict['completion_prediction'])
                        
                        self._goals[goal_id] = GoalProgress(**goal_dict)
            
            self.logger.info("Analytics data loaded successfully")
            
        except Exception as e:
            self.logger.warning(f"Could not load analytics data: {e}")
    
    def _save_analytics_data(self) -> None:
        """Save analytics data to storage"""
        try:
            # Save metrics history
            metrics_file = self.data_path / "metrics_history.json"
            metrics_data = [asdict(metric) for metric in list(self._metrics_history)]
            with open(metrics_file, 'w') as f:
                json.dump(metrics_data, f, default=str)
            
            # Save goals
            goals_file = self.data_path / "goals.json"
            goals_data = {}
            for goal_id, goal in self._goals.items():
                goal_dict = asdict(goal)
                # Convert datetime objects to strings for JSON serialization
                goal_dict['due_date'] = goal.due_date.isoformat()
                if goal.completion_prediction:
                    goal_dict['completion_prediction'] = goal.completion_prediction.isoformat()
                goals_data[goal_id] = goal_dict
            
            with open(goals_file, 'w') as f:
                json.dump(goals_data, f, indent=2)
            
        except Exception as e:
            self.logger.error(f"Failed to save analytics data: {e}")
    
    def _get_fallback_dashboard(self) -> Dict[str, Any]:
        """Return fallback dashboard when generation fails"""
        return {
            'timestamp': datetime.now().isoformat(),
            'error': 'Dashboard generation failed',
            'metrics': [],
            'trends': {},
            'goals': [],
            'recommendations': [],
            'charts': {},
            'insights': [],
            'performance_score': 50.0
        }


class TrendAnalyzer:
    """Lightweight trend analysis for productivity metrics"""
    
    def __init__(self, memory_limit_mb: int = 25):
        self.memory_limit_mb = memory_limit_mb
        self.logger = get_rich_logger(f"{__name__}.TrendAnalyzer")
    
    def analyze_recent_trends(self, metrics_history: deque) -> Dict[str, Any]:
        """Analyze recent trends in productivity metrics"""
        if not metrics_history:
            return {}
        
        recent_metrics = list(metrics_history)[-50:]  # Memory optimization
        
        trends = {}
        metric_groups = defaultdict(list)
        
        # Group metrics by name
        for metric in recent_metrics:
            metric_groups[metric.name].append(metric.value)
        
        # Analyze each metric group
        for metric_name, values in metric_groups.items():
            if len(values) >= 3:
                trends[metric_name] = self._calculate_trend_stats(values)
        
        return trends
    
    def _calculate_trend_stats(self, values: List[float]) -> Dict[str, Any]:
        """Calculate trend statistics for a metric"""
        if len(values) < 2:
            return {'direction': 'stable', 'strength': 0.0}
        
        # Simple linear regression slope
        n = len(values)
        x_mean = (n - 1) / 2
        y_mean = statistics.mean(values)
        
        numerator = sum((i - x_mean) * (y - y_mean) for i, y in enumerate(values))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        
        slope = numerator / denominator if denominator != 0 else 0
        
        # Determine trend direction and strength
        if abs(slope) < 0.01:
            direction = 'stable'
            strength = 0.0
        elif slope > 0:
            direction = 'increasing'
            strength = min(abs(slope) * 10, 1.0)
        else:
            direction = 'decreasing'
            strength = min(abs(slope) * 10, 1.0)
        
        return {
            'direction': direction,
            'strength': strength,
            'slope': slope,
            'recent_average': statistics.mean(values[-5:]) if len(values) >= 5 else values[-1]
        }


class GoalPredictor:
    """Lightweight goal completion prediction"""
    
    def __init__(self, memory_limit_mb: int = 25):
        self.memory_limit_mb = memory_limit_mb
        self.logger = get_rich_logger(f"{__name__}.GoalPredictor")
    
    def predict_completion(self, 
                         goal: GoalProgress, 
                         metrics_history: deque) -> Dict[str, Any]:
        """Predict goal completion date and confidence"""
        if goal.current_value >= goal.target_value:
            return {
                'predicted_date': datetime.now(),
                'confidence': 1.0,
                'status': 'completed'
            }
        
        # Calculate progress rate from recent activity
        progress_rate = self._estimate_progress_rate(goal, metrics_history)
        
        if progress_rate <= 0:
            return {
                'predicted_date': None,
                'confidence': 0.0,
                'status': 'stalled'
            }
        
        # Calculate remaining work and time needed
        remaining_work = goal.target_value - goal.current_value
        days_needed = remaining_work / progress_rate
        
        predicted_date = datetime.now() + timedelta(days=days_needed)
        
        # Calculate confidence based on consistency
        confidence = self._calculate_prediction_confidence(goal, metrics_history, progress_rate)
        
        return {
            'predicted_date': predicted_date,
            'confidence': confidence,
            'status': 'on_track' if predicted_date <= goal.due_date else 'at_risk',
            'progress_rate': progress_rate
        }
    
    def _estimate_progress_rate(self, goal: GoalProgress, metrics_history: deque) -> float:
        """Estimate daily progress rate for a goal"""
        # Simple heuristic: use task completion rate as proxy
        recent_completions = [
            m.value for m in list(metrics_history)[-14:]  # Last 2 weeks
            if m.name == "task_completion_rate"
        ]
        
        if not recent_completions:
            return 0.0
        
        # Assume each task contributes to goals proportionally
        avg_daily_tasks = statistics.mean(recent_completions)
        
        # Estimate contribution per task (this would be more sophisticated in practice)
        estimated_contribution_per_task = goal.target_value / 50  # Assume 50 tasks needed
        
        return avg_daily_tasks * estimated_contribution_per_task
    
    def _calculate_prediction_confidence(self, 
                                       goal: GoalProgress, 
                                       metrics_history: deque, 
                                       progress_rate: float) -> float:
        """Calculate confidence in the prediction"""
        # Factors affecting confidence:
        # 1. Consistency of recent progress
        # 2. Amount of historical data
        # 3. Time remaining vs. predicted time
        
        recent_values = [
            m.value for m in list(metrics_history)[-10:]
            if m.name == "task_completion_rate"
        ]
        
        if len(recent_values) < 3:
            return 0.3  # Low confidence with little data
        
        # Consistency score (low variance = high confidence)
        variance = statistics.variance(recent_values) if len(recent_values) > 1 else 1.0
        consistency_score = max(0.0, 1.0 - variance)
        
        # Data amount score
        data_score = min(len(recent_values) / 10, 1.0)
        
        # Time buffer score (more time = higher confidence)
        days_remaining = (goal.due_date - datetime.now()).days
        time_score = min(days_remaining / 30, 1.0) if days_remaining > 0 else 0.0
        
        # Weighted average
        confidence = (consistency_score * 0.5 + data_score * 0.3 + time_score * 0.2)
        
        return max(0.1, min(confidence, 0.95))  # Keep within reasonable bounds
