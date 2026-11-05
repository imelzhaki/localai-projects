"""Visualisasi geometri 2D dan 3D menggunakan Plotly untuk Socratic Tutor Bot."""

import plotly.graph_objects as go


def _close_polygon(points):
    """Kembalikan daftar titik yang ditutup (titik pertama diulang di akhir)."""
    return points + [points[0]]


def create_triangle_from_sides(a: float, b: float, c: float):
    """Buat figure Plotly untuk segitiga dengan panjang sisi a, b, c.

    Menempatkan sisi c pada sumbu x dari (0,0) ke (c,0), lalu menghitung
    titik ketiga menggunakan hukum kosinus.
    """
    import math

    # Titik A di (0,0), Titik B di (c, 0)
    # Titik C pada jarak a dari A dan jarak b dari B
    x = (a**2 + c**2 - b**2) / (2 * c)
    y_squared = a**2 - x**2
    if y_squared < 0:
        # Segitiga tidak valid (sisi tidak memenuhi ketidaksamaan segitiga)
        y = 0.0
    else:
        y = math.sqrt(y_squared)

    points = [(0, 0), (c, 0), (x, y)]
    return create_triangle_figure(points)


def create_triangle_figure(points):
    """Buat figure Plotly untuk segitiga dari 3 titik (x, y)."""
    closed = _close_polygon(points)
    xs, ys = zip(*closed)
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=list(xs),
            y=list(ys),
            mode="lines+markers",
            name="Segitiga",
            line=dict(color="royalblue", width=2),
            marker=dict(size=8, color="royalblue"),
        )
    )
    fig.update_layout(
        title="Segitiga",
        xaxis_title="x",
        yaxis_title="y",
        xaxis=dict(scaleanchor="y", scaleratio=1),
        yaxis=dict(scaleanchor="x", scaleratio=1),
        width=500,
        height=500,
        showlegend=False,
    )
    return fig


def create_quadrilateral_figure(points):
    """Buat figure Plotly untuk segiempat dari 4 titik (x, y)."""
    closed = _close_polygon(points)
    xs, ys = zip(*closed)
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=list(xs),
            y=list(ys),
            mode="lines+markers",
            name="Segiempat",
            line=dict(color="seagreen", width=2),
            marker=dict(size=8, color="seagreen"),
        )
    )
    fig.update_layout(
        title="Segiempat",
        xaxis_title="x",
        yaxis_title="y",
        xaxis=dict(scaleanchor="y", scaleratio=1),
        yaxis=dict(scaleanchor="x", scaleratio=1),
        width=500,
        height=500,
        showlegend=False,
    )
    return fig


def create_circle_figure(center, radius):
    """Buat figure Plotly untuk lingkaran dengan pusat dan radius."""
    cx, cy = center
    theta = [i * 0.1 for i in range(64)]
    xs = [cx + radius * __import__("math").cos(t) for t in theta]
    ys = [cy + radius * __import__("math").sin(t) for t in theta]
    xs.append(xs[0])
    ys.append(ys[0])
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=xs,
            y=ys,
            mode="lines",
            name="Lingkaran",
            line=dict(color="crimson", width=2),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[cx],
            y=[cy],
            mode="markers",
            name="Pusat",
            marker=dict(size=8, color="crimson"),
        )
    )
    fig.update_layout(
        title="Lingkaran",
        xaxis_title="x",
        yaxis_title="y",
        xaxis=dict(scaleanchor="y", scaleratio=1),
        yaxis=dict(scaleanchor="x", scaleratio=1),
        width=500,
        height=500,
        showlegend=False,
    )
    return fig


def create_sphere_figure(radius=1.0):
    """Buat figure Plotly 3D untuk bola dengan radius tertentu."""
    import math

    # Buat permukaan bola menggunakan parameterisasi bola
    u = [i * 0.1 for i in range(32)]  # azimuth
    v = [i * 0.1 for i in range(16)]  # polar

    xs = []
    ys = []
    zs = []

    for ui in u:
        for vi in v:
            x = radius * math.cos(ui) * math.sin(vi)
            y = radius * math.sin(ui) * math.sin(vi)
            z = radius * math.cos(vi)
            xs.append(x)
            ys.append(y)
            zs.append(z)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter3d(
            x=xs,
            y=ys,
            z=zs,
            mode="markers",
            marker=dict(size=2, color="royalblue", opacity=0.6),
            name=f"Bola (r={radius})",
        )
    )
    fig.update_layout(
        title=f"Bola 3D (radius: {radius})",
        scene=dict(
            xaxis_title="x",
            yaxis_title="y",
            zaxis_title="z",
            aspectmode="cube",
        ),
        width=600,
        height=600,
        showlegend=False,
    )
    return fig


def create_cube_figure():
    """Buat figure Plotly 3D untuk kubus satuan."""
    # 8 titik sudut kubus
    vertices = [
        (0, 0, 0),
        (1, 0, 0),
        (1, 1, 0),
        (0, 1, 0),
        (0, 0, 1),
        (1, 0, 1),
        (1, 1, 1),
        (0, 1, 1),
    ]
    # 12 rusuk kubus (pasangan indeks vertitas)
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),  # bawah
        (4, 5), (5, 6), (6, 7), (7, 4),  # atas
        (0, 4), (1, 5), (2, 6), (3, 7),  # vertikal
    ]
    fig = go.Figure()
    for i, j in edges:
        x0, y0, z0 = vertices[i]
        x1, y1, z1 = vertices[j]
        fig.add_trace(
            go.Scatter3d(
                x=[x0, x1, None],
                y=[y0, y1, None],
                z=[z0, z1, None],
                mode="lines",
                line=dict(color="darkorange", width=4),
                showlegend=False,
                hoverinfo="none",
            )
        )
    # Titik sudut
    xs, ys, zs = zip(*vertices)
    fig.add_trace(
        go.Scatter3d(
            x=list(xs),
            y=list(ys),
            z=list(zs),
            mode="markers",
            marker=dict(size=5, color="darkorange"),
            name="Sudut",
        )
    )
    fig.update_layout(
        title="Kubus 3D",
        scene=dict(
            xaxis_title="x",
            yaxis_title="y",
            zaxis_title="z",
            aspectmode="cube",
        ),
        width=600,
        height=600,
        showlegend=False,
    )
    return fig
