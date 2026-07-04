"""
Scheduler Module
Background jobs for notifications and task management
"""
import logging
import threading
import time
from datetime import datetime
from .note_handler import NoteHandler
from .notifier import Notifier
from .emailer import Emailer
from .user_manager import UserManager

logger = logging.getLogger(__name__)


class TaskScheduler:
    def __init__(self,
                 user_manager: UserManager,
                 notifier: Notifier,
                 emailer: Emailer,
                 check_interval: int = 1800):  # 30 minutes default
        """
        Initialize TaskScheduler

        Iterates every registered user on each tick and checks/archives
        their tasks, since notes/tasks are stored per-user.

        Args:
            user_manager: UserManager instance, used to enumerate users
            notifier: Notifier instance
            emailer: Emailer instance
            check_interval: Interval in seconds between checks (default 1800 = 30 min)
        """
        self.user_manager = user_manager
        self.notifier = notifier
        self.emailer = emailer
        self.check_interval = check_interval
        self.running = False
        self.thread = None
        self.recipient_email = None  # Set via config

    def start(self):
        """Start the background scheduler"""
        if self.running:
            logger.info("Scheduler already running")
            return

        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        logger.info("Scheduler started (checking every %s seconds)", self.check_interval)

    def stop(self):
        """Stop the background scheduler"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Scheduler stopped")

    def _run(self):
        """Main scheduler loop"""
        while self.running:
            try:
                self._tick()
            except Exception:
                logger.exception("Error in scheduler tick")

            # Sleep in small intervals to allow quick shutdown
            for _ in range(self.check_interval):
                if not self.running:
                    break
                time.sleep(1)

    def _tick(self):
        """Run one check/archive pass across every registered user"""
        for user in self.user_manager.load_users()['users']:
            note_handler = NoteHandler(user_id=user['id'])
            self._check_tasks(note_handler)
            self._auto_archive(note_handler)

    def _check_tasks(self, note_handler: NoteHandler):
        """Check a user's tasks and send notifications"""
        try:
            tasks = note_handler.get_all_tasks()

            # Send desktop notifications
            stats = self.notifier.check_and_notify_tasks(
                tasks,
                deadline_hours=24,
                stale_hours=48
            )

            if any(stats.values()):
                logger.info("Notifications sent - Deadline: %s, Overdue: %s, Stale: %s",
                             stats['deadline'], stats['overdue'], stats['stale'])

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
                        except (ValueError, KeyError):
                            logger.warning("Skipping reminder for task with unparseable last_update: %s",
                                           task.get('id'))

        except Exception:
            logger.exception("Error checking tasks")

    def _auto_archive(self, note_handler: NoteHandler):
        """Archive completed tasks older than threshold"""
        try:
            data = note_handler.load_notes()
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
                            note_handler.archive_note(note['id'])
                            archived_count += 1
                    except (ValueError, KeyError):
                        logger.warning("Skipping auto-archive for note with unparseable date_created: %s",
                                       note.get('id'))

            if archived_count > 0:
                logger.info("Auto-archived %s completed notes", archived_count)

        except Exception:
            logger.exception("Error auto-archiving")

    def set_recipient_email(self, email: str):
        """Set the recipient email for reminders"""
        self.recipient_email = email
