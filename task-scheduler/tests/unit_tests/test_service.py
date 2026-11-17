import json

import pytest

import service
from constants import HEARTBEAT_TOPIC, TASK_ACK_TOPIC


@pytest.fixture
def scheduler(mocker):
    task_scheduler = service.TaskSchedulerService()
    homeware = mocker.MagicMock()
    mqtt_client = mocker.MagicMock()
    task_scheduler.initialize(homeware, mqtt_client)
    return task_scheduler


def _task(task_id, due_time, asserts=None, target_value=True):
    return {
        "id": task_id,
        "time": due_time,
        "asserts": asserts or [],
        "target": {"device_id": "light-1", "param": "on", "value": target_value},
    }


def test_set_task_adds_it_and_publishes_ack(scheduler):
    task = _task("task-1", 123)
    payload = {"action": "set", **task}

    scheduler._handle_message("tasks", json.dumps(payload))

    assert scheduler.tasks == [payload]
    scheduler.mqtt_client.publish.assert_called_once_with(TASK_ACK_TOPIC, json.dumps(payload))


def test_set_task_with_delta_calculates_absolute_time(scheduler, monkeypatch):
    monkeypatch.setattr(service.time, "time", lambda: 100)
    payload = {"id": "task-1", "action": "set", "delta": 30, "asserts": [], "target": {}}

    scheduler._handle_message("tasks", json.dumps(payload))

    expected_task = {**payload, "time": 130}
    assert scheduler.tasks == [expected_task]
    scheduler.mqtt_client.publish.assert_called_once_with(TASK_ACK_TOPIC, json.dumps(expected_task))


def test_delete_task_removes_matching_task_and_publishes_ack(scheduler):
    scheduler.tasks = [_task("keep", 100), _task("delete-me", 200)]
    payload = {"id": "delete-me", "action": "delete"}

    scheduler._handle_message("tasks", json.dumps(payload))

    assert [task["id"] for task in scheduler.tasks] == ["keep"]
    scheduler.mqtt_client.publish.assert_called_once_with(TASK_ACK_TOPIC, json.dumps(payload))


def test_delete_unknown_task_does_not_publish_ack(scheduler):
    scheduler.tasks = [_task("keep", 100)]

    scheduler._handle_message("tasks", json.dumps({"id": "missing", "action": "delete"}))

    assert len(scheduler.tasks) == 1
    scheduler.mqtt_client.publish.assert_not_called()


def test_heartbeat_processes_due_tasks(scheduler, mocker):
    process_due = mocker.patch.object(scheduler, "_process_due_tasks")

    scheduler._handle_message(HEARTBEAT_TOPIC, "ignored")

    process_due.assert_called_once_with()


def test_process_due_tasks_executes_all_due_tasks_and_keeps_future_tasks(scheduler, monkeypatch):
    monkeypatch.setattr(service.time, "time", lambda: 100)
    scheduler.homeware.get.return_value = "enabled"
    condition = {"device_id": "sensor-1", "param": "state", "value": "enabled"}
    due_one = _task("one", 90, [condition], target_value="first")
    due_two = _task("two", 99, target_value="second")
    future = _task("future", 101)
    scheduler.tasks = [due_one, due_two, future]

    scheduler._process_due_tasks()

    assert [call.args for call in scheduler.homeware.execute.call_args_list] == [
        ("light-1", "on", "first"),
        ("light-1", "on", "second"),
    ]
    scheduler.homeware.get.assert_called_once_with("sensor-1", "state")
    assert scheduler.tasks == [future]


def test_process_due_task_skips_execution_when_assertion_fails(scheduler, monkeypatch):
    monkeypatch.setattr(service.time, "time", lambda: 100)
    scheduler.homeware.get.return_value = "disabled"
    condition = {"device_id": "sensor-1", "param": "state", "value": "enabled"}
    task = _task("conditional", 99, [condition])
    scheduler.tasks = [task]

    scheduler._process_due_tasks()

    scheduler.homeware.get.assert_called_once_with("sensor-1", "state")
    scheduler.homeware.execute.assert_not_called()
    assert scheduler.tasks == []
