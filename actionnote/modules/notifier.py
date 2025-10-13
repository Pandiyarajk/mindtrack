"""
Notifier Module
Sends desktop notifications for tasks
"""
import platform
from datetime import datetime, timedelta
from typing import Dict, List

try:
    from plyer import notification
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False
    print("Warning: plyer not available. Desktop notifications disabled.")


class Notifier:
    def __init__(self, app_name="ActionNote"):
        self.app_name = app_name
        self.platform = platform.system()
    
    def send_notification(self, title: str, message: str, timeout: int = 10) -> bool:
        """
        Send a desktop notification
        
        Args:
            title: Notification title
            message: Notification message
            timeout: Duration to show notification (seconds)
        
        Returns:
            True if successful, False otherwise
        """
        if not PLYER_AVAILABLE:
            print(f"[NOTIFICATION] {title}: {message}")
            return False
        
        try:
            notification.notify(
                title=title,
                message=message,
                app_name=self.app_name,
                timeout=timeout
            )
            return True
        except Exception as e:
            print(f"Error sending notification: {e}")
            return False
    
    def notify_task_deadline(self, task: Dict) -> bool:
        """Notify about an approaching task deadline"""
        title = f"⚠️ Task Deadline Approaching"
        message = f"{task['title']}\nPriority: {task['priority']}\nDeadline: {task.get('deadline', 'Not set')}"
        return self.send_notification(title, message)
    
    def notify_task_overdue(self, task: Dict) -> bool:
        """Notify about an overdue task"""
        title = f"🚨 Task Overdue"
        message = f"{task['title']}\nPriority: {task['priority']}\nStatus: {task['status']}"
        return self.send_notification(title, message)
    
    def notify_task_stale(self, task: Dict, hours: int) -> bool:
        """Notify about a task with no updates"""
        title = f"💤 Task Needs Attention"
        message = f"{task['title']}\nNo update for {hours} hours\nPriority: {task['priority']}"
        return self.send_notification(title, message)
    
    def check_and_notify_tasks(self, tasks: List[Dict], 
                               deadline_hours: int = 24,
                               stale_hours: int = 48) -> Dict[str, int]:
        """
        Check all tasks and send notifications as needed
        
        Args:
            tasks: List of tasks to check
            deadline_hours: Hours before deadline to notify
            stale_hours: Hours without update to notify
        
        Returns:
            Dict with counts of notifications sent
        """
        now = datetime.now()
        stats = {
            'deadline': 0,
            'overdue': 0,
            'stale': 0
        }
        
        for task in tasks:
            # Skip completed tasks
            if task.get('status', '').lower() == 'done':
                continue
            
            # Check deadline
            if 'deadline' in task:
                try:
                    deadline = datetime.fromisoformat(task['deadline'])
                    time_until = deadline - now
                    
                    # Overdue
                    if time_until.total_seconds() < 0:
                        if self.notify_task_overdue(task):
                            stats['overdue'] += 1
                    # Approaching deadline
                    elif time_until.total_seconds() < deadline_hours * 3600:
                        if self.notify_task_deadline(task):
                            stats['deadline'] += 1
                except:
                    pass
            
            # Check last update
            if 'last_update' in task:
                try:
                    last_update = datetime.fromisoformat(task['last_update'])
                    hours_since = (now - last_update).total_seconds() / 3600
                    
                    if hours_since > stale_hours:
                        if self.notify_task_stale(task, int(hours_since)):
                            stats['stale'] += 1
                except:
                    pass
        
        return stats
    
    def notify_new_tasks(self, tasks: List[Dict]) -> bool:
        """Notify about newly created tasks"""
        if not tasks:
            return False
        
        if len(tasks) == 1:
            title = "✅ New Task Created"
            message = f"{tasks[0]['title']}\nPriority: {tasks[0]['priority']}"
        else:
            title = f"✅ {len(tasks)} New Tasks Created"
            message = "\n".join([f"• {t['title']}" for t in tasks[:3]])
            if len(tasks) > 3:
                message += f"\n...and {len(tasks) - 3} more"
        
        return self.send_notification(title, message)
