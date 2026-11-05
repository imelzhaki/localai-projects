import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from geometry_parser import parse_geometry_request, GeometryRequest, default_points_for_shape


def test_parse_geometry_request_segitiga_sama_kaki():
    req = parse_geometry_request("gambarkan segitiga sama kaki")
    assert req.action == "gambar"
    assert req.shape == "segitiga"


def test_parse_geometry_request_gambar_persegi_panjang():
    req = parse_geometry_request("gambar persegi panjang")
    assert req.action == "gambar"
    assert req.shape == "segiempat"


def test_parse_geometry_request_lingkaran():
    req = parse_geometry_request("gambarkan lingkaran")
    assert req.action == "gambar"
    assert req.shape == "lingkaran"


def test_parse_geometry_request_kubus_3d():
    req = parse_geometry_request("gambar kubus 3D")
    assert req.action == "gambar"
    assert req.shape == "kubus"


def test_parse_geometry_request_tanpa_gambar_mengembalikan_kosong():
    req = parse_geometry_request("segitiga sama kaki adalah segitiga yang memiliki dua sisi sama panjang")
    assert req.action is None
    assert req.shape is None


def test_parse_geometry_request_bukan_perintah_gambar():
    req = parse_geometry_request("Apa itu segitiga sama kaki?")
    assert req.action is None
    assert req.shape is None


def test_default_points_for_shape_segitiga():
    points = default_points_for_shape("segitiga")
    assert points is not None
    assert len(points) == 3


def test_default_points_for_shape_segiempat():
    points = default_points_for_shape("segiempat")
    assert points is not None
    assert len(points) == 4


def test_default_points_for_shape_tidak_dikenal():
    points = default_points_for_shape("lingkaran")
    assert points is None
