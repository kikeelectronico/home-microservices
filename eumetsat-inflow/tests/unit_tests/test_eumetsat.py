import io
import zipfile
from datetime import datetime
from types import SimpleNamespace

import numpy as np
import pytest

import eumetsat


def make_product_archive(filename=eumetsat.FRP_NETCDF_FILENAME):
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, "w") as zipped:
        if filename:
            zipped.writestr(filename, b"netcdf-placeholder")
    return archive.getvalue()


class Product:
    def __init__(self, content):
        self.content = content

    def __str__(self):
        return "sentinel-product"

    def open(self):
        return io.BytesIO(self.content)


def test_haversine_returns_zero_for_same_point():
    assert eumetsat.haversine(40.0, -3.0, 40.0, -3.0) == 0


def test_haversine_calculates_known_equatorial_distance():
    assert eumetsat.haversine(0, 0, 0, 1) == pytest.approx(111.2, abs=0.2)


def test_find_nearest_fire_returns_closest_event():
    result = eumetsat.findNearestFireEvent(0, 0, [(0, 2, 50), (0, 1, 20)])

    assert result[1:] == (0, 1, 20)
    assert result[0] == pytest.approx(111.2, abs=0.2)


def test_find_nearest_fire_returns_none_for_empty_list():
    assert eumetsat.findNearestFireEvent(0, 0, []) is None


def test_extract_fire_data_ignores_nan_frp_values(mocker, monkeypatch):
    dataset = mocker.MagicMock()
    dataset.data_vars = {eumetsat.LATITUDE_VAR: None, eumetsat.LONGITUDE_VAR: None, eumetsat.FRP_VAR: None}
    dataset.dims = {eumetsat.FIRE_DIMENSION: 3}
    values = {
        eumetsat.LATITUDE_VAR: SimpleNamespace(values=np.array([40.0, 41.0, 42.0])),
        eumetsat.LONGITUDE_VAR: SimpleNamespace(values=np.array([-3.0, -4.0, -5.0])),
        eumetsat.FRP_VAR: SimpleNamespace(values=np.array([100.0, np.nan, 300.0])),
    }
    dataset.__getitem__.side_effect = values.__getitem__
    open_dataset = mocker.MagicMock(return_value=dataset)
    monkeypatch.setattr(eumetsat.xr, "open_dataset", open_dataset)

    result = eumetsat.extractFireDataFromProduct(Product(make_product_archive()))

    assert result == [(40.0, -3.0, 100.0), (42.0, -5.0, 300.0)]
    open_dataset.assert_called_once()
    dataset.close.assert_called_once_with()


def test_extract_fire_data_returns_empty_when_archive_has_no_frp_file(mocker, caplog):
    result = eumetsat.extractFireDataFromProduct(Product(make_product_archive("other.nc")))

    assert result == []
    assert "No se encontró el archivo" in caplog.text


def test_extract_fire_data_handles_corrupt_archive(caplog):
    result = eumetsat.extractFireDataFromProduct(Product(b"not-a-zip"))

    assert result == []
    assert "Error procesando el producto" in caplog.text


def test_get_nearest_fire_returns_normalized_nearest_product(mocker, monkeypatch):
    class FixedDateTime(datetime):
        @classmethod
        def utcnow(cls):
            return cls(2026, 11, 16, 12, 30, 45)

    monkeypatch.setattr(eumetsat, "datetime", FixedDateTime)
    products = ["product-1"]
    search = mocker.MagicMock(return_value=products)
    extract = mocker.MagicMock(return_value=[(0.0, 1.0, 42.9), (0.0, 2.0, 99.0)])
    monkeypatch.setattr(eumetsat, "getProducts", search)
    monkeypatch.setattr(eumetsat, "extractFireDataFromProduct", extract)

    result = eumetsat.getNearestFire("consumer", "secret", 0, 0, "bbox")

    assert result == {"distance": 111.2, "latitude": 0.0, "longitud": 1.0, "frp": 42}
    assert search.call_args.args[:4] == ("consumer", "secret", "bbox", datetime(2026, 11, 15, 0, 0))
    assert search.call_args.args[4] == datetime(2026, 11, 16, 23, 59, 59)
    assert search.call_args.args[5] == eumetsat.FIRE_SATELLITES
    extract.assert_called_once_with("product-1")


@pytest.mark.parametrize("fires", [[], None])
def test_get_nearest_fire_returns_none_when_no_fire_data(fires, mocker, monkeypatch):
    monkeypatch.setattr(eumetsat, "getProducts", mocker.MagicMock(return_value=["product"]))
    monkeypatch.setattr(eumetsat, "extractFireDataFromProduct", mocker.MagicMock(return_value=fires or []))

    assert eumetsat.getNearestFire("consumer", "secret", 0, 0, "bbox") is None


def test_get_nearest_fire_handles_product_search_failure(mocker, monkeypatch, caplog):
    monkeypatch.setattr(eumetsat, "getProducts", mocker.MagicMock(side_effect=RuntimeError("offline")))

    assert eumetsat.getNearestFire("consumer", "secret", 0, 0, "bbox") is None
    assert "Error at getNearestFire" in caplog.text
