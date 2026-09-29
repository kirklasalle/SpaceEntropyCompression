#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_dpa\integration\task_integration.py #command_line #python #source_code  
**Category:** Source Code  
**Status:** Active
"""









# Task Integration

**Created:** 2024-10-15  
**Updated:** 2025-07-26 10:26:57  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_dpa\integration\task_integration.py #command_line #python #source_code  
**Category:** Source Code  
**Status:** Active

"""
Task Integration Manager for ImpressionCore Personal Assistant

This module integrates task management and reminders with the existing
Personal Assistant Core components, providing seamless task handling
through natural language interfaces.

Created: 2025-01-03
Author: GitHub Copilot
Version: 1.0
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
import re

from ..tasks.task_manager import TaskManager
from ..tasks.models import Task, TaskPriority, TaskStatus, TriggerType, NotificationType
from ..reminders.reminder_engine import ReminderEngine
from ..core.query_processor import QueryProcessor
from ..core.context_manager import ConversationSession
from ..nlp.nlu_engine import NLUEngine
from ...core.utils.rich_logging import setup_rich_logging
from ...core.utils.rich_status_animation import StatusAnimation


class TaskIntegrationManager:
    """
    Integration layer that connects task management and reminders with
    the Personal Assistant Core components for seamless user interaction.
    """
    
    def __init__(self, 
                 task_manager: TaskManager,
                 reminder_engine: ReminderEngine,
                 query_processor: QueryProcessor,
                 nlu_engine: NLUEngine,
                 user_id: Optional[str] = None):
        """Initialize task integration manager"""
        self.logger = setup_rich_logging(__name__)
        self.user_id = user_id
        
        # Component references
        self.task_manager = task_manager
        self.reminder_engine = reminder_engine
        self.query_processor = query_processor
        self.nlu_engine = nlu_engine
        
        # Task-specific intent mappings
        self.task_intents = {
            'create_task': self._handle_create_task,
            'list_tasks': self._handle_list_tasks,
            'update_task': self._handle_update_task,
            'complete_task': self._handle_complete_task,
            'delete_task': self._handle_delete_task,
            'set_reminder': self._handle_set_reminder,
            'search_tasks': self._handle_search_tasks,
            'task_status': self._handle_task_status,
            'schedule_event': self._handle_schedule_event
        }
        
        # Entity extraction patterns
        self._setup_entity_patterns()
        
        # Register with query processor
        self._register_task_handlers()
        
        self.logger.info("TaskIntegrationManager initialized", extra={
            "user_id": self.user_id,
            "registered_intents": len(self.task_intents)
        })
    
    def process_task_query(self, query: str, context: Optional[ConversationSession] = None) -> Dict[str, Any]:
        """
        Process a natural language query related to tasks or reminders
        
        Args:
            query: Natural language query
            context: Conversation context
        
        Returns:
            Processing result with task actions and response
        """
        animation = StatusAnimation(
            total_steps=5,
            description="Processing task query"
        )
        
        try:
            animation.start()
            
            # Step 1: Analyze query with NLU
            animation.update(1, "Analyzing query intent")
            nlu_result = self.nlu_engine.analyze_query(query, context)
            
            # Step 2: Extract task-specific entities
            animation.update(2, "Extracting task entities")
            entities = self._extract_task_entities(query)
            
            # Step 3: Determine primary intent
            animation.update(3, "Determining task intent")
            primary_intent = self._get_primary_task_intent(nlu_result, entities)
            
            # Step 4: Execute task action
            animation.update(4, "Executing task action")
            if primary_intent in self.task_intents:
                result = self.task_intents[primary_intent](query, entities, context)
            else:
                result = self._handle_generic_task_query(query, entities, context)
            
            # Step 5: Generate response
            animation.update(5, "Generating response")
            response = self._generate_task_response(result, primary_intent)
            
            animation.complete("Task query processed successfully")
            
            return {
                'intent': primary_intent,
                'entities': entities,
                'result': result,
                'response': response,
                'success': True
            }
            
        except Exception as e:
            animation.fail(f"Failed to process task query: {str(e)}")
            self.logger.error("Task query processing failed", extra={
                "query": query,
                "error": str(e)
            })
            
            return {
                'intent': None,
                'entities': {},
                'result': None,
                'response': f"I encountered an error processing your task request: {str(e)}",
                'success': False
            }
    
    def _handle_create_task(self, query: str, entities: Dict[str, Any], context: Optional[ConversationSession]) -> Dict[str, Any]:
        """Handle task creation requests"""
        try:
            # Extract task details from entities
            title = entities.get('task_title') or self._extract_task_title(query)
            description = entities.get('description')
            due_date = entities.get('due_date')
            priority = entities.get('priority', TaskPriority.MEDIUM)
            category = entities.get('category')
            tags = entities.get('tags', [])
            
            if not title:
                return {'success': False, 'error': 'Task title is required'}
            
            # Create task
            task = self.task_manager.create_task(
                title=title,
                description=description,
                due_date=due_date,
                priority=priority,
                category=category,
                tags=tags
            )
            
            # Create reminder if requested
            reminder_info = entities.get('reminder')
            if reminder_info:
                self._create_task_reminder(task, reminder_info)
            
            return {
                'success': True,
                'task': task,
                'action': 'created',
                'message': f"Created task: {title}"
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _handle_list_tasks(self, query: str, entities: Dict[str, Any], context: Optional[ConversationSession]) -> Dict[str, Any]:
        """Handle task listing requests"""
        try:
            # Extract filtering criteria
            category = entities.get('category')
            status = entities.get('status')
            priority = entities.get('priority')
            project = entities.get('project')
            tags = entities.get('tags')
            
            # Special filters
            if 'overdue' in query.lower():
                tasks = self.task_manager.get_overdue_tasks()
            elif 'upcoming' in query.lower() or 'due soon' in query.lower():
                days = entities.get('days', 7)
                tasks = self.task_manager.get_upcoming_tasks(days)
            else:
                tasks = self.task_manager.list_tasks(
                    category=category,
                    status=status,
                    priority=priority,
                    project=project,
                    tags=tags
                )
            
            return {
                'success': True,
                'tasks': tasks,
                'count': len(tasks),
                'action': 'listed',
                'message': f"Found {len(tasks)} tasks"
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _handle_update_task(self, query: str, entities: Dict[str, Any], context: Optional[ConversationSession]) -> Dict[str, Any]:
        """Handle task update requests"""
        try:
            task_id = entities.get('task_id')
            task_title = entities.get('task_title')
            
            # Find task by ID or title
            task = None
            if task_id:
                task = self.task_manager.get_task(task_id)
            elif task_title:
                # Search by title
                matching_tasks = self.task_manager.search_tasks(task_title)
                if matching_tasks:
                    task = matching_tasks[0]  # Take first match
            
            if not task:
                return {'success': False, 'error': 'Task not found'}
            
            # Extract updates
            updates = {}
            if 'title' in entities:
                updates['title'] = entities['title']
            if 'description' in entities:
                updates['description'] = entities['description']
            if 'due_date' in entities:
                updates['due_date'] = entities['due_date']
            if 'priority' in entities:
                updates['priority'] = entities['priority']
            if 'category' in entities:
                updates['category'] = entities['category']
            if 'progress' in entities:
                updates['progress_percentage'] = entities['progress']
            
            # Apply updates
            success = self.task_manager.update_task(task.id, **updates)
            
            return {
                'success': success,
                'task': task,
                'updates': updates,
                'action': 'updated',
                'message': f"Updated task: {task.title}"
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _handle_complete_task(self, query: str, entities: Dict[str, Any], context: Optional[ConversationSession]) -> Dict[str, Any]:
        """Handle task completion requests"""
        try:
            task_id = entities.get('task_id')
            task_title = entities.get('task_title')
            
            # Find task
            task = None
            if task_id:
                task = self.task_manager.get_task(task_id)
            elif task_title:
                matching_tasks = self.task_manager.search_tasks(task_title)
                if matching_tasks:
                    task = matching_tasks[0]
            
            if not task:
                return {'success': False, 'error': 'Task not found'}
            
            # Complete task
            success = self.task_manager.complete_task(task.id)
            
            return {
                'success': success,
                'task': task,
                'action': 'completed',
                'message': f"Completed task: {task.title}"
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _handle_delete_task(self, query: str, entities: Dict[str, Any], context: Optional[ConversationSession]) -> Dict[str, Any]:
        """Handle task deletion requests"""
        try:
            task_id = entities.get('task_id')
            task_title = entities.get('task_title')
            
            # Find task
            task = None
            if task_id:
                task = self.task_manager.get_task(task_id)
            elif task_title:
                matching_tasks = self.task_manager.search_tasks(task_title)
                if matching_tasks:
                    task = matching_tasks[0]
            
            if not task:
                return {'success': False, 'error': 'Task not found'}
            
            # Delete task (soft delete by default)
            soft_delete = not ('permanently' in query.lower() or 'hard delete' in query.lower())
            success = self.task_manager.delete_task(task.id, soft_delete=soft_delete)
            
            return {
                'success': success,
                'task': task,
                'action': 'deleted',
                'soft_delete': soft_delete,
                'message': f"Deleted task: {task.title}"
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _handle_set_reminder(self, query: str, entities: Dict[str, Any], context: Optional[ConversationSession]) -> Dict[str, Any]:
        """Handle reminder creation requests"""
        try:
            task_id = entities.get('task_id')
            task_title = entities.get('task_title')
            reminder_time = entities.get('reminder_time')
            message = entities.get('message') or f"Reminder for task"
            
            # Find task
            task = None
            if task_id:
                task = self.task_manager.get_task(task_id)
            elif task_title:
                matching_tasks = self.task_manager.search_tasks(task_title)
                if matching_tasks:
                    task = matching_tasks[0]
            
            if not task:
                return {'success': False, 'error': 'Task not found'}
            
            # Create reminder
            reminder = self.reminder_engine.create_reminder(
                task_id=task.id,
                message=f"{message}: {task.title}",
                trigger_type=TriggerType.TIME_ABSOLUTE,
                trigger_value=reminder_time,
                notification_type=NotificationType.POPUP
            )
            
            return {
                'success': True,
                'task': task,
                'reminder': reminder,
                'action': 'reminder_set',
                'message': f"Set reminder for task: {task.title}"
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _handle_search_tasks(self, query: str, entities: Dict[str, Any], context: Optional[ConversationSession]) -> Dict[str, Any]:
        """Handle task search requests"""
        try:
            search_query = entities.get('search_query') or self._extract_search_query(query)
            
            if not search_query:
                return {'success': False, 'error': 'Search query is required'}
            
            tasks = self.task_manager.search_tasks(search_query)
            
            return {
                'success': True,
                'tasks': tasks,
                'count': len(tasks),
                'search_query': search_query,
                'action': 'searched',
                'message': f"Found {len(tasks)} tasks matching '{search_query}'"
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _handle_task_status(self, query: str, entities: Dict[str, Any], context: Optional[ConversationSession]) -> Dict[str, Any]:
        """Handle task status requests"""
        try:
            stats = self.task_manager.get_statistics()
            
            return {
                'success': True,
                'statistics': stats,
                'action': 'status',
                'message': f"Task overview: {stats['total_tasks']} total, {stats['completed_tasks']} completed"
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _handle_schedule_event(self, query: str, entities: Dict[str, Any], context: Optional[ConversationSession]) -> Dict[str, Any]:
        """Handle event scheduling requests"""
        # For now, treat as task creation with specific category
        entities['category'] = 'event'
        return self._handle_create_task(query, entities, context)
    
    def _handle_generic_task_query(self, query: str, entities: Dict[str, Any], context: Optional[ConversationSession]) -> Dict[str, Any]:
        """Handle generic task-related queries"""
        return {
            'success': False,
            'action': 'unknown',
            'message': "I'm not sure how to handle that task request. Try asking me to create, list, update, or complete tasks."
        }
    
    def _extract_task_entities(self, query: str) -> Dict[str, Any]:
        """Extract task-specific entities from query"""
        entities = {}
        
        # Extract due date patterns
        due_date = self._extract_due_date(query)
        if due_date:
            entities['due_date'] = due_date
        
        # Extract priority
        priority = self._extract_priority(query)
        if priority:
            entities['priority'] = priority
        
        # Extract category
        category = self._extract_category(query)
        if category:
            entities['category'] = category
        
        # Extract tags
        tags = self._extract_tags(query)
        if tags:
            entities['tags'] = tags
        
        # Extract reminder time
        reminder_time = self._extract_reminder_time(query)
        if reminder_time:
            entities['reminder_time'] = reminder_time
        
        return entities
    
    def _extract_due_date(self, query: str) -> Optional[datetime]:
        """Extract due date from query"""
        query_lower = query.lower()
        
        # Today
        if 'today' in query_lower:
            return datetime.now().replace(hour=23, minute=59, second=59)
        
        # Tomorrow
        if 'tomorrow' in query_lower:
            return (datetime.now() + timedelta(days=1)).replace(hour=23, minute=59, second=59)
        
        # Next week
        if 'next week' in query_lower:
            return datetime.now() + timedelta(weeks=1)
        
        # Specific date patterns (basic implementation)
        date_patterns = [
            r'(\d{1,2})/(\d{1,2})/(\d{4})',  # MM/DD/YYYY
            r'(\d{4})-(\d{1,2})-(\d{1,2})',  # YYYY-MM-DD
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, query)
            if match:
                try:
                    if '/' in pattern:
                        month, day, year = match.groups()
                        return datetime(int(year), int(month), int(day), 23, 59, 59)
                    else:
                        year, month, day = match.groups()
                        return datetime(int(year), int(month), int(day), 23, 59, 59)
                except ValueError:
                    continue
        
        return None
    
    def _extract_priority(self, query: str) -> Optional[TaskPriority]:
        """Extract priority from query"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['urgent', 'critical', 'asap']):
            return TaskPriority.URGENT
        elif any(word in query_lower for word in ['high', 'important']):
            return TaskPriority.HIGH
        elif any(word in query_lower for word in ['low', 'minor']):
            return TaskPriority.LOW
        elif 'medium' in query_lower:
            return TaskPriority.MEDIUM
        
        return None
    
    def _extract_category(self, query: str) -> Optional[str]:
        """Extract category from query"""
        query_lower = query.lower()
        
        categories = {
            'work': ['work', 'office', 'meeting', 'project', 'client'],
            'personal': ['personal', 'family', 'friend'],
            'health': ['doctor', 'appointment', 'exercise', 'health'],
            'shopping': ['buy', 'purchase', 'shopping', 'groceries'],
            'finance': ['pay', 'bill', 'bank', 'money'],
            'learning': ['study', 'course', 'book', 'learn']
        }
        
        for category, keywords in categories.items():
            if any(keyword in query_lower for keyword in keywords):
                return category
        
        return None
    
    def _extract_tags(self, query: str) -> List[str]:
        """Extract tags from query"""
        # Look for hashtags or explicit tag mentions
        tags = []
        
        # Hashtags
        hashtag_pattern = r'#(\w+)'
        hashtags = re.findall(hashtag_pattern, query)
        tags.extend(hashtags)
        
        # Tag keywords
        tag_pattern = r'tag(?:ged)?\s+(?:with\s+|as\s+)?([a-zA-Z0-9_,\s]+)'
        tag_match = re.search(tag_pattern, query, re.IGNORECASE)
        if tag_match:
            tag_text = tag_match.group(1)
            additional_tags = [tag.strip() for tag in tag_text.split(',')]
            tags.extend(additional_tags)
        
        return tags
    
    def _extract_reminder_time(self, query: str) -> Optional[datetime]:
        """Extract reminder time from query"""
        # Similar to due date extraction but for reminders
        query_lower = query.lower()
        
        # Relative time patterns
        if 'in ' in query_lower:
            # "remind me in 30 minutes"
            time_pattern = r'in (\d+) (minute|hour|day)s?'
            match = re.search(time_pattern, query_lower)
            if match:
                value, unit = match.groups()
                value = int(value)
                
                if unit == 'minute':
                    return datetime.now() + timedelta(minutes=value)
                elif unit == 'hour':
                    return datetime.now() + timedelta(hours=value)
                elif unit == 'day':
                    return datetime.now() + timedelta(days=value)
        
        return None
    
    def _extract_task_title(self, query: str) -> Optional[str]:
        """Extract task title from query"""
        # Remove common task action words
        cleaned_query = query
        action_words = ['create', 'add', 'make', 'new', 'task', 'todo', 'remind', 'me', 'to']
        
        for word in action_words:
            cleaned_query = re.sub(rf'\b{word}\b', '', cleaned_query, flags=re.IGNORECASE)
        
        # Clean up whitespace
        cleaned_query = re.sub(r'\s+', ' ', cleaned_query).strip()
        
        # Remove leading/trailing quotes
        cleaned_query = cleaned_query.strip('"\'')
        
        return cleaned_query if cleaned_query else None
    
    def _extract_search_query(self, query: str) -> Optional[str]:
        """Extract search query from natural language"""
        # Remove search action words
        search_patterns = [
            r'search\s+(?:for\s+)?(.+)',
            r'find\s+(?:tasks?\s+)?(?:about\s+|containing\s+)?(.+)',
            r'look\s+for\s+(.+)',
            r'show\s+(?:me\s+)?(?:tasks?\s+)?(?:about\s+|containing\s+)?(.+)'
        ]
        
        for pattern in search_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _get_primary_task_intent(self, nlu_result: Dict[str, Any], entities: Dict[str, Any]) -> str:
        """Determine primary task intent from NLU result and entities"""
        # Check NLU intents first
        if nlu_result.get('intents'):
            for intent in nlu_result['intents']:
                if intent.get('intent') in self.task_intents:
                    return intent['intent']
        
        # Fallback to keyword matching
        query_lower = nlu_result.get('query', '').lower()
        
        if any(word in query_lower for word in ['create', 'add', 'make', 'new']):
            return 'create_task'
        elif any(word in query_lower for word in ['list', 'show', 'display']):
            return 'list_tasks'
        elif any(word in query_lower for word in ['complete', 'done', 'finish']):
            return 'complete_task'
        elif any(word in query_lower for word in ['update', 'modify', 'change']):
            return 'update_task'
        elif any(word in query_lower for word in ['delete', 'remove']):
            return 'delete_task'
        elif any(word in query_lower for word in ['remind', 'reminder']):
            return 'set_reminder'
        elif any(word in query_lower for word in ['search', 'find']):
            return 'search_tasks'
        elif any(word in query_lower for word in ['status', 'summary', 'overview']):
            return 'task_status'
        elif any(word in query_lower for word in ['schedule', 'event', 'meeting']):
            return 'schedule_event'
        
        return 'create_task'  # Default fallback
    
    def _generate_task_response(self, result: Dict[str, Any], intent: str) -> str:
        """Generate natural language response for task operations"""
        if not result.get('success'):
            return f"I encountered an error: {result.get('error', 'Unknown error')}"
        
        action = result.get('action', '')
        message = result.get('message', '')
        
        # Customize response based on action
        if action == 'created':
            task = result.get('task')
            response = f"✅ {message}"
            if task and task.due_date:
                response += f" (due {task.due_date.strftime('%Y-%m-%d')})"
            return response
        
        elif action == 'listed':
            count = result.get('count', 0)
            if count == 0:
                return "📋 I didn't find any tasks matching your criteria."
            elif count == 1:
                return f"📋 I found 1 task for you."
            else:
                return f"📋 I found {count} tasks for you."
        
        elif action == 'completed':
            return f"🎉 {message}"
        
        elif action == 'updated':
            return f"✏️ {message}"
        
        elif action == 'deleted':
            return f"🗑️ {message}"
        
        elif action == 'reminder_set':
            return f"⏰ {message}"
        
        elif action == 'searched':
            count = result.get('count', 0)
            query = result.get('search_query', '')
            return f"🔍 Found {count} tasks matching '{query}'"
        
        elif action == 'status':
            stats = result.get('statistics', {})
            total = stats.get('total_tasks', 0)
            completed = stats.get('completed_tasks', 0)
            overdue = stats.get('overdue_tasks', 0)
            
            response = f"📊 Task Summary:\n"
            response += f"• Total tasks: {total}\n"
            response += f"• Completed: {completed}\n"
            if overdue > 0:
                response += f"• ⚠️ Overdue: {overdue}"
            
            return response
        
        return message or "Task operation completed successfully."
    
    def _setup_entity_patterns(self):
        """Setup entity extraction patterns"""
        # This would contain regex patterns and NLP models for entity extraction
        pass
    
    def _register_task_handlers(self):
        """Register task handlers with the query processor"""
        # This would register task intents with the main query processor
        pass
    
    def _create_task_reminder(self, task: Task, reminder_info: Dict[str, Any]):
        """Create a reminder for a task"""
        try:
            reminder_time = reminder_info.get('time')
            message = reminder_info.get('message', f"Reminder: {task.title}")
            
            if reminder_time:
                self.reminder_engine.create_reminder(
                    task_id=task.id,
                    message=message,
                    trigger_type=TriggerType.TIME_ABSOLUTE,
                    trigger_value=reminder_time,
                    notification_type=NotificationType.POPUP
                )
                
                self.logger.info("Task reminder created", extra={
                    "task_id": task.id,
                    "reminder_time": reminder_time.isoformat() if isinstance(reminder_time, datetime) else str(reminder_time)
                })
        
        except Exception as e:
            self.logger.error("Failed to create task reminder", extra={
                "task_id": task.id,
                "error": str(e)
            })


class TaskIntegration:
    """
    Simplified interface for task integration functionality.
    
    This class provides a clean interface for external components
    to interact with task management features.
    """
    
    def __init__(self, integration_manager: TaskIntegrationManager = None):
        """
        Initialize task integration.
        
        Args:
            integration_manager: Optional TaskIntegrationManager instance
        """
        self.integration_manager = integration_manager
        self.logger = setup_rich_logging(__name__)
    
    def process_task_query(self, query: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process a task-related query through the integration manager.
        
        Args:
            query: Natural language query about tasks
            user_context: Additional context about the user
            
        Returns:
            Dictionary containing the response and any created/modified tasks
        """
        if not self.integration_manager:
            return {
                'success': False,
                'message': 'Task integration manager not initialized',
                'tasks': []
            }
        
        try:
            # Create a mock conversation session for the query
            session = ConversationSession(
                session_id=f"task_query_{datetime.now().timestamp()}",
                user_id=user_context.get('user_id', 'default') if user_context else 'default'
            )
            
            # Process the query
            response = self.integration_manager.process_task_query(query, session)
            
            return {
                'success': True,
                'message': response,
                'tasks': []  # Could be populated with created/modified tasks
            }
            
        except Exception as e:
            self.logger.error(f"Failed to process task query: {e}")
            return {
                'success': False,
                'message': f'Error processing task query: {str(e)}',
                'tasks': []
            }
    
    def get_integration_status(self) -> Dict[str, Any]:
        """
        Get the current status of task integration.
        
        Returns:
            Dictionary containing integration status information
        """
        if not self.integration_manager:
            return {
                'initialized': False,
                'components': {}
            }
        
        return {
            'initialized': True,
            'components': {
                'task_manager': self.integration_manager.task_manager is not None,
                'reminder_engine': self.integration_manager.reminder_engine is not None,
                'query_processor': self.integration_manager.query_processor is not None,
                'nlu_engine': self.integration_manager.nlu_engine is not None
            }
        }
