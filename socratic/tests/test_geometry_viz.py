import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from geometry_viz import (
    create_triangle_figure,
    create_quadrilateral_figure,
    create_circle_figure,
    create_cube_figure,
    create_sphere_figure,
)
import plotly.graph_objects as go


def test_create_triangle_figure_returns_go_figure():
    points = [(0, 0), (4, 0), (2, 3)]
    fig = create_triangle_figure(points)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) > 0


def test_create_triangle_figure_has_three_vertices():
    points = [(0, 0), (4, 0), (2, 3)]
    fig = create_triangle_figure(points)
    # Scatter trace untuk garis segitiga harus memiliki 4 titik (tertutup)
    scatter_traces = [t for t in fig.data if isinstance(t, go.Scatter)]
    assert len(scatter_traces) >= 1
    x = scatter_traces[0].x
    y = scatter_traces[0].y
    assert len(x) == 4  # 3 titik + kembali ke titik awal
    assert len(y) == 4


def test_create_quadrilateral_figure_returns_go_figure():
    points = [(0, 0), (4, 0), (4, 3), (0, 3)]
    fig = create_quadrilateral_figure(points)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) > 0


def test_create_quadrilateral_figure_has_four_vertices():
    points = [(0, 0), (4, 0), (4, 3), (0, 3)]
    fig = create_quadrilateral_figure(points)
    scatter_traces = [t for t in fig.data if isinstance(t, go.Scatter)]
    assert len(scatter_traces) >= 1
    x = scatter_traces[0].x
    y = scatter_traces[0].y
    assert len(x) == 5  # 4 titik + kembali ke titik awal
    assert len(y) == 5


def test_create_circle_figure_returns_go_figure():
    fig = create_circle_figure((0, 0), 2)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) > 0


def test_create_cube_figure_returns_go_figure_3d():
    fig = create_cube_figure()
    assert isinstance(fig, go.Figure)
    assert len(fig.data) > 0
    # Scatter3d untuk 3D
    scatter3d_traces = [t for t in fig.data if isinstance(t, go.Scatter3d)]
    assert len(scatter3d_traces) >= 1


def test_create_sphere_figure_returns_go_figure_3d():
    fig = create_sphere_figure(radius=1.0)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) > 0
    scatter3d_traces = [t for t in fig.data if isinstance(t, go.Scatter3d)]
    assert len(scatter3d_traces) >= 1


def test_create_sphere_figure_has_title_with_radius():
    fig = create_sphere_figure(radius=0.5)
    assert "0.5" in fig.layout.title.text
