import json
import threading

from modules.json_store import JSONStore


def test_creates_default_file_if_missing(tmp_path):
    path = tmp_path / "store.json"
    store = JSONStore(str(path), lambda: {"items": []})

    assert path.exists()
    assert store.read() == {"items": []}


def test_write_then_read_round_trips(tmp_path):
    store = JSONStore(str(tmp_path / "store.json"), lambda: {"items": []})
    store.write({"items": [1, 2, 3]})
    assert store.read() == {"items": [1, 2, 3]}


def test_recovers_from_corrupt_file(tmp_path):
    path = tmp_path / "store.json"
    path.write_text("not valid json")
    store = JSONStore(str(path), lambda: {"items": []})
    assert store.read() == {"items": []}


def test_write_does_not_leave_temp_files_on_disk(tmp_path):
    store = JSONStore(str(tmp_path / "store.json"), lambda: {"items": []})
    store.write({"items": [1]})

    leftovers = [p for p in tmp_path.iterdir() if p.name.startswith(".tmp_")]
    assert leftovers == []


def test_modify_holds_lock_across_read_and_write(tmp_path):
    store = JSONStore(str(tmp_path / "counter.json"), lambda: {"count": 0})

    def increment():
        for _ in range(50):
            with store.modify() as data:
                data["count"] += 1

    threads = [threading.Thread(target=increment) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert store.read()["count"] == 200


def test_modify_does_not_write_when_body_raises(tmp_path):
    path = tmp_path / "store.json"
    store = JSONStore(str(path), lambda: {"items": []})
    store.write({"items": ["original"]})

    class Boom(Exception):
        pass

    try:
        with store.modify() as data:
            data["items"].append("should-not-persist")
            raise Boom()
    except Boom:
        pass

    with open(path) as f:
        assert json.load(f) == {"items": ["original"]}
