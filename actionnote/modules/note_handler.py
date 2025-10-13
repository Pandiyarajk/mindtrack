"""
Note Handler Module
Manages notes and tasks in JSON storage
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Optional


class NoteHandler:
    def __init__(self, notes_file='data/notes.json', archive_file='data/archive.json', user_id=None):
        # If user_id is provided, use user-specific paths
        if user_id:
            self.notes_file = f'data/users/{user_id}/notes.json'
            self.archive_file = f'data/users/{user_id}/archive.json'
        else:
            self.notes_file = notes_file
            self.archive_file = archive_file
        self._ensure_files_exist()
    
    def _ensure_files_exist(self):
        """Create data files if they don't exist"""
        for file_path in [self.notes_file, self.archive_file]:
            if not os.path.exists(file_path):
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'w') as f:
                    if 'archive' in file_path:
                        json.dump({"archived_notes": []}, f)
                    else:
                        json.dump({"notes": []}, f)
    
    def load_notes(self) -> Dict:
        """Load notes from JSON file"""
        try:
            with open(self.notes_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"notes": []}
    
    def save_notes(self, data: Dict) -> bool:
        """Save notes to JSON file"""
        try:
            with open(self.notes_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving notes: {e}")
            return False
    
    def add_note(self, text: str, tasks: List[Dict] = None) -> Dict:
        """Add a new note with optional tasks"""
        data = self.load_notes()
        
        # Generate note ID
        note_id = f"note_{len(data['notes']) + 1:03d}"
        
        note = {
            "id": note_id,
            "text": text,
            "date_created": datetime.now().isoformat(),
            "tasks": tasks or []
        }
        
        data['notes'].append(note)
        self.save_notes(data)
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
        data = self.load_notes()
        for i, note in enumerate(data['notes']):
            if note['id'] == note_id:
                data['notes'][i].update(updates)
                return self.save_notes(data)
        return False
    
    def delete_note(self, note_id: str) -> bool:
        """Delete a note"""
        data = self.load_notes()
        data['notes'] = [n for n in data['notes'] if n['id'] != note_id]
        return self.save_notes(data)
    
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
        data = self.load_notes()
        for note in data['notes']:
            for i, task in enumerate(note.get('tasks', [])):
                if task['id'] == task_id:
                    note['tasks'][i].update(updates)
                    note['tasks'][i]['last_update'] = datetime.now().isoformat()
                    return self.save_notes(data)
        return False
    
    def archive_note(self, note_id: str) -> bool:
        """Archive a note"""
        note = self.get_note(note_id)
        if not note:
            return False
        
        # Load archive
        try:
            with open(self.archive_file, 'r') as f:
                archive = json.load(f)
        except:
            archive = {"archived_notes": []}
        
        # Add to archive
        note['archived_date'] = datetime.now().isoformat()
        archive['archived_notes'].append(note)
        
        # Save archive
        with open(self.archive_file, 'w') as f:
            json.dump(archive, f, indent=2)
        
        # Delete from notes
        return self.delete_note(note_id)
    
    def get_task(self, task_id: str) -> Optional[Dict]:
        """Get a specific task by ID"""
        tasks = self.get_all_tasks()
        for task in tasks:
            if task['id'] == task_id:
                return task
        return None
