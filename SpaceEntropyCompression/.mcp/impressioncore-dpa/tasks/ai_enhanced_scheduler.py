#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_dpa\tasks\ai_enhanced_scheduler.py #memory_management #python #source_code  
**Category:** Source Code  
**Status:** Active
"""









# Ai Enhanced Scheduler

**Created:** 2024-10-15  
**Updated:** 2025-07-26 10:26:57  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_dpa\tasks\ai_enhanced_scheduler.py #memory_management #python #source_code  
**Category:** Source Code  
**Status:** Active

"""
AI-Enhanced Task Scheduler for ImpressionCore Personal Assistant

This module provides intelligent task scheduling with AI-powered priority adjustment,
context-aware deadline management, and adaptive resource allocation optimized for GTX 1050 Ti.

Phase 8B Enhancement Features:
- AI-powered dynamic priority adjustment
- Context-aware smart scheduling
- Predictive deadline management
- Energy-based task allocation
- Conflict resolution with machine learning
- Memory-optimized scheduling algorithms

Created: 2025-06-07
Author: GitHub Copilot
Version: 2.0 (Phase 8B Enhancement)
"""

import logging
import heapq
import threading
import pickle
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import math
import statistics
from collections import defaultdict, deque

# Core imports
from ..tasks.models import Task, TaskPriority, TaskStatus, TaskList
from ...core.utils.rich_logging import get_rich_logger
from ...core.utils.rich_status_animation import StatusAnimation
from ...core.utils.rich_enhancements import create_panel, create_table

# Memory management for GTX 1050 Ti
import psutil
import gc


class AISchedulingStrategy(Enum):
    """AI-enhanced scheduling strategies"""
    ADAPTIVE_PRIORITY = "adaptive_priority"
    CONTEXT_AWARE = "context_aware"
    ENERGY_OPTIMIZED = "energy_optimized"
    DEADLINE_INTELLIGENT = "deadline_intelligent"
    HYBRID_AI = "hybrid_ai"


@dataclass
class TaskContext:
    """Context information for AI-enhanced scheduling"""
    user_energy_level: float = 0.8  # 0.0 to 1.0
    current_focus_area: str = "general"
    interruption_likelihood: float = 0.3  # 0.0 to 1.0
    available_time_blocks: List[int] = field(default_factory=list)  # minutes
    preferred_task_types: List[str] = field(default_factory=list)
    stress_level: float = 0.5  # 0.0 to 1.0
    external_deadlines: List[datetime] = field(default_factory=list)


@dataclass
class SchedulingDecision:
    """AI scheduling decision with reasoning"""
    task_id: str
    scheduled_time: datetime
    estimated_duration: int
    priority_score: float
    reasoning: List[str]
    confidence: float
    alternative_slots: List[Tuple[datetime, float]] = field(default_factory=list)


@dataclass
class AdaptivePriorityWeights:
    """Weights for adaptive priority calculation"""
    deadline_weight: float = 0.3
    importance_weight: float = 0.25
    urgency_weight: float = 0.2
    energy_match_weight: float = 0.15
    context_weight: float = 0.1


class AIEnhancedTaskScheduler:
    """
    AI-enhanced task scheduler with machine learning-based priority adjustment
    and context-aware scheduling optimized for GTX 1050 Ti hardware.
    """
    
    def __init__(self, 
                 user_id: str,
                 strategy: AISchedulingStrategy = AISchedulingStrategy.HYBRID_AI,
                 memory_limit_mb: int = 50):
        """Initialize AI-enhanced task scheduler"""
        self.logger = get_rich_logger(__name__)
        self.user_id = user_id
        self.strategy = strategy
        self.memory_limit_mb = memory_limit_mb
        
        # AI components (lightweight for GTX 1050 Ti)
        self.priority_engine = AdaptivePriorityEngine(memory_limit_mb=15)
        self.context_analyzer = ContextAnalyzer(memory_limit_mb=15)
        self.deadline_predictor = DeadlinePredictor(memory_limit_mb=10)
        self.learning_engine = SchedulingLearningEngine(memory_limit_mb=10)
        
        # Scheduling state
        self._schedule: Dict[str, List[SchedulingDecision]] = defaultdict(list)
        self._task_queue: List[Tuple[float, str, Task]] = []  # Priority queue
        self._context_history: deque = deque(maxlen=100)  # Memory optimization
        self._performance_metrics: Dict[str, float] = {}
        
        # Adaptive weights
        self.priority_weights = AdaptivePriorityWeights()
        
        # Threading for real-time updates
        self._lock = threading.RLock()
        self._background_optimizer = None
        
        # Performance tracking
        self._scheduling_stats = {
            'ai_decisions_made': 0,
            'conflicts_resolved': 0,
            'accuracy_score': 0.0,
            'user_satisfaction': 0.0,
            'schedule_changes': 0
        }
        
        self.logger.info("AI-Enhanced Task Scheduler initialized", extra={
            "user_id": user_id,
            "strategy": strategy.value,
            "memory_limit": f"{memory_limit_mb}MB"
        })
    
    def schedule_task_with_ai(self, 
                            task: Task,
                            context: Optional[TaskContext] = None,
                            force_reschedule: bool = False) -> SchedulingDecision:
        """Schedule a task using AI-enhanced algorithms"""
        animation = StatusAnimation(
            total_steps=7,
            description=f"AI scheduling: {task.title[:30]}..."
        )
        
        try:
            animation.start()
            
            # Step 1: Analyze current context
            animation.update(1, "Analyzing context")
            current_context = context or self._analyze_current_context()
            
            # Step 2: Calculate adaptive priority
            animation.update(2, "Calculating AI priority")
            ai_priority = self.priority_engine.calculate_adaptive_priority(
                task, current_context, self._context_history
            )
            
            # Step 3: Find optimal time slots
            animation.update(3, "Finding optimal slots")
            optimal_slots = self._find_optimal_time_slots(task, current_context, ai_priority)
            
            # Step 4: Resolve conflicts intelligently
            animation.update(4, "Resolving conflicts")
            best_slot = self._resolve_scheduling_conflicts(task, optimal_slots, current_context)
            
            # Step 5: Generate reasoning
            animation.update(5, "Generating reasoning")
            reasoning = self._generate_scheduling_reasoning(task, best_slot, current_context)
            
            # Step 6: Create scheduling decision
            animation.update(6, "Creating decision")
            decision = SchedulingDecision(
                task_id=task.id,
                scheduled_time=best_slot['time'],
                estimated_duration=best_slot['duration'],
                priority_score=ai_priority,
                reasoning=reasoning,
                confidence=best_slot['confidence'],
                alternative_slots=[(slot['time'], slot['confidence']) for slot in optimal_slots[1:3]]
            )
            
            # Step 7: Update schedule and learn
            animation.update(7, "Updating schedule")
            self._add_to_schedule(decision)
            self.learning_engine.record_scheduling_decision(task, decision, current_context)
            
            # Update statistics
            self._scheduling_stats['ai_decisions_made'] += 1
            
            animation.complete(f"Task scheduled: {best_slot['time'].strftime('%H:%M')}")
            return decision
            
        except Exception as e:
            animation.error(f"AI scheduling failed: {e}")
            self.logger.error(f"AI scheduling error for task {task.title}: {e}")
            return self._fallback_scheduling(task)
    
    def optimize_daily_schedule(self, 
                              target_date: datetime,
                              optimization_goals: List[str] = None) -> Dict[str, Any]:
        """Optimize entire daily schedule using AI"""
        animation = StatusAnimation(
            total_steps=5,
            description="Optimizing daily schedule"
        )
        
        try:
            animation.start()
            
            # Step 1: Get current schedule
            animation.update(1, "Analyzing current schedule")
            date_key = target_date.strftime('%Y-%m-%d')
            current_schedule = self._schedule.get(date_key, [])
            
            # Step 2: Analyze optimization opportunities
            animation.update(2, "Finding optimization opportunities")
            optimization_opportunities = self._find_optimization_opportunities(current_schedule)
            
            # Step 3: Apply AI optimizations
            animation.update(3, "Applying AI optimizations")
            optimized_schedule = self._apply_ai_optimizations(
                current_schedule, optimization_opportunities, optimization_goals or []
            )
            
            # Step 4: Validate optimizations
            animation.update(4, "Validating optimizations")
            validation_results = self._validate_schedule_optimizations(
                current_schedule, optimized_schedule
            )
            
            # Step 5: Update schedule if beneficial
            animation.update(5, "Updating schedule")
            if validation_results['improvement_score'] > 0.1:
                self._schedule[date_key] = optimized_schedule
                self._scheduling_stats['schedule_changes'] += 1
                
                result = {
                    'success': True,
                    'improvements': validation_results['improvements'],
                    'optimization_score': validation_results['improvement_score'],
                    'tasks_rescheduled': len(optimization_opportunities),
                    'estimated_time_saved': validation_results['time_saved_minutes']
                }
            else:
                result = {
                    'success': False,
                    'reason': 'No significant improvements found',
                    'current_efficiency': validation_results['current_efficiency']
                }
            
            animation.complete("Schedule optimization complete")
            return result
            
        except Exception as e:
            animation.error(f"Schedule optimization failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_ai_insights(self) -> Dict[str, Any]:
        """Get AI-generated insights about scheduling patterns"""
        insights = {
            'productivity_patterns': self._analyze_productivity_patterns(),
            'optimal_scheduling_times': self._find_optimal_scheduling_times(),
            'improvement_suggestions': self._generate_improvement_suggestions(),
            'performance_metrics': self._scheduling_stats.copy(),
            'priority_weight_effectiveness': self._analyze_priority_weights()
        }
        
        return insights
    
    def adapt_to_user_feedback(self, 
                             decision_id: str,
                             feedback_score: float,
                             feedback_notes: str = "") -> None:
        """Adapt AI based on user feedback"""
        try:
            self.learning_engine.process_user_feedback(decision_id, feedback_score, feedback_notes)
            
            # Update priority weights based on feedback
            if feedback_score < 0.5:
                self._adjust_priority_weights(feedback_notes)
            
            # Update satisfaction metrics
            self._scheduling_stats['user_satisfaction'] = (
                self._scheduling_stats['user_satisfaction'] * 0.9 + feedback_score * 0.1
            )
            
            self.logger.info(f"AI adapted to user feedback", extra={
                "decision_id": decision_id,
                "feedback_score": feedback_score,
                "new_satisfaction": self._scheduling_stats['user_satisfaction']
            })
            
        except Exception as e:
            self.logger.error(f"Failed to adapt to user feedback: {e}")
    
    def _analyze_current_context(self) -> TaskContext:
        """Analyze current context for scheduling decisions"""
        current_hour = datetime.now().hour
        
        # Estimate energy level based on time of day
        if 9 <= current_hour <= 11:
            energy_level = 0.9  # Morning high energy
        elif 11 <= current_hour <= 13:
            energy_level = 0.8  # Pre-lunch good energy
        elif 13 <= current_hour <= 15:
            energy_level = 0.6  # Post-lunch dip
        elif 15 <= current_hour <= 17:
            energy_level = 0.7  # Afternoon recovery
        else:
            energy_level = 0.5  # Evening/night
        
        # Analyze available time blocks
        available_blocks = self._calculate_available_time_blocks()
        
        return TaskContext(
            user_energy_level=energy_level,
            current_focus_area="productivity",
            interruption_likelihood=0.3,
            available_time_blocks=available_blocks,
            stress_level=0.4
        )
    
    def _find_optimal_time_slots(self, 
                               task: Task,
                               context: TaskContext,
                               priority_score: float) -> List[Dict[str, Any]]:
        """Find optimal time slots for a task"""
        optimal_slots = []
        
        # Consider next 7 days
        for day_offset in range(7):
            target_date = datetime.now().date() + timedelta(days=day_offset)
            
            # Get available slots for this day
            day_slots = self._get_available_slots_for_day(target_date, task.estimated_duration)
            
            for slot_time, duration in day_slots:
                # Calculate slot quality score
                quality_score = self._calculate_slot_quality(
                    slot_time, task, context, priority_score
                )
                
                optimal_slots.append({
                    'time': slot_time,
                    'duration': duration,
                    'quality_score': quality_score,
                    'confidence': min(quality_score, 0.95)
                })
        
        # Sort by quality score and return top options
        optimal_slots.sort(key=lambda x: x['quality_score'], reverse=True)
        return optimal_slots[:5]  # Return top 5 options
    
    def _calculate_slot_quality(self, 
                              slot_time: datetime,
                              task: Task,
                              context: TaskContext,
                              priority_score: float) -> float:
        """Calculate quality score for a time slot"""
        quality_score = 0.0
        
        # Time of day preference
        hour = slot_time.hour
        if task.category == "creative" and 9 <= hour <= 11:
            quality_score += 0.3  # Creative work in morning
        elif task.category == "administrative" and 13 <= hour <= 16:
            quality_score += 0.2  # Admin work in afternoon
        
        # Energy level alignment
        estimated_energy = self._estimate_energy_at_time(slot_time)
        energy_match = 1.0 - abs(estimated_energy - task.difficulty * 0.1)
        quality_score += energy_match * 0.25
        
        # Deadline proximity
        if task.due_date:
            days_to_deadline = (task.due_date - slot_time).days
            if days_to_deadline <= 1:
                quality_score += 0.4  # High urgency
            elif days_to_deadline <= 3:
                quality_score += 0.2  # Medium urgency
        
        # Priority alignment
        quality_score += priority_score * 0.2
        
        # Conflict penalty
        existing_tasks = self._get_conflicting_tasks(slot_time, task.estimated_duration)
        if existing_tasks:
            quality_score -= len(existing_tasks) * 0.1
        
        return max(0.0, min(quality_score, 1.0))
    
    def _resolve_scheduling_conflicts(self, 
                                   task: Task,
                                   optimal_slots: List[Dict[str, Any]],
                                   context: TaskContext) -> Dict[str, Any]:
        """Intelligently resolve scheduling conflicts"""
        for slot in optimal_slots:
            conflicting_tasks = self._get_conflicting_tasks(
                slot['time'], slot['duration']
            )
            
            if not conflicting_tasks:
                return slot
            
            # Try to resolve conflicts
            resolution_success = self._attempt_conflict_resolution(
                task, slot, conflicting_tasks, context
            )
            
            if resolution_success:
                self._scheduling_stats['conflicts_resolved'] += 1
                return slot
        
        # Fallback to least conflicted slot
        return optimal_slots[0] if optimal_slots else {
            'time': datetime.now() + timedelta(hours=1),
            'duration': task.estimated_duration,
            'quality_score': 0.3,
            'confidence': 0.3
        }
    
    def _generate_scheduling_reasoning(self, 
                                     task: Task,
                                     selected_slot: Dict[str, Any],
                                     context: TaskContext) -> List[str]:
        """Generate human-readable reasoning for scheduling decision"""
        reasoning = []
        
        # Time selection reasoning
        hour = selected_slot['time'].hour
        if 9 <= hour <= 11:
            reasoning.append("Scheduled during peak morning energy hours")
        elif hour >= 17:
            reasoning.append("Placed in evening due to lower priority")
        
        # Priority reasoning
        if selected_slot['quality_score'] > 0.7:
            reasoning.append("High-quality time slot matching task requirements")
        
        # Deadline reasoning
        if task.due_date:
            days_remaining = (task.due_date - selected_slot['time']).days
            if days_remaining <= 1:
                reasoning.append("Urgent scheduling due to approaching deadline")
            elif days_remaining <= 3:
                reasoning.append("Prioritized due to near-term deadline")
        
        # Context reasoning
        if context.user_energy_level > 0.8:
            reasoning.append("Leveraging current high energy level")
        
        if not reasoning:
            reasoning.append("Optimal available slot based on current schedule")
        
        return reasoning
    
    def _add_to_schedule(self, decision: SchedulingDecision) -> None:
        """Add scheduling decision to the schedule"""
        date_key = decision.scheduled_time.strftime('%Y-%m-%d')
        
        with self._lock:
            self._schedule[date_key].append(decision)
            # Sort by scheduled time
            self._schedule[date_key].sort(key=lambda d: d.scheduled_time)
    
    def _fallback_scheduling(self, task: Task) -> SchedulingDecision:
        """Fallback scheduling when AI fails"""
        fallback_time = datetime.now() + timedelta(hours=2)
        
        return SchedulingDecision(
            task_id=task.id,
            scheduled_time=fallback_time,
            estimated_duration=task.estimated_duration,
            priority_score=0.5,
            reasoning=["Fallback scheduling due to AI processing error"],
            confidence=0.3
        )
    
    def _get_available_slots_for_day(self, 
                                   target_date: datetime,
                                   required_duration: int) -> List[Tuple[datetime, int]]:
        """Get available time slots for a specific day"""
        slots = []
        date_key = target_date.strftime('%Y-%m-%d')
        existing_schedule = self._schedule.get(date_key, [])
        
        # Define working hours (9 AM to 6 PM)
        start_time = datetime.combine(target_date, datetime.min.time().replace(hour=9))
        end_time = datetime.combine(target_date, datetime.min.time().replace(hour=18))
        
        current_time = start_time
        
        while current_time + timedelta(minutes=required_duration) <= end_time:
            # Check if this slot conflicts with existing tasks
            slot_conflicts = any(
                self._time_ranges_overlap(
                    current_time, 
                    current_time + timedelta(minutes=required_duration),
                    decision.scheduled_time,
                    decision.scheduled_time + timedelta(minutes=decision.estimated_duration)
                )
                for decision in existing_schedule
            )
            
            if not slot_conflicts:
                slots.append((current_time, required_duration))
            
            current_time += timedelta(minutes=30)  # 30-minute increments
        
        return slots
    
    def _time_ranges_overlap(self, 
                           start1: datetime, end1: datetime,
                           start2: datetime, end2: datetime) -> bool:
        """Check if two time ranges overlap"""
        return start1 < end2 and start2 < end1


class AdaptivePriorityEngine:
    """AI engine for adaptive task prioritization"""
    
    def __init__(self, memory_limit_mb: int = 15):
        self.memory_limit_mb = memory_limit_mb
        self.logger = get_rich_logger(f"{__name__}.AdaptivePriorityEngine")
        
        # Learning data (limited for memory optimization)
        self._priority_patterns: deque = deque(maxlen=100)
        self._user_preferences: Dict[str, float] = defaultdict(float)
    
    def calculate_adaptive_priority(self, 
                                  task: Task,
                                  context: TaskContext,
                                  history: deque) -> float:
        """Calculate adaptive priority score using AI"""
        base_priority = self._get_base_priority_score(task)
        
        # Context adjustments
        energy_adjustment = self._calculate_energy_adjustment(task, context)
        deadline_adjustment = self._calculate_deadline_adjustment(task)
        pattern_adjustment = self._calculate_pattern_adjustment(task, history)
        
        # Combine all factors
        adaptive_priority = (
            base_priority * 0.4 +
            energy_adjustment * 0.2 +
            deadline_adjustment * 0.3 +
            pattern_adjustment * 0.1
        )
        
        return max(0.0, min(adaptive_priority, 1.0))
    
    def _get_base_priority_score(self, task: Task) -> float:
        """Get base priority score from task properties"""
        priority_map = {
            TaskPriority.LOW: 0.2,
            TaskPriority.NORMAL: 0.4,
            TaskPriority.HIGH: 0.7,
            TaskPriority.URGENT: 0.9
        }
        
        return priority_map.get(task.priority, 0.4)
    
    def _calculate_energy_adjustment(self, task: Task, context: TaskContext) -> float:
        """Calculate energy-based priority adjustment"""
        task_energy_requirement = task.difficulty * 0.1  # Estimate
        energy_match = 1.0 - abs(context.user_energy_level - task_energy_requirement)
        
        return energy_match * 0.5
    
    def _calculate_deadline_adjustment(self, task: Task) -> float:
        """Calculate deadline-based priority adjustment"""
        if not task.due_date:
            return 0.3  # Neutral for tasks without deadlines
        
        days_remaining = (task.due_date - datetime.now()).days
        
        if days_remaining <= 0:
            return 1.0  # Maximum priority for overdue
        elif days_remaining <= 1:
            return 0.9  # Very high for due today/tomorrow
        elif days_remaining <= 3:
            return 0.7  # High for due soon
        elif days_remaining <= 7:
            return 0.5  # Medium for due this week
        else:
            return 0.3  # Lower for distant deadlines


class ContextAnalyzer:
    """Analyzes context for AI scheduling decisions"""
    
    def __init__(self, memory_limit_mb: int = 15):
        self.memory_limit_mb = memory_limit_mb
        self.logger = get_rich_logger(f"{__name__}.ContextAnalyzer")


class DeadlinePredictor:
    """Predicts optimal deadlines and scheduling windows"""
    
    def __init__(self, memory_limit_mb: int = 10):
        self.memory_limit_mb = memory_limit_mb
        self.logger = get_rich_logger(f"{__name__}.DeadlinePredictor")


class SchedulingLearningEngine:
    """Learning engine for improving scheduling decisions"""
    
    def __init__(self, memory_limit_mb: int = 10):
        self.memory_limit_mb = memory_limit_mb
        self.logger = get_rich_logger(f"{__name__}.SchedulingLearningEngine")
        
        # Learning data storage
        self._decisions_history: deque = deque(maxlen=200)
        self._feedback_history: deque = deque(maxlen=100)
    
    def record_scheduling_decision(self, 
                                 task: Task,
                                 decision: SchedulingDecision,
                                 context: TaskContext) -> None:
        """Record a scheduling decision for learning"""
        decision_record = {
            'timestamp': datetime.now().isoformat(),
            'task_category': task.category,
            'task_priority': task.priority.value,
            'scheduled_hour': decision.scheduled_time.hour,
            'context_energy': context.user_energy_level,
            'decision_confidence': decision.confidence
        }
        
        self._decisions_history.append(decision_record)
    
    def process_user_feedback(self, 
                            decision_id: str,
                            feedback_score: float,
                            feedback_notes: str) -> None:
        """Process user feedback for learning"""
        feedback_record = {
            'decision_id': decision_id,
            'feedback_score': feedback_score,
            'feedback_notes': feedback_notes,
            'timestamp': datetime.now().isoformat()
        }
        
        self._feedback_history.append(feedback_record)
        
        # Simple learning: adjust future similar decisions
        self._adjust_learning_parameters(feedback_score, feedback_notes)
