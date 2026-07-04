"""
ActionNote Flask Application
A note-taking app with AI-powered task extraction and management
"""
import logging
import os
import secrets
from datetime import datetime

from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf import CSRFProtect
from werkzeug.exceptions import HTTPException

from modules.note_handler import NoteHandler
from modules.task_extractor import TaskExtractor
from modules.notifier import Notifier
from modules.emailer import Emailer
from modules.scheduler import TaskScheduler
from modules.user_manager import UserManager
from modules.validators import is_valid_password

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s: %(message)s')
logger = logging.getLogger(__name__)


def _get_secret_key() -> str:
    """Use SECRET_KEY from the environment if set; otherwise generate one
    and persist it under instance/ so sessions survive process restarts."""
    key = os.getenv('SECRET_KEY')
    if key:
        return key

    os.makedirs('instance', exist_ok=True)
    key_path = os.path.join('instance', 'secret_key')
    if os.path.exists(key_path):
        with open(key_path, 'r') as f:
            return f.read().strip()

    key = secrets.token_hex(32)
    with open(key_path, 'w') as f:
        f.write(key)
    os.chmod(key_path, 0o600)
    logger.warning(
        "SECRET_KEY not set; using an auto-generated dev key persisted at "
        "instance/secret_key. Set the SECRET_KEY environment variable for production."
    )
    return key


# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = _get_secret_key()

