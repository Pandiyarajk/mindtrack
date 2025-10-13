"""
Task Extractor Module
Uses OpenAI API to extract action items from notes
"""
import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import openai


class TaskExtractor:
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize TaskExtractor with OpenAI API key
        If no key provided, tries to get from environment variable OPENAI_API_KEY
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if self.api_key:
            openai.api_key = self.api_key
    
    def extract_tasks(self, note_text: str) -> List[Dict]:
        """
        Extract actionable tasks from note text using OpenAI
        Returns a list of tasks with title, priority, and deadline
        """
        if not self.api_key:
            # Fallback to simple extraction if no API key
            return self._simple_extract(note_text)
        
        try:
            prompt = f"""
Extract actionable tasks from the following note and return them as a JSON array.
For each task, provide:
- title: A clear, concise task title
- priority: High, Medium, or Low
- deadline: Estimate a reasonable deadline based on the note (ISO format)
- color: red for High, orange for Medium, green for Low

Note: {note_text}

Return ONLY a valid JSON array with no additional text. Example format:
[{{"title": "Follow up with John", "priority": "High", "deadline": "2025-10-14T18:00:00", "color": "red"}}]
"""
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that extracts actionable tasks from notes. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse JSON response
            tasks_data = json.loads(content)
            
            # Add IDs and status
            tasks = []
            for i, task in enumerate(tasks_data):
                task['id'] = f"task_{datetime.now().strftime('%Y%m%d%H%M%S')}_{i}"
                task['status'] = 'Pending'
                task['last_update'] = datetime.now().isoformat()
                tasks.append(task)
            
            return tasks
            
        except Exception as e:
            print(f"Error extracting tasks with OpenAI: {e}")
            # Fallback to simple extraction
            return self._simple_extract(note_text)
    
    def _simple_extract(self, note_text: str) -> List[Dict]:
        """
        Simple fallback task extraction without AI
        Looks for action words and creates basic tasks
        """
        action_words = ['follow up', 'call', 'email', 'send', 'complete', 'finish', 
                       'review', 'prepare', 'schedule', 'meet', 'contact', 'submit']
        
        tasks = []
        lower_text = note_text.lower()
        
        # Check if note contains action words
        has_action = any(word in lower_text for word in action_words)
        
        if has_action:
            # Create a single task from the note
            task_id = f"task_{datetime.now().strftime('%Y%m%d%H%M%S')}_0"
            
            # Default deadline: 3 days from now
            deadline = (datetime.now() + timedelta(days=3)).isoformat()
            
            # Determine priority based on keywords
            priority = "Medium"
            color = "orange"
            
            if any(word in lower_text for word in ['urgent', 'asap', 'immediately', 'critical']):
                priority = "High"
                color = "red"
            elif any(word in lower_text for word in ['when possible', 'eventually', 'someday']):
                priority = "Low"
                color = "green"
            
            task = {
                "id": task_id,
                "title": note_text[:100],  # Use first 100 chars as title
                "priority": priority,
                "status": "Pending",
                "deadline": deadline,
                "color": color,
                "last_update": datetime.now().isoformat()
            }
            tasks.append(task)
        
        return tasks
    
    def suggest_priority(self, task_title: str) -> Dict[str, str]:
        """
        Suggest priority for a task
        Returns dict with priority and color
        """
        if not self.api_key:
            return self._simple_priority(task_title)
        
        try:
            prompt = f"""
Analyze this task and suggest a priority level (High, Medium, or Low).
Consider urgency and importance.

Task: {task_title}

Return ONLY a JSON object with format: {{"priority": "High", "color": "red"}}
Colors: red for High, orange for Medium, green for Low
"""
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that prioritizes tasks. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=50
            )
            
            content = response.choices[0].message.content.strip()
            result = json.loads(content)
            return result
            
        except Exception as e:
            print(f"Error suggesting priority: {e}")
            return self._simple_priority(task_title)
    
    def _simple_priority(self, task_title: str) -> Dict[str, str]:
        """Simple priority suggestion without AI"""
        lower_title = task_title.lower()
        
        if any(word in lower_title for word in ['urgent', 'asap', 'critical', 'immediately']):
            return {"priority": "High", "color": "red"}
        elif any(word in lower_title for word in ['when possible', 'eventually', 'someday']):
            return {"priority": "Low", "color": "green"}
        else:
            return {"priority": "Medium", "color": "orange"}
