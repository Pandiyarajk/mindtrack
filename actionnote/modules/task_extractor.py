"""
Task Extractor Module
Uses OpenAI API to extract action items from notes
"""
import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from openai import OpenAI


class TaskExtractor:
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize TaskExtractor with OpenAI API key
        If no key provided, tries to get from environment variable OPENAI_API_KEY
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

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

            response = self.client.chat.completions.create(
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
        Improved fallback task extraction without AI
        Looks for action words, patterns, and creates contextual tasks
        """
        action_words = {
            'high_action': ['must', 'need to', 'have to', 'should', 'do', 'make', 'create', 'build', 'fix', 'resolve'],
            'communication': ['follow up', 'call', 'email', 'contact', 'reach out', 'message', 'notify', 'text', 'reply', 'respond'],
            'review': ['review', 'check', 'verify', 'audit', 'inspect', 'examine', 'approve', 'validate', 'test'],
            'planning': ['schedule', 'plan', 'organize', 'arrange', 'prepare', 'setup', 'configure', 'install'],
            'execution': ['complete', 'finish', 'execute', 'implement', 'deploy', 'launch', 'submit', 'publish', 'release'],
            'documentation': ['document', 'write', 'update', 'record', 'log', 'note', 'draft'],
            'research': ['research', 'investigate', 'explore', 'analyze', 'study', 'learn']
        }

        tasks = []
        lower_text = note_text.lower()

        # Check if note contains action words
        all_action_words = []
        for category, words in action_words.items():
            all_action_words.extend(words)

        has_action = any(word in lower_text for word in all_action_words)

        if has_action:
            # Split into sentences to extract more specific tasks
            sentences = [s.strip() for s in note_text.split('.') if s.strip()]

            task_count = 0
            for sentence in sentences:
                lower_sentence = sentence.lower()

                # Check if sentence contains action words
                if any(word in lower_sentence for word in all_action_words):
                    # Create task from this sentence
                    task_id = f"task_{datetime.now().strftime('%Y%m%d%H%M%S')}_{task_count}"

                    # Determine deadline based on keywords
                    deadline_days = 3  # default
                    if any(word in lower_sentence for word in ['today', 'tonight']):
                        deadline_days = 0
                    elif any(word in lower_sentence for word in ['tomorrow', 'next day']):
                        deadline_days = 1
                    elif any(word in lower_sentence for word in ['this week', 'asap']):
                        deadline_days = 2
                    elif any(word in lower_sentence for word in ['next week']):
                        deadline_days = 7

                    deadline = (datetime.now() + timedelta(days=deadline_days)).isoformat()

                    # Determine priority based on keywords
                    priority = "Medium"
                    color = "orange"

                    if any(word in lower_sentence for word in ['urgent', 'asap', 'immediately', 'critical', 'emergency', 'important', 'must', 'high priority']):
                        priority = "High"
                        color = "red"
                    elif any(word in lower_sentence for word in ['when possible', 'eventually', 'someday', 'low priority', 'optional']):
                        priority = "Low"
                        color = "green"

                    # Use first 100 chars of sentence as title, or full sentence if shorter
                    title = sentence[:100] if len(sentence) > 100 else sentence

                    task = {
                        "id": task_id,
                        "title": title,
                        "priority": priority,
                        "status": "Pending",
                        "deadline": deadline,
                        "color": color,
                        "last_update": datetime.now().isoformat()
                    }
                    tasks.append(task)
                    task_count += 1

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

            response = self.client.chat.completions.create(
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
