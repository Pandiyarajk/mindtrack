import json
from types import SimpleNamespace
from unittest.mock import MagicMock

from modules.task_extractor import TaskExtractor


def _fake_completion(content: str):
    message = SimpleNamespace(content=content)
    choice = SimpleNamespace(message=message)
    return SimpleNamespace(choices=[choice])


def test_no_api_key_uses_fallback_extraction():
    extractor = TaskExtractor(api_key=None)
    tasks = extractor.extract_tasks("Please call the vendor urgently about the invoice")

    assert len(tasks) == 1
    assert tasks[0]["priority"] == "High"
    assert tasks[0]["status"] == "Pending"


def test_fallback_extraction_ignores_notes_without_action_words():
    extractor = TaskExtractor(api_key=None)
    tasks = extractor.extract_tasks("Just a random thought with no actions")
    assert tasks == []


def test_fallback_priority_detection():
    extractor = TaskExtractor(api_key=None)
    assert extractor._simple_priority("this is urgent")["priority"] == "High"
    assert extractor._simple_priority("do this eventually")["priority"] == "Low"
    assert extractor._simple_priority("regular task")["priority"] == "Medium"


def test_extract_tasks_uses_openai_client_when_key_present():
    extractor = TaskExtractor(api_key="test-key")
    payload = json.dumps([{"title": "Follow up with John", "priority": "High",
                            "deadline": "2025-10-14T18:00:00", "color": "red"}])
    extractor.client.chat.completions.create = MagicMock(return_value=_fake_completion(payload))

    tasks = extractor.extract_tasks("Follow up with John about the proposal")

    assert len(tasks) == 1
    assert tasks[0]["title"] == "Follow up with John"
    assert tasks[0]["status"] == "Pending"
    assert "id" in tasks[0]
    extractor.client.chat.completions.create.assert_called_once()


def test_extract_tasks_falls_back_when_openai_call_raises():
    extractor = TaskExtractor(api_key="test-key")
    extractor.client.chat.completions.create = MagicMock(side_effect=RuntimeError("boom"))

    tasks = extractor.extract_tasks("Call the client urgently")

    assert len(tasks) == 1
    assert tasks[0]["priority"] == "High"
