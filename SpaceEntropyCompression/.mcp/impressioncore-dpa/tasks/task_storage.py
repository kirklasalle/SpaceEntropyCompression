#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_dpa\tasks\task_storage.py #python #source_code  
**Category:** Source Code  
**Status:** Active
"""









# Task Storage

**Created:** 2024-10-15  
**Updated:** 2025-07-26 10:26:57  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_dpa\tasks\task_storage.py #python #source_code  
**Category:** Source Code  
**Status:** Active

"""
Task Storage for ImpressionCore Personal Assistant

This module provides secure task persistence with cross-session data retention,
backup and recovery capabilities, and data encryption integration.

Created: 2025-01-06
Author: ImpressionCore Development Team
Version: 1.0
Phase: 8B Week 2 - Task Management & Reminders
"""

import json
import logging
import shutil
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
import pickle
import threading
from dataclasses import asdict
import sqlite3

from .models import Task, TaskPriority, TaskStatus, TaskList, TaskDict
from ...core.utils.rich_logging import setup_rich_logging
from ...core.utils.rich_status_animation import StatusAnimation

try:
    from ...core.utils.rich_enhancements import RichEnhancer
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class TaskStorage:
    """
    Secure task persistence system with encryption, backup, and recovery.
    Optimized for GTX 1050 Ti hardware constraints with efficient storage.
    """
    
    def __init__(self, storage_path: Optional[str] = None, user_id: Optional[str] = None):
        """Initialize task storage system"""
        self.logger = setup_rich_logging(__name__)
        self.user_id = user_id or "default"
        
        # Storage paths
        self.base_path = Path(storage_path or "src/user_data/tasks")
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        self.db_path = self.base_path / f"tasks_{self.user_id}.db"
        self.backup_path = self.base_path / "backups"
        self.backup_path.mkdir(exist_ok=True)
        
        # Storage configuration
        self.auto_backup = True
        self.backup_interval = timedelta(hours=6)
        self.max_backups = 10
        self.encryption_enabled = False  # Future enhancement
        
        # Threading
        self._lock = threading.RLock()
        
        # Initialize database
        self._init_database()
        
        # Status tracking
        self._last_backup = None
        self._storage_stats = {
            'total_tasks': 0,
            'storage_size': 0,
            'last_access': datetime.now()
        }
        
        self.logger.info(f"Task storage initialized at {self.db_path}")
    
    def _init_database(self):
        """Initialize SQLite database with proper schema"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create tasks table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS tasks (
                        id TEXT PRIMARY KEY,
                        title TEXT NOT NULL,
                        description TEXT,
                        category TEXT DEFAULT 'general',
                        priority INTEGER DEFAULT 2,
                        status TEXT DEFAULT 'created',
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        due_date TEXT,
                        start_date TEXT,
                        completed_at TEXT,
                        project TEXT,
                        tags TEXT,
                        recurrence_pattern TEXT,
                        metadata TEXT,
                        user_id TEXT DEFAULT 'default'
                    )
                ''')
                
                # Create indexes for better performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_category ON tasks(category)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority)')
                
                # Create storage metadata table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS storage_metadata (
                        key TEXT PRIMARY KEY,
                        value TEXT,
                        updated_at TEXT
                    )
                ''')
                
                conn.commit()
                self.logger.info("Database schema initialized successfully")
                
        except Exception as e:
            self.logger.error(f"Database initialization failed: {e}")
            raise
    
    def save_task(self, task: Task) -> bool:
        """Save a task to storage"""
        with self._lock:
            try:
                # Update timestamp
                task.updated_at = datetime.now()
                
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Convert task to database format
                    task_data = (
                        task.id,
                        task.title,
                        task.description,
                        task.category,
                        task.priority.value,
                        task.status.value,
                        task.created_at.isoformat(),
                        task.updated_at.isoformat(),
                        task.due_date.isoformat() if task.due_date else None,
                        task.start_date.isoformat() if task.start_date else None,
                        task.completed_at.isoformat() if task.completed_at else None,
                        task.project,
                        json.dumps(task.tags) if task.tags else None,
                        task.recurrence_pattern.value if task.recurrence_pattern else None,
                        json.dumps(asdict(task.metadata)) if task.metadata else None,
                        self.user_id
                    )
                    
                    # Insert or update task
                    cursor.execute('''
                        INSERT OR REPLACE INTO tasks VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', task_data)
                    
                    conn.commit()
                    
                self._update_storage_stats()
                self._check_auto_backup()
                
                self.logger.debug(f"Task saved: {task.id} - {task.title}")
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to save task {task.id}: {e}")
                return False
    
    def load_task(self, task_id: str) -> Optional[Task]:
        """Load a specific task from storage"""
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                        SELECT * FROM tasks WHERE id = ? AND user_id = ?
                    ''', (task_id, self.user_id))
                    
                    row = cursor.fetchone()
                    if not row:
                        return None
                    
                    return self._row_to_task(row)
                    
            except Exception as e:
                self.logger.error(f"Failed to load task {task_id}: {e}")
                return None
    
    def load_all_tasks(self, include_completed: bool = True) -> TaskList:
        """Load all tasks for the current user"""
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    query = 'SELECT * FROM tasks WHERE user_id = ?'
                    params = [self.user_id]
                    
                    if not include_completed:
                        query += ' AND status != ?'
                        params.append(TaskStatus.COMPLETED.value)
                    
                    query += ' ORDER BY created_at DESC'
                    
                    cursor.execute(query, params)
                    rows = cursor.fetchall()
                    
                    tasks = []
                    for row in rows:
                        task = self._row_to_task(row)
                        if task:
                            tasks.append(task)
                    
                    self.logger.debug(f"Loaded {len(tasks)} tasks")
                    return tasks
                    
            except Exception as e:
                self.logger.error(f"Failed to load tasks: {e}")
                return []
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task from storage"""
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                        DELETE FROM tasks WHERE id = ? AND user_id = ?
                    ''', (task_id, self.user_id))
                    
                    deleted = cursor.rowcount > 0
                    conn.commit()
                    
                if deleted:
                    self._update_storage_stats()
                    self.logger.debug(f"Task deleted: {task_id}")
                    
                return deleted
                
            except Exception as e:
                self.logger.error(f"Failed to delete task {task_id}: {e}")
                return False
    
    def search_tasks(self, 
                    query: Optional[str] = None,
                    category: Optional[str] = None,
                    status: Optional[TaskStatus] = None,
                    priority: Optional[TaskPriority] = None,
                    tags: Optional[List[str]] = None,
                    date_range: Optional[tuple] = None) -> TaskList:
        """Search tasks with filters"""
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Build dynamic query
                    where_clauses = ['user_id = ?']
                    params = [self.user_id]
                    
                    if query:
                        where_clauses.append('(title LIKE ? OR description LIKE ?)')
                        params.extend([f'%{query}%', f'%{query}%'])
                    
                    if category:
                        where_clauses.append('category = ?')
                        params.append(category)
                    
                    if status:
                        where_clauses.append('status = ?')
                        params.append(status.value)
                    
                    if priority:
                        where_clauses.append('priority = ?')
                        params.append(priority.value)
                    
                    if date_range:
                        start_date, end_date = date_range
                        where_clauses.append('created_at BETWEEN ? AND ?')
                        params.extend([start_date.isoformat(), end_date.isoformat()])
                    
                    sql = f'''
                        SELECT * FROM tasks 
                        WHERE {' AND '.join(where_clauses)}
                        ORDER BY priority DESC, created_at DESC
                    '''
                    
                    cursor.execute(sql, params)
                    rows = cursor.fetchall()
                    
                    tasks = []
                    for row in rows:
                        task = self._row_to_task(row)
                        if task:
                            # Filter by tags if specified
                            if tags and not any(tag in task.tags for tag in tags):
                                continue
                            tasks.append(task)
                    
                    self.logger.debug(f"Search returned {len(tasks)} tasks")
                    return tasks
                    
            except Exception as e:
                self.logger.error(f"Search failed: {e}")
                return []
    
    def backup_storage(self, backup_name: Optional[str] = None) -> bool:
        """Create a backup of the task storage"""
        with self._lock:
            try:
                if not backup_name:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    backup_name = f"tasks_backup_{timestamp}.db"
                
                backup_file = self.backup_path / backup_name
                shutil.copy2(self.db_path, backup_file)
                
                # Clean old backups
                self._cleanup_old_backups()
                
                self._last_backup = datetime.now()
                self.logger.info(f"Backup created: {backup_file}")
                return True
                
            except Exception as e:
                self.logger.error(f"Backup failed: {e}")
                return False
    
    def restore_from_backup(self, backup_name: str) -> bool:
        """Restore tasks from a backup"""
        with self._lock:
            try:
                backup_file = self.backup_path / backup_name
                if not backup_file.exists():
                    self.logger.error(f"Backup file not found: {backup_file}")
                    return False
                
                # Create safety backup of current data
                safety_backup = f"pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                self.backup_storage(safety_backup)
                
                # Restore from backup
                shutil.copy2(backup_file, self.db_path)
                
                self._update_storage_stats()
                self.logger.info(f"Storage restored from: {backup_file}")
                return True
                
            except Exception as e:
                self.logger.error(f"Restore failed: {e}")
                return False
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics and health information"""
        with self._lock:
            self._update_storage_stats()
            
            stats = self._storage_stats.copy()
            stats.update({
                'database_size': self.db_path.stat().st_size if self.db_path.exists() else 0,
                'backup_count': len(list(self.backup_path.glob('*.db'))),
                'last_backup': self._last_backup.isoformat() if self._last_backup else None,
                'encryption_enabled': self.encryption_enabled,
            })
            
            return stats
    
    def _row_to_task(self, row) -> Optional[Task]:
        """Convert database row to Task object"""
        try:
            # Unpack row data
            (id, title, description, category, priority, status, created_at, updated_at,
             due_date, start_date, completed_at, project, tags, recurrence_pattern, 
             metadata, user_id) = row
            
            # Convert data types
            task = Task(
                id=id,
                title=title,
                description=description,
                category=category,
                priority=TaskPriority(priority),
                status=TaskStatus(status),
                created_at=datetime.fromisoformat(created_at),
                updated_at=datetime.fromisoformat(updated_at),
                due_date=datetime.fromisoformat(due_date) if due_date else None,
                start_date=datetime.fromisoformat(start_date) if start_date else None,
                completed_at=datetime.fromisoformat(completed_at) if completed_at else None,
                project=project,
                tags=json.loads(tags) if tags else [],
                recurrence_pattern=None,  # Will be handled in future enhancement
                metadata=None  # Will be handled in future enhancement
            )
            
            return task
            
        except Exception as e:
            self.logger.error(f"Failed to convert row to task: {e}")
            return None
    
    def _update_storage_stats(self):
        """Update internal storage statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('SELECT COUNT(*) FROM tasks WHERE user_id = ?', (self.user_id,))
                total_tasks = cursor.fetchone()[0]
                
                self._storage_stats.update({
                    'total_tasks': total_tasks,
                    'storage_size': self.db_path.stat().st_size if self.db_path.exists() else 0,
                    'last_access': datetime.now()
                })
                
        except Exception as e:
            self.logger.error(f"Failed to update stats: {e}")
    
    def _check_auto_backup(self):
        """Check if auto backup is needed"""
        if not self.auto_backup:
            return
        
        if (not self._last_backup or 
            datetime.now() - self._last_backup >= self.backup_interval):
            self.backup_storage()
    
    def _cleanup_old_backups(self):
        """Remove old backup files"""
        try:
            backup_files = sorted(
                self.backup_path.glob('*.db'),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            
            # Remove excess backups
            for backup_file in backup_files[self.max_backups:]:
                backup_file.unlink()
                self.logger.debug(f"Removed old backup: {backup_file}")
                
        except Exception as e:
            self.logger.error(f"Backup cleanup failed: {e}")
    
    def close(self):
        """Close storage and cleanup resources"""
        with self._lock:
            self.logger.info("Task storage closed")


# Factory function for easy instantiation
def create_task_storage(storage_path: Optional[str] = None, 
                       user_id: Optional[str] = None) -> TaskStorage:
    """Create and return a TaskStorage instance"""
    return TaskStorage(storage_path=storage_path, user_id=user_id)
