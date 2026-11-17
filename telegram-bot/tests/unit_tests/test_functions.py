import requests

import functions

def test_get_public_ip_returns_response_text(mocker, monkeypatch):
    get = mocker.MagicMock(return_value=mocker.MagicMock(text="203.0.113.10"))
    monkeypatch.setattr(functions.requests, "get", get)

    assert functions.getPublicIP("https://ip.test") == "203.0.113.10"
    get.assert_called_once_with("https://ip.test", timeout=functions.REQUEST_TIMEOUT)


def test_get_public_ip_returns_fail_on_connection_error(mocker, monkeypatch, caplog):
    get = mocker.MagicMock(side_effect=requests.ConnectionError("offline"))
    monkeypatch.setattr(functions.requests, "get", get)

    assert functions.getPublicIP("https://ip.test") == "Fail"
    assert "Fail to get public IP" in caplog.text


def test_get_homeware_test_checks_scene_state_and_request_details(mocker, monkeypatch):
    response = mocker.MagicMock(status_code=200)
    response.json.return_value = {"enable": True}
    get = mocker.MagicMock(return_value=response)
    monkeypatch.setattr(functions.requests, "get", get)

    assert functions.getHomewareTest("https://homeware.test", "api-key") is True
    get.assert_called_once_with(
        "https://homeware.test/api/devices/scene_dim/states",
        headers={"Authorization": "bearer api-key"},
        timeout=functions.REQUEST_TIMEOUT,
    )


def test_get_homeware_test_returns_false_for_unavailable_api(mocker, monkeypatch):
    monkeypatch.setattr(functions.requests, "get", mocker.MagicMock(return_value=mocker.MagicMock(status_code=503)))

    assert functions.getHomewareTest("https://homeware.test", "api-key") is False


def test_download_video_uploads_mp4_and_returns_encoded_url(tmp_path, mocker, monkeypatch):
    monkeypatch.chdir(tmp_path)
    video = mocker.MagicMock()
    download = video.streams.filter.return_value.order_by.return_value.desc.return_value.first.return_value.download
    download.side_effect = lambda: (tmp_path / "my video.mp4").write_text("video")
    monkeypatch.setattr(functions, "YouTube", mocker.MagicMock(return_value=video))
    storage_client = mocker.MagicMock()

    urls = functions.downloadYouTubeVideo("https://youtu.be/id", storage_client, "video-bucket")

    assert urls == ["https://storage.cloud.google.com/video-bucket/my%20video.mp4"]
    storage_client.bucket.assert_called_once_with("video-bucket")
    storage_client.bucket.return_value.blob.assert_called_once_with("my video.mp4")
    storage_client.bucket.return_value.blob.return_value.upload_from_filename.assert_called_once_with("my video.mp4")
    assert not (tmp_path / "my video.mp4").exists()


def test_download_video_returns_empty_list_if_download_fails(tmp_path, mocker, monkeypatch, caplog):
    monkeypatch.chdir(tmp_path)
    video = mocker.MagicMock()
    video.streams.filter.return_value.order_by.return_value.desc.return_value.first.return_value.download.side_effect = RuntimeError(
        "download failed"
    )
    monkeypatch.setattr(functions, "YouTube", mocker.MagicMock(return_value=video))

    assert functions.downloadYouTubeVideo("https://youtu.be/id", mocker.MagicMock(), "video-bucket") == []
    assert "Fail to download YouTube video" in caplog.text
