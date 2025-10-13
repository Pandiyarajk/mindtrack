"""
User Manager Module
Handles user authentication, registration, and profile management
"""
import json
import os
import bcrypt
from datetime import datetime
from typing import Optional, Dict
from flask_login import UserMixin


class User(UserMixin):
    """User model for Flask-Login"""
    def __init__(self, user_id: str, username: str, email: str, profile: Dict = None):
        self.id = user_id
        self.username = username
        self.email = email
        self.profile = profile or {}
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'profile': self.profile
        }


class UserManager:
    """Manages user authentication and profiles"""
    
    def __init__(self, users_file='data/users.json'):
        self.users_file = users_file
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Create users file if it doesn't exist"""
        if not os.path.exists(self.users_file):
            os.makedirs(os.path.dirname(self.users_file), exist_ok=True)
            with open(self.users_file, 'w') as f:
                json.dump({"users": []}, f)
    
    def load_users(self) -> Dict:
        """Load users from JSON file"""
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"users": []}
    
    def save_users(self, data: Dict) -> bool:
        """Save users to JSON file"""
        try:
            with open(self.users_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving users: {e}")
            return False
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def register_user(self, username: str, email: str, password: str, full_name: str = "") -> Optional[User]:
        """Register a new user"""
        data = self.load_users()
        
        # Check if username or email already exists
        for user in data['users']:
            if user['username'].lower() == username.lower():
                raise ValueError("Username already exists")
            if user['email'].lower() == email.lower():
                raise ValueError("Email already exists")
        
        # Generate user ID
        user_id = f"user_{len(data['users']) + 1:03d}"
        
        # Create user
        user_data = {
            "id": user_id,
            "username": username,
            "email": email,
            "password_hash": self.hash_password(password),
            "profile": {
                "full_name": full_name,
                "created_at": datetime.now().isoformat(),
                "last_login": None
            }
        }
        
        data['users'].append(user_data)
        self.save_users(data)
        
        # Create user data directory
        self._create_user_directory(user_id)
        
        return User(user_id, username, email, user_data['profile'])
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user with username and password"""
        data = self.load_users()
        
        for user in data['users']:
            if user['username'].lower() == username.lower():
                if self.verify_password(password, user['password_hash']):
                    # Update last login
                    user['profile']['last_login'] = datetime.now().isoformat()
                    self.save_users(data)
                    
                    return User(user['id'], user['username'], user['email'], user['profile'])
                return None
        return None
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get a user by their ID"""
        data = self.load_users()
        
        for user in data['users']:
            if user['id'] == user_id:
                return User(user['id'], user['username'], user['email'], user['profile'])
        return None
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get a user by their username"""
        data = self.load_users()
        
        for user in data['users']:
            if user['username'].lower() == username.lower():
                return User(user['id'], user['username'], user['email'], user['profile'])
        return None
    
    def update_profile(self, user_id: str, profile_updates: Dict) -> bool:
        """Update a user's profile"""
        data = self.load_users()
        
        for user in data['users']:
            if user['id'] == user_id:
                user['profile'].update(profile_updates)
                user['profile']['updated_at'] = datetime.now().isoformat()
                return self.save_users(data)
        return False
    
    def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """Change a user's password"""
        data = self.load_users()
        
        for user in data['users']:
            if user['id'] == user_id:
                if self.verify_password(old_password, user['password_hash']):
                    user['password_hash'] = self.hash_password(new_password)
                    return self.save_users(data)
                return False
        return False
    
    def _create_user_directory(self, user_id: str):
        """Create data directory for user"""
        user_dir = f"data/users/{user_id}"
        os.makedirs(user_dir, exist_ok=True)
        
        # Create initial notes and archive files
        notes_file = f"{user_dir}/notes.json"
        archive_file = f"{user_dir}/archive.json"
        
        if not os.path.exists(notes_file):
            with open(notes_file, 'w') as f:
                json.dump({"notes": []}, f)
        
        if not os.path.exists(archive_file):
            with open(archive_file, 'w') as f:
                json.dump({"archived_notes": []}, f)
    
    def get_user_data_path(self, user_id: str) -> str:
        """Get the data directory path for a user"""
        return f"data/users/{user_id}"
