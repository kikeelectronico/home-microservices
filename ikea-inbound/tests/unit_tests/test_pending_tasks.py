import pending_tasks


def test_process_executes_and_removes_tasks_older_than_ten_seconds(mocker, monkeypatch):
    homeware = mocker.MagicMock()
    tasks = {
        "outlet-1-isRunning": {
            "time": 89,
            "device_id": "outlet-1",
            "param": "isRunning",
            "value": False,
        }
    }
    monkeypatch.setattr(pending_tasks.time, "time", lambda: 100)

    pending_tasks.process(homeware, tasks)

    homeware.execute.assert_called_once_with("outlet-1", "isRunning", False)
    assert tasks == {}


def test_process_keeps_tasks_that_have_not_expired(mocker, monkeypatch):
    homeware = mocker.MagicMock()
    tasks = {
        "outlet-1-isRunning": {
            "time": 90,
            "device_id": "outlet-1",
            "param": "isRunning",
            "value": False,
        }
    }
    monkeypatch.setattr(pending_tasks.time, "time", lambda: 100)

    pending_tasks.process(homeware, tasks)

    homeware.execute.assert_not_called()
    assert "outlet-1-isRunning" in tasks
