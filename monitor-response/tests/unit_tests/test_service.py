from types import SimpleNamespace

import service


def make_settings():
    return SimpleNamespace(
        response_test_trigger_topic="trigger/topic",
        response_test_response_topic="response/topic",
        response_ddbb="project.dataset.measurements",
    )


def test_trigger_starts_measurement_and_does_not_write_to_bigquery(mocker, monkeypatch):
    bigquery = mocker.MagicMock()
    monitor = service.MonitorResponseService(make_settings(), bigquery)
    monkeypatch.setattr(service.time, "perf_counter", lambda: 12.5)

    monitor._handle_message("trigger/topic", b"start")

    assert monitor.pending_measurement == 12.5
    bigquery.query.assert_not_called()


def test_response_without_trigger_is_ignored(mocker, monkeypatch):
    bigquery = mocker.MagicMock()
    monitor = service.MonitorResponseService(make_settings(), bigquery)
    monkeypatch.setattr(service.time, "perf_counter", lambda: 20)

    monitor._handle_message("response/topic", b"response")

    assert monitor.pending_measurement is None
    bigquery.query.assert_not_called()


def test_response_writes_elapsed_time_and_waits_for_query_job(mocker, monkeypatch):
    bigquery = mocker.MagicMock()
    query_job = bigquery.query.return_value
    monitor = service.MonitorResponseService(make_settings(), bigquery)
    clock_values = iter([10.0, 10.1239])
    monkeypatch.setattr(service.time, "perf_counter", lambda: next(clock_values))
    monkeypatch.setattr(service.time, "time", lambda: 1700.9)

    monitor._handle_message("trigger/topic", b"trigger")
    monitor._handle_message("response/topic", b"response")

    query = bigquery.query.call_args.args[0]
    assert "INSERT INTO project.dataset.measurements" in query
    assert '(time, trigger, response, duration)' in query
    assert '(1700,"trigger/topic","response/topic",123)' in query
    query_job.result.assert_called_once_with()
    assert monitor.pending_measurement is None


def test_second_trigger_restarts_pending_measurement(mocker, monkeypatch):
    bigquery = mocker.MagicMock()
    monitor = service.MonitorResponseService(make_settings(), bigquery)
    clock_values = iter([1.0, 2.0])
    monkeypatch.setattr(service.time, "perf_counter", lambda: next(clock_values))

    monitor._handle_message("trigger/topic", b"first")
    monitor._handle_message("trigger/topic", b"second")

    assert monitor.pending_measurement == 2.0
    bigquery.query.assert_not_called()


def test_unrelated_topic_does_not_change_pending_measurement(mocker, monkeypatch):
    bigquery = mocker.MagicMock()
    monitor = service.MonitorResponseService(make_settings(), bigquery)
    monitor.pending_measurement = 7.0
    monkeypatch.setattr(service.time, "perf_counter", lambda: 8.0)

    monitor._handle_message("other/topic", b"ignored")

    assert monitor.pending_measurement == 7.0
    bigquery.query.assert_not_called()