# CSRF protection for all forms and API requests
csrf = CSRFProtect(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# Initialize user manager
user_manager = UserManager(users_file='data/users.json')


@login_manager.user_loader
def load_user(user_id):
    return user_manager.get_user_by_id(user_id)


# Initialize shared modules (user-specific instances created per request)
task_extractor = TaskExtractor()
notifier = Notifier()
emailer = Emailer()

# Configuration
CONFIG = {
    'recipient_email': os.getenv('NOTIFICATION_EMAIL'),
    'scheduler_enabled': os.getenv('SCHEDULER_ENABLED', 'true').lower() == 'true'
}


def get_user_note_handler():
    """Get note handler for current user"""
    if current_user.is_authenticated:
        return NoteHandler(user_id=current_user.id)
    return None


@app.errorhandler(Exception)
def handle_unexpected_error(e):
    """Log unexpected errors server-side and avoid leaking internals to clients.
    HTTPExceptions (404, 400, CSRF errors, etc.) already carry the right
    status/message and are passed through unchanged."""
    if isinstance(e, HTTPException):
        return e
    logger.exception("Unhandled exception while handling %s", request.path)
    return jsonify({'error': 'Internal server error'}), 500


# ==================== Authentication Routes ====================

@app.route('/')
def index():
    """Home page - redirect based on authentication"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            return render_template('login.html', error='Please provide username and password')

        user = user_manager.authenticate_user(username, password)
        if user:
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid username or password')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        full_name = request.form.get('full_name', '').strip()

        # Validation
        if not all([username, email, password, confirm_password]):
            return render_template('register.html', error='All fields are required')

        if password != confirm_password:
            return render_template('register.html', error='Passwords do not match')

        if not is_valid_password(password):
            return render_template(
                'register.html',
                error='Password must be at least 8 characters and include a letter and a number'
            )

        try:
            user_manager.register_user(username, email, password, full_name)
            return redirect(url_for('login', message='Registration successful! Please log in.'))
        except ValueError as e:
            return render_template('register.html', error=str(e))

    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    """Logout user"""
    logout_user()
    return redirect(url_for('login'))


@app.route('/profile')
@login_required
def profile():
    """User profile page"""
    return render_template('profile.html', user=current_user)


@app.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    """Update user profile"""
    full_name = request.form.get('full_name', '').strip()

    if not full_name:
        return render_template('profile.html', user=current_user, error='Full name is required')

    success = user_manager.update_profile(current_user.id, {'full_name': full_name})

    if success:
        # Reload user to get updated profile
        updated_user = user_manager.get_user_by_id(current_user.id)
        return render_template('profile.html', user=updated_user, message='Profile updated successfully')
    else:
        return render_template('profile.html', user=current_user, error='Failed to update profile')


@app.route('/profile/change-password', methods=['POST'])
@login_required
def change_password():
    """Change user password"""
    old_password = request.form.get('old_password', '')
    new_password = request.form.get('new_password', '')
    confirm_password = request.form.get('confirm_password', '')

    if not all([old_password, new_password, confirm_password]):
        return render_template('profile.html', user=current_user, error='All password fields are required')

    if new_password != confirm_password:
        return render_template('profile.html', user=current_user, error='New passwords do not match')

    if not is_valid_password(new_password):
        return render_template(
            'profile.html', user=current_user,
            error='Password must be at least 8 characters and include a letter and a number'
        )

    success = user_manager.change_password(current_user.id, old_password, new_password)

    if success:
        return render_template('profile.html', user=current_user, message='Password changed successfully')
    else:
        return render_template('profile.html', user=current_user, error='Current password is incorrect')


# ==================== Application Routes ====================


@app.route('/dashboard')
@login_required
def dashboard():
    """Task dashboard page"""
    note_handler = get_user_note_handler()
    tasks = note_handler.get_all_tasks()

    # Sort by priority and deadline
    priority_order = {'High': 0, 'Medium': 1, 'Low': 2}
    tasks_sorted = sorted(
        tasks,
        key=lambda t: (
            priority_order.get(t.get('priority', 'Medium'), 1),
            t.get('deadline', '9999-12-31')
        )
    )

    # Calculate statistics
    stats = {
        'total': len(tasks),
        'pending': len([t for t in tasks if t['status'] == 'Pending']),
        'in_progress': len([t for t in tasks if t['status'] == 'In Progress']),
        'done': len([t for t in tasks if t['status'] == 'Done']),
        'high_priority': len([t for t in tasks if t['priority'] == 'High']),
    }

    return render_template('dashboard.html', tasks=tasks_sorted, stats=stats)


@app.route('/notes')
@login_required
def notes_page():
    """Notes management page"""
    note_handler = get_user_note_handler()
    data = note_handler.load_notes()
    notes = data.get('notes', [])

    # Sort by most recent first
    notes_sorted = sorted(
        notes,
        key=lambda n: n.get('date_created', ''),
        reverse=True
    )

    return render_template('notes.html', notes=notes_sorted)


@app.route('/add_note')
@login_required
def add_note_page():
    """Add note page"""
    return render_template('add_note.html')


@app.route('/api/notes', methods=['GET'])
@login_required
def get_notes():
    """API: Get all notes"""
    note_handler = get_user_note_handler()
    data = note_handler.load_notes()
    return jsonify(data)


@app.route('/api/notes', methods=['POST'])
@login_required
def create_note():
    """API: Create a new note and extract tasks"""
    note_handler = get_user_note_handler()
    data = request.get_json()
    note_text = data.get('text', '').strip()

    if not note_text:
        return jsonify({'error': 'Note text is required'}), 400

    # Extract tasks using AI
    tasks = task_extractor.extract_tasks(note_text)

    # Create note with tasks
    note = note_handler.add_note(note_text, tasks)

    # Send notification about new tasks
    if tasks:
        notifier.notify_new_tasks(tasks)

    return jsonify({
        'success': True,
        'note': note,
        'tasks_created': len(tasks)
    })


@app.route('/api/tasks', methods=['GET'])
@login_required
def get_tasks():
    """API: Get all tasks"""
    note_handler = get_user_note_handler()
    tasks = note_handler.get_all_tasks()
    return jsonify({'tasks': tasks})


@app.route('/api/tasks/manual', methods=['POST'])
@login_required
def create_manual_task():
    """API: Create a manual task without requiring a note"""
    note_handler = get_user_note_handler()
    data = request.get_json()
    title = data.get('title', '').strip()
    priority = data.get('priority', 'Medium')
    deadline = data.get('deadline')
    description = data.get('description', '').strip()

    if not title:
        return jsonify({'error': 'Task title is required'}), 400

    if priority not in ['High', 'Medium', 'Low']:
        return jsonify({'error': 'Invalid priority level'}), 400

    # Create task object
    task = {
        'id': f"task_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        'title': title,
        'priority': priority,
        'status': 'Pending',
        'deadline': deadline,
        'color': {'High': 'red', 'Medium': 'orange', 'Low': 'green'}.get(priority, 'orange'),
        'last_update': datetime.now().isoformat(),
        'note_text': description if description else None
    }

    # Save task to note handler
    try:
        note_handler.add_task(task)
        return jsonify({'success': True, 'task': task})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/tasks/<task_id>', methods=['PUT'])
@login_required
def update_task(task_id):
    """API: Update a task"""
    note_handler = get_user_note_handler()
    data = request.get_json()
    success = note_handler.update_task(task_id, data)

    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Task not found'}), 404


@app.route('/api/tasks/<task_id>/status', methods=['PUT'])
@login_required
def update_task_status(task_id):
    """API: Update task status"""
    note_handler = get_user_note_handler()
    data = request.get_json()
    status = data.get('status')

    if status not in ['Pending', 'In Progress', 'Done']:
        return jsonify({'error': 'Invalid status'}), 400

    success = note_handler.update_task(task_id, {'status': status})

    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Task not found'}), 404


@app.route('/api/notes/<note_id>', methods=['PUT'])
@login_required
def update_note(note_id):
    """API: Update a note"""
    note_handler = get_user_note_handler()
    data = request.get_json()
    text = data.get('text', '').strip()

    if not text:
        return jsonify({'error': 'Note text is required'}), 400

    success = note_handler.update_note(note_id, {'text': text})

    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Note not found'}), 404


@app.route('/api/notes/<note_id>', methods=['DELETE'])
@login_required
def delete_note(note_id):
    """API: Delete a note"""
    note_handler = get_user_note_handler()
    success = note_handler.delete_note(note_id)

    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Note not found'}), 404


@app.route('/api/notes/<note_id>/archive', methods=['POST'])
@login_required
def archive_note(note_id):
    """API: Archive a note"""
    note_handler = get_user_note_handler()
    success = note_handler.archive_note(note_id)

    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Note not found'}), 404


@app.route('/api/config', methods=['GET'])
@login_required
def get_config():
    """API: Get application configuration"""
    return jsonify({
        'openai_enabled': bool(task_extractor.api_key),
        'email_enabled': emailer.enabled,
        'notifications_enabled': notifier.PLYER_AVAILABLE,
        'scheduler_enabled': CONFIG['scheduler_enabled']
    })


@app.route('/settings')
@login_required
def settings():
    """Settings page"""
    config = {
        'openai_enabled': bool(task_extractor.api_key),
        'email_enabled': emailer.enabled,
        'notifications_enabled': True,  # Desktop notifications
        'scheduler_enabled': CONFIG['scheduler_enabled'],
        'recipient_email': CONFIG['recipient_email'] or ''
    }
    return render_template('settings.html', config=config)


if __name__ == '__main__':
    scheduler = None
    if CONFIG['scheduler_enabled']:
        scheduler = TaskScheduler(user_manager, notifier, emailer)
        scheduler.set_recipient_email(CONFIG['recipient_email'])
        scheduler.start()

    try:
        # Run Flask app
        print("=" * 50)
        print("ActionNote MVP - Starting with User Authentication...")
        print("=" * 50)
        print(f"OpenAI API: {'[YES] Enabled' if task_extractor.api_key else '[NO] Disabled (using fallback)'}")
        print(f"Email: {'[YES] Enabled' if emailer.enabled else '[NO] Disabled'}")
        print(f"Desktop Notifications: {'[YES] Enabled' if notifier.PLYER_AVAILABLE else '[NO] Disabled'}")
        print(f"Scheduler: {'[YES] Enabled' if scheduler else '[NO] Disabled'}")
        print("=" * 50)

        flask_host = os.getenv('FLASK_HOST', '127.0.0.1')
        flask_debug = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
        print(f"\nAccess the app at: http://{flask_host}:5000")
        print("Please register a new account or login to continue.")
        print("\nPress Ctrl+C to stop\n")

        app.run(debug=flask_debug, host=flask_host, port=5000, use_reloader=False)

    except KeyboardInterrupt:
        print("\n\nShutting down ActionNote...")
        print("Goodbye!")
    finally:
        if scheduler:
            scheduler.stop()
