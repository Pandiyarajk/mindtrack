"""
Note Handler Module
Manages notes and tasks in JSON storage
"""
import logging
from datetime import datetime
from typing import List, Dict, Optional

from .json_store import JSONStore

logger = logging.getLogger(__name__)


class NoteHandler:
    def __init__(self, notes_file='data/notes.json', archive_file='data/archive.json', user_id=None):
        # If user_id is provided, use user-specific paths
        if user_id:
            self.notes_file = f'data/users/{user_id}/notes.json'
            self.archive_file = f'data/users/{user_id}/archive.json'
        else:
            self.notes_file = notes_file
            self.archive_file = archive_file

        self._notes_store = JSONStore(self.notes_file, lambda: {"notes": []})
        self._archive_store = JSONStore(self.archive_file, lambda: {"archived_notes": []})

    def load_notes(self) -> Dict:
        """Load notes from JSON file"""
        return self._notes_store.read()

    def save_notes(self, data: Dict) -> bool:
        """Save notes to JSON file"""
        return self._notes_store.write(data)

    def add_note(self, text: str, tasks: List[Dict] = None) -> Dict:
        """Add a new note with optional tasks"""
        with self._notes_store.modify() as data:
            note_id = f"note_{len(data['notes']) + 1:03d}"

            note = {
                "id": note_id,
                "text": text,
                "date_created": datetime.now().isoformat(),
                "tasks": tasks or []
            }

            data['notes'].append(note)

        return note

    def get_note(self, note_id: str) -> Optional[Dict]:
        """Get a specific note by ID"""
        data = self.load_notes()
        for note in data['notes']:
            if note['id'] == note_id:
                return note
        return None

    def update_note(self, note_id: str, updates: Dict) -> bool:
        """Update a note"""
        with self._notes_store.modify() as data:
            for note in data['notes']:
                if note['id'] == note_id:
                    note.update(updates)
                    return True
            return False

    def delete_note(self, note_id: str) -> bool:
        """Delete a note"""
        with self._notes_store.modify() as data:
            data['notes'] = [n for n in data['notes'] if n['id'] != note_id]
        return True

    def get_all_tasks(self) -> List[Dict]:
        """Get all tasks from all notes"""
        data = self.load_notes()
        tasks = []
        for note in data['notes']:
            for task in note.get('tasks', []):
                task['note_id'] = note['id']
                task['note_text'] = note['text']
                tasks.append(task)
        return tasks

    def update_task(self, task_id: str, updates: Dict) -> bool:
        """Update a specific task"""
        with self._notes_store.modify() as data:
            for note in data['notes']:
                for task in note.get('tasks', []):
                    if task['id'] == task_id:
                        task.update(updates)
                        task['last_update'] = datetime.now().isoformat()
                        return True
            return False

    def archive_note(self, note_id: str) -> bool:
        """Archive a note: move it from the notes file into the archive file.

        These are two separate JSONStore-guarded writes, not one atomic
        transaction -- a crash between them could leave a note in both (or
        neither) file. That's a pre-existing limitation, unchanged here.
        """
        note = self.get_note(note_id)
        if not note:
            return False

        note = dict(note)
        note['archived_date'] = datetime.now().isoformat()

        with self._archive_store.modify() as archive:
            archive['archived_notes'].append(note)

        return self.delete_note(note_id)

    def get_task(self, task_id: str) -> Optional[Dict]:
        """Get a specific task by ID"""
        tasks = self.get_all_tasks()
        for task in tasks:
            if task['id'] == task_id:
                return task
        return None
