import pytest
import requests

import water


HTML_PAGE = b"""
<div id="index_bodycenter">
  <div></div>
  <div>
    <div></div>
    <div>
      <div></div>
      <div></div>
      <div>
        <div><strong>Actualizado (16/11/2026)</strong></div>
        <div></div>
        <div></div>
        <div><strong>72,5</strong></div>
      </div>
    </div>
  </div>
</div>
"""


def test_get_water_parses_level_and_update_date(mocker, monkeypatch):
    get = mocker.MagicMock(return_value=mocker.MagicMock(status_code=200, content=HTML_PAGE))
    monkeypatch.setattr(water.requests, "get", get)

    assert water.getWater() == {"level": 72.5, "last_update": "16/11/2026"}
    get.assert_called_once_with(water.WATER_URL, timeout=water.REQUEST_TIMEOUT)


def test_get_water_returns_none_for_http_error(mocker, monkeypatch, caplog):
    monkeypatch.setattr(water.requests, "get", mocker.MagicMock(return_value=mocker.MagicMock(status_code=503)))

    assert water.getWater() is None
    assert "Status code: 503" in caplog.text


@pytest.mark.parametrize(
    "failure",
    [requests.ConnectionError("offline"), ValueError("invalid response")],
    ids=["connection-error", "parse-error"],
)
def test_get_water_returns_none_on_request_or_parse_exception(failure, mocker, monkeypatch, caplog):
    monkeypatch.setattr(water.requests, "get", mocker.MagicMock(side_effect=failure))

    assert water.getWater() is None
    assert "Fail to reach embalses.net" in caplog.text
