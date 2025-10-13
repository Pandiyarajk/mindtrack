"""
Scheduler Module
Background jobs for notifications and task management
"""
import threading
import time
from datetime import datetime, timedelta
from typing import Callable, Optional
from .note_handler import NoteHandler
from .notifier import Notifier
from .emailer import Emailer


class TaskScheduler:
    def __init__(self, 
                 note_handler: NoteHandler,
                 notifier: Notifier,
                 emailer: Emailer,
                 check_interval: int = 1800):  # 30 minutes default
        """
        Initialize TaskScheduler
        
        Args:
            note_handler: NoteHandler instance
            notifier: Notifier instance
            emailer: Emailer instance
            check_interval: Interval in seconds between checks (default 1800 = 30 min)
        """
        self.note_handler = note_handler
        self.notifier = notifier
        self.emailer = emailer
        self.check_interval = check_interval
        self.running = False
        self.thread = None
        self.recipient_email = None  # Set via config
    
    def start(self):
        """Start the background scheduler"""
        if self.running:
            print("Scheduler already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        print(f"Scheduler started (checking every {self.check_interval} seconds)")
    
    def stop(self):
        """Stop the background scheduler"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        print("Scheduler stopped")
    
    def _run(self):
        """Main scheduler loop"""
        while self.running:
            try:
                self._check_tasks()
                self._auto_archive()
            except Exception as e:
                print(f"Error in scheduler: {e}")
            
            # Sleep in small intervals to allow quick shutdown
            for _ in range(self.check_interval):
                if not self.running:
                    break
                time.sleep(1)
    
    def _check_tasks(self):
        """Check all tasks and send notifications"""
        try:
            tasks = self.note_handler.get_all_tasks()
            
            # Send desktop notifications
            stats = self.notifier.check_and_notify_tasks(
                tasks,
                deadline_hours=24,
                stale_hours=48
            )
            
            if any(stats.values()):
                print(f"Notifications sent - Deadline: {stats['deadline']}, "
                      f"Overdue: {stats['overdue']}, Stale: {stats['stale']}")
            
            # Send email reminders for stale tasks
            if self.recipient_email and self.emailer.enabled:
                for task in tasks:
                    if task.get('status', '').lower() != 'done':
                        try:
                            last_update = datetime.fromisoformat(task['last_update'])
                            hours_since = (datetime.now() - last_update).total_seconds() / 3600
                            
                            # Email if no update for 72 hours (3 days)
                            if hours_since > 72:
                                note_text = task.get('note_text', '')
                                self.emailer.send_task_reminder(
                                    self.recipient_email,
                                    task,
                                    note_text
                                )
                        except:
                            pass
        
        except Exception as e:
            print(f"Error checking tasks: {e}")
    
    def _auto_archive(self):
        """Archive completed tasks older than threshold"""
        try:
            data = self.note_handler.load_notes()
            now = datetime.now()
            archived_count = 0
            
            for note in data['notes']:
                # Check if all tasks in note are done and old
                tasks = note.get('tasks', [])
                if not tasks:
                    continue
                
                all_done = all(t.get('status', '').lower() == 'done' for t in tasks)
                
                if all_done:
                    # Check if note is older than 7 days
                    try:
                        created = datetime.fromisoformat(note['date_created'])
                        days_old = (now - created).days
                        
                        if days_old > 7:
                            self.note_handler.archive_note(note['id'])
                            archived_count += 1
                    except:
                        pass
            
            if archived_count > 0:
                print(f"Auto-archived {archived_count} completed notes")
        
        except Exception as e:
            print(f"Error auto-archiving: {e}")
    
    def set_recipient_email(self, email: str):
        """Set the recipient email for reminders"""
        self.recipient_email = email


class SimpleScheduler:
    """
    Simplified scheduler without APScheduler dependency
    Uses threading for background tasks
    """
    
    def __init__(self):
        self.jobs = []
        self.running = False
        self.thread = None
    
    def add_job(self, func: Callable, interval_seconds: int, job_id: str = None):
        """Add a job to run periodically"""
        job = {
            'id': job_id or f'job_{len(self.jobs)}',
            'func': func,
            'interval': interval_seconds,
            'last_run': None
        }
        self.jobs.append(job)
        return job['id']
    
    def start(self):
        """Start the scheduler"""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        print("SimpleScheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        print("SimpleScheduler stopped")
    
    def _run(self):
        """Main scheduler loop"""
        while self.running:
            now = time.time()
            
            for job in self.jobs:
                if job['last_run'] is None or (now - job['last_run']) >= job['interval']:
                    try:
                        job['func']()
                        job['last_run'] = now
                    except Exception as e:
                        print(f"Error running job {job['id']}: {e}")
            
            time.sleep(1)  # Check every second
