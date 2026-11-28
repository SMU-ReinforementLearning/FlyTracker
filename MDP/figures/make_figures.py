"""01-camera-markov-process.md의 그림 스무 장을 만든다.

    python docs/mdp-v1/figures/make_figures.py            # SVG 스무 장을 이 폴더에 쓴다
    python docs/mdp-v1/figures/make_figures.py --png DIR  # 확인용 PNG도 DIR에 쓴다

그림의 내용과 값은 docs/mdp-v1/01-figures.md를 따른다.
"""

from __future__ import annotations

import argparse
import math
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager as fm
from matplotlib.patches import (Circle, Ellipse, FancyArrowPatch, FancyBboxPatch,
                                PathPatch, Polygon, Rectangle, Wedge)
from matplotlib.path import Path as MPath

HERE = Path(__file__).resolve().parent

BLUE, ORANGE, GREEN = "#0072B2", "#E69F00", "#009E73"
POINT = "#D55E00"
GRAY = "#7F7F7F"
INK = "#222222"
SOFT = 0.15
WIDTH = 7.0
FS = 10


def setup() -> None:
    have = {f.name for f in fm.fontManager.ttflist}
    family = [n for n in ("Malgun Gothic", "Apple SD Gothic Neo", "Noto Sans KR") if n in have]
    plt.rcParams.update({
        "font.family": family + ["sans-serif"],
        "font.size": FS,
        "mathtext.fontset": "cm",
        "svg.fonttype": "path",
        "svg.hashsalt": "01-figures",
        "axes.unicode_minus": False,
        "figure.facecolor": "white",
        "savefig.facecolor": "white",
        "axes.edgecolor": INK,
        "text.color": INK,
        "axes.labelcolor": INK,
        "xtick.color": INK,
        "ytick.color": INK,
    })


# ---------- 공용: 계산 ----------

def ex1(s, u):
    return (s[0] + 30.0 * u, s[1])


def ex2(s, u):
    return (s[0] + 30.0 * u, 20.0 + math.exp(-0.5 * u) * (s[1] - 20.0))


def check_values() -> None:
    rows = [((40, -50), 1, (70, -22.5)), ((40, -50), 2, (100, -5.8)),
            ((100, -5.8), 3, (190, 14.3)), ((40, -50), 5, (190, 14.3)),
            ((30, -50), 1.5, (75, -13.1)), ((70, -20), 1.5, (115, 1.1))]
    for s, u, want in rows:
        got = ex2(s, u)
        assert abs(got[0] - want[0]) <= 0.1 and abs(got[1] - want[1]) <= 0.1, (s, u, got, want)


def clip(poly, n, d):
    """다각형을 반공간 n.x <= d로 자른다(2차원과 3차원 공용)."""
    out = []
    m = len(poly)
    for i in range(m):
        a, b = poly[i], poly[(i + 1) % m]
        fa, fb = float(np.dot(n, a) - d), float(np.dot(n, b) - d)
        if fa <= 0:
            out.append(a)
        if (fa < 0 < fb) or (fb < 0 < fa):
            out.append(a + (b - a) * (fa / (fa - fb)))
    return out


# ---------- 공용: 바탕 ----------

def arrow(ax, a, b, color=GRAY, lw=1.0, ms=9, style="-|>", ls="-", rad=0.0, z=3):
    p = FancyArrowPatch(a, b, arrowstyle=style, mutation_scale=ms, color=color, lw=lw,
                        linestyle=ls, shrinkA=0, shrinkB=0,
                        connectionstyle=f"arc3,rad={rad}", zorder=z)
    ax.add_patch(p)
    return p


def unrolled(ax, labels=True) -> None:
    """3.5의 펼친 직사각형. 다섯 그림이 똑같이 쓴다."""
    ax.set_xlim(0, 360)
    ax.set_ylim(-60, 60)
    ax.set_box_aspect(0.42)
    ax.set_xticks([0, 90, 180, 270, 360])
    ax.set_xticklabels(["0°\n(북)", "90°\n(동)", "180°\n(남)", "270°\n(서)", "360°\n(북)"])
    ax.set_yticks([-60, 0, 60])
    ax.set_yticklabels(["−60°", "0°", "60°"])
    ax.grid(False)
    if labels:
        ax.set_xlabel(r"$s_{\mathrm{yaw}}$")
        ax.set_ylabel(r"$s_{\mathrm{pitch}}$")
    for x in (0, 360):
        ax.plot([x, x], [-9, 9], linestyle="none", marker="^", markersize=6,
                color=INK, clip_on=False, zorder=6)


COLS = [0.0, 1.5, 2.95, 4.4, 5.85]
ROWH = 0.56
HEAD = ["", "시각 $0$", "시각 $t$", "시각 $t+u$"]
DATA = [["북", "동", "남"], ["북", "동", "동"], ["동", "동", "남"],
        ["동", "동", "동"], ["동", "남", "남"]]


def motion_table(ax, outline=None, names=(), column=None, legend=(), title=None, top=None):
    """3.6의 운동의 표. outline은 {(행, 열): 색}, names는 이름 칸을 칠할 행, column은 칠할 열."""
    outline = outline or {}
    n = len(DATA)
    ytop = (n + 1) * ROWH
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_xlim(-0.2, COLS[-1] + 0.2)
    ax.set_ylim(-0.25 - 0.55 * len(legend), ytop + (1.35 if (title or top) else 0.2))

    def cell(r, c):  # r = -1이 머리 행, c = 0이 이름 칸
        return COLS[c], ytop - (r + 2) * ROWH, COLS[c + 1] - COLS[c], ROWH

    if column is not None:
        x, y, w, h = cell(n - 1, column)
        ax.add_patch(Rectangle((x, y), w, ROWH * n, facecolor=BLUE, alpha=SOFT, edgecolor="none"))
    for r in names:
        x, y, w, h = cell(r, 0)
        ax.add_patch(Rectangle((x, y), w, h, facecolor=BLUE, alpha=0.30, edgecolor="none"))
    for r in range(-1, n):
        for c in range(4):
            x, y, w, h = cell(r, c)
            ax.add_patch(Rectangle((x, y), w, h, facecolor="none", edgecolor=GRAY, lw=0.7))
            if r == -1:
                text = HEAD[c]
            elif c == 0:
                text = f"운동 {r + 1}"
            else:
                text = DATA[r][c - 1]
            ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=FS + 1)
    for (r, c), color in outline.items():
        x, y, w, h = cell(r, c)
        pad = 0.07
        ax.add_patch(Rectangle((x + pad, y + pad), w - 2 * pad, h - 2 * pad,
                               facecolor="none", edgecolor=color, lw=2.0))
    for c, text in (top or ()):
        x, y, w, h = cell(-1, c)
        ax.text(x + w / 2, ytop + 0.2, text, ha="center", va="bottom", fontsize=FS, color=BLUE)
    if title:
        ax.text(COLS[-1] / 2, ytop + 0.8, title, ha="center", va="bottom", fontsize=FS + 1)
    for i, (kind, text) in enumerate(legend):
        y = -0.45 - 0.55 * i
        if kind == "outline":
            ax.add_patch(Rectangle((0.15, y - 0.16), 0.5, 0.32, facecolor="none", edgecolor=BLUE, lw=2.0))
        else:
            ax.add_patch(Rectangle((0.15, y - 0.16), 0.5, 0.32, facecolor=BLUE, alpha=0.30, edgecolor="none"))
        ax.text(0.85, y, text, ha="left", va="center", fontsize=FS + 1)


# ---------- 그림 1 ~ 4: 방과 state space ----------

def fig01():
    p0 = np.array([2.0, 2.0, 1.0])
    psi, th = math.radians(30), math.radians(10)
    ef = np.array([math.cos(th) * math.sin(psi), math.cos(th) * math.cos(psi), math.sin(th)])
    er = np.array([math.cos(psi), -math.sin(psi), 0.0])
    eu = np.array([-math.sin(th) * math.sin(psi), -math.sin(th) * math.cos(psi), math.cos(th)])
    ta, tb = math.tan(math.radians(30)), math.tan(math.radians(22.5))
    rays = [ef + sa * ta * er + sb * tb * eu for sa, sb in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    box = [(np.array(n, float), d) for n, d in (((1, 0, 0), 4), ((-1, 0, 0), 0), ((0, 1, 0), 4),
                                               ((0, -1, 0), 0), ((0, 0, 1), 4), ((0, 0, -1), 0))]

    def in_box(poly):
        for n, d in box:
            poly = clip(poly, n, d)
            if len(poly) < 3:
                return []
        return poly

    faces = []
    for i in range(4):  # 사각뿔의 옆면 넷
        a, b = rays[i], rays[(i + 1) % 4]
        faces.append(in_box([p0, p0 + 20 * a, p0 + 20 * b]))
    planes = []  # 사각뿔의 안쪽: n.(x - p0) <= 0
    for i in range(4):
        n = np.cross(rays[i], rays[(i + 1) % 4])
        if np.dot(n, ef) > 0:
            n = -n
        planes.append((n, float(np.dot(n, p0))))
    walls = [[(4, 0, 0), (4, 4, 0), (4, 4, 4), (4, 0, 4)], [(0, 4, 0), (4, 4, 0), (4, 4, 4), (0, 4, 4)],
             [(0, 0, 4), (4, 0, 4), (4, 4, 4), (0, 4, 4)], [(0, 0, 0), (4, 0, 0), (4, 4, 0), (0, 4, 0)],
             [(0, 0, 0), (0, 4, 0), (0, 4, 4), (0, 0, 4)], [(0, 0, 0), (4, 0, 0), (4, 0, 4), (0, 0, 4)]]
    for wall in walls:  # 벽에 닿는 면
        poly = [np.array(v, float) for v in wall]
        for n, d in planes:
            poly = clip(poly, n, d)
            if len(poly) < 3:
                break
        if len(poly) >= 3:
            faces.append(poly)

    az, el = math.radians(38), math.radians(24)
    right = np.array([math.cos(az), math.sin(az), 0.0])
    fwd = np.array([-math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), -math.sin(el)])
    up = np.cross(right, fwd)

    def pr(v):
        v = np.asarray(v, float)
        return float(np.dot(v, right)), float(np.dot(v, up))

    fig, ax = plt.subplots(figsize=(WIDTH, 4.6))
    corners = [np.array([x, y, z], float) for x in (0, 4) for y in (0, 4) for z in (0, 4)]
    for i, a in enumerate(corners):
        for b in corners[i + 1:]:
            if np.sum(np.abs(a - b) > 0) == 1:
                (x1, y1), (x2, y2) = pr(a), pr(b)
                seen = False
                for j in range(3):  # 이 모서리에 닿은 두 면 가운데 하나라도 앞을 보면 보이는 모서리
                    if a[j] == b[j]:
                        n = np.zeros(3)
                        n[j] = 1.0 if a[j] == 4 else -1.0
                        seen = seen or float(np.dot(n, fwd)) < 0
                ax.plot([x1, x2], [y1, y2], color=GRAY, lw=0.9 if seen else 0.6,
                        linestyle="-" if seen else (0, (3, 3)), zorder=1)
    faces = [f for f in faces if len(f) >= 3]
    faces.sort(key=lambda f: -float(np.dot(np.mean(f, axis=0), fwd)))
    for f in faces:
        ax.add_patch(Polygon([pr(v) for v in f], closed=True, facecolor=BLUE, alpha=0.22,
                             edgecolor=BLUE, lw=0.8, zorder=2))
    x0, y0 = pr(p0)
    xf, yf = pr((2.0, 2.0, 0.0))
    ax.plot([x0, xf], [y0, yf], color=INK, lw=0.7, linestyle=":", zorder=4)
    ax.plot([xf], [yf], "x", color=INK, markersize=4, zorder=4)
    ax.plot([x0], [y0], "o", color=INK, markersize=5, zorder=5)
    ax.annotate(r"$p_0$", (x0, y0), xytext=(x0 - 0.55, y0 - 0.7), fontsize=FS + 3,
                arrowprops=dict(arrowstyle="-", color=GRAY, lw=0.7), ha="center", va="center")
    cx, cy = min((pr((x, y, 4)) for x in (0, 4) for y in (0, 4)), key=lambda q: q[0])
    ax.annotate(r"$\mathrm{Room}$", (cx, cy), xytext=(cx - 0.7, cy + 0.55), fontsize=FS + 3,
                arrowprops=dict(arrowstyle="-", color=GRAY, lw=0.7), ha="center", va="center")
    ax.set_aspect("equal")
    ax.axis("off")
    ax.margins(0.08)
    return fig


def fig02():
    fig, ax = plt.subplots(figsize=(WIDTH, 4.8))
    ax.add_patch(Rectangle((0, 0), 4, 4, facecolor="none", edgecolor=INK, lw=1.0))
    p0 = np.array([2.0, 2.0])
    sq = [(np.array([1.0, 0.0]), 4.0), (np.array([-1.0, 0.0]), 0.0),
          (np.array([0.0, 1.0]), 4.0), (np.array([0.0, -1.0]), 0.0)]

    def d(yaw):
        r = math.radians(yaw)
        return np.array([math.sin(r), math.cos(r)])

    for yaw, color, name in ((30, BLUE, "$s$"), (150, ORANGE, "$s'$"), (270, GREEN, "$s''$")):
        poly = [p0, p0 + 20 * d(yaw - 30), p0 + 20 * d(yaw + 30)]
        for n, dd in sq:
            poly = clip(poly, n, dd)
        ax.add_patch(Polygon(poly, closed=True, facecolor=color, alpha=0.25, edgecolor=color, lw=1.0))
        tip = p0 + 1.05 * d(yaw)
        arrow(ax, p0, tip, color=color, lw=1.6, ms=12)
        lab = p0 + 1.32 * d(yaw)
        ax.text(lab[0], lab[1], name, ha="center", va="center", fontsize=FS + 3)
    ax.plot([2], [2], "o", color=INK, markersize=5, zorder=6)
    ax.text(1.78, 2.2, r"$p_0$", ha="center", va="center", fontsize=FS + 3)
    far = p0 + 1.75 * d(30)
    ax.annotate(r"$\mathrm{View}(s)$", (far[0], far[1]), xytext=(5.0, 3.5), fontsize=FS + 2,
                arrowprops=dict(arrowstyle="-", color=GRAY, lw=0.7), ha="center", va="center")
    for (x, y), t in (((2, 4.28), "북"), ((4.28, 2), "동"), ((2, -0.28), "남"), ((-0.28, 2), "서")):
        ax.text(x, y, t, ha="center", va="center", fontsize=FS + 1)
    ax.set_xlim(-0.7, 5.8)
    ax.set_ylim(-0.6, 4.6)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig


def fig03():
    fig, ax = plt.subplots(figsize=(WIDTH, 4.6))
    ax.add_patch(Rectangle((0, 0), 4, 4, facecolor="none", edgecolor=INK, lw=1.0))
    p0 = np.array([2.0, 1.0])
    lo, hi = math.radians(-32.5), math.radians(12.5)
    dlo, dhi = np.array([math.cos(lo), math.sin(lo)]), np.array([math.cos(hi), math.sin(hi)])
    poly = [p0, p0 + 20 * dlo, p0 + 20 * dhi]
    for n, dd in ((np.array([1.0, 0.0]), 4.0), (np.array([0.0, -1.0]), 0.0), (np.array([0.0, 1.0]), 4.0)):
        poly = clip(poly, n, dd)
    ax.add_patch(Polygon(poly, closed=True, facecolor=BLUE, alpha=SOFT, edgecolor="none"))
    for dv in (dlo, dhi):
        end = p0 + 3.5 * dv
        ax.plot([p0[0], end[0]], [p0[1], end[1]], color=INK, lw=0.9)
    mid = math.radians(-10)
    tipq = p0 + 3.3 * np.array([math.cos(mid), math.sin(mid)])
    ax.plot([p0[0], tipq[0]], [p0[1], tipq[1]], color=INK, lw=0.8, linestyle="-.")
    ax.text(tipq[0] + 0.18, tipq[1], r"$s$", ha="center", va="center", fontsize=FS + 3)
    ax.add_patch(Wedge(p0, 0.8, -32.5, 12.5, facecolor=POINT, alpha=0.55, edgecolor="none"))
    ax.add_patch(Circle(p0, 0.8, facecolor="none", edgecolor=INK, lw=0.9, linestyle="--"))
    ax.plot([p0[0]], [p0[1]], "o", color=INK, markersize=5, zorder=6)
    ax.text(1.72, 1.0, r"$p_0$", ha="center", va="center", fontsize=FS + 3)
    ax.text(1.55, 1.95, r"$D$", ha="center", va="center", fontsize=FS + 3)
    ax.text(0.5, 3.6, r"$\mathrm{Room}$", ha="center", va="center", fontsize=FS + 3)
    ax.text(3.42, 0.42, r"$\mathrm{View}(s)$", ha="center", va="center", fontsize=FS + 2, color=BLUE)
    tip = p0 + 3.5 * dhi
    ax.text(tip[0] + 0.1, tip[1] + 0.22, r"$\mathrm{Cone}(s)$", ha="center", va="center", fontsize=FS + 2)
    ax.set_xlim(-0.4, 6.0)
    ax.set_ylim(-1.1, 4.3)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig


THREE = (((30, 0), BLUE), ((150, 30), ORANGE), ((270, -30), GREEN))


def fig04():
    fig, (a, b) = plt.subplots(1, 2, figsize=(WIDTH, 3.3), gridspec_kw={"width_ratios": [1, 1.45]})
    R, ry, h0, h1, front = 1.0, 0.4, -1.0, 1.0, 90.0
    t = np.linspace(0, 2 * math.pi, 200)
    a.fill_between([-R, R], [h0, h0], [h1, h1], color="#F2F2F2", zorder=0)
    a.add_patch(Ellipse((0, h1), 2 * R, 2 * ry, facecolor="#FAFAFA", edgecolor=INK, lw=1.0, zorder=2))
    a.plot(R * np.cos(t[100:]), h0 + ry * np.sin(t[100:]), color=INK, lw=1.0)
    a.plot(R * np.cos(t[:100]), h0 + ry * np.sin(t[:100]), color=GRAY, lw=0.7, linestyle=":")
    a.plot([-R, -R], [h0, h1], color=INK, lw=1.0)
    a.plot([R, R], [h0, h1], color=INK, lw=1.0)

    def on(yaw, pitch):
        rel = math.radians(yaw - front)
        return R * math.sin(rel), (pitch / 60.0) * 0.8 - ry * math.cos(rel), math.cos(rel) > 0

    for (yaw, pitch), color in THREE:
        x, y, vis = on(yaw, pitch)
        a.plot([x], [y], "o", markersize=8, markerfacecolor=color, alpha=1.0 if vis else 0.35,
               markeredgecolor=color, markeredgewidth=1.2, zorder=5)
    for yaw, name in ((0, "북"), (90, "동"), (180, "남"), (270, "서")):
        rel = math.radians(yaw - front)
        a.text(0.66 * R * math.sin(rel), h1 - 0.5 * ry * math.cos(rel), name, ha="center", va="center", fontsize=FS)
    a.plot([-R, -R], [-0.72, -0.46], linestyle="none", marker="^", markersize=6, color=INK, zorder=6)
    a.text(R + 0.4, h1 + 0.25, r"$\mathcal{S}$", ha="center", va="center", fontsize=FS + 5)
    arrow(a, (-R - 0.38, h0), (-R - 0.38, h1), color=INK, lw=0.8)
    a.text(-R - 0.5, 0, r"$s_{\mathrm{pitch}}$", ha="right", va="center", fontsize=FS + 1)
    arrow(a, (-0.55, h0 - 0.62), (0.55, h0 - 0.62), color=INK, lw=0.8, rad=0.25)
    a.text(0, h0 - 1.05, r"$s_{\mathrm{yaw}}$", ha="center", va="center", fontsize=FS + 1)
    a.set_xlim(-2.2, 1.7)
    a.set_ylim(-2.3, 1.75)
    a.set_aspect("equal")
    a.axis("off")
    unrolled(b)
    for (yaw, pitch), color in THREE:
        b.plot([yaw], [pitch], "o", markersize=8, color=color, zorder=5)
    fig.subplots_adjust(left=0.01, right=0.955, bottom=0.24, top=0.97, wspace=0.5)
    pa, pb = a.get_position(), b.get_position()
    y = (pa.y0 + pa.y1) / 2
    x1, x2 = pa.x1 + 0.0, pb.x0 - 0.1
    fig.patches.append(FancyArrowPatch((x1, y), (x2, y), transform=fig.transFigure, arrowstyle="-|>",
                                       mutation_scale=11, color=INK, lw=0.9))
    fig.text((x1 + x2) / 2, y + 0.06, "펼침", ha="center", va="bottom", fontsize=FS)
    return fig


# ---------- 그림 5 ~ 9: 운동의 표와 대응 ----------

def fig09():
    fig, ax = plt.subplots(figsize=(WIDTH, 2.9))
    for x0 in (0.3, 4.7):
        ax.add_patch(FancyBboxPatch((x0, 0.3), 3.0, 2.4, boxstyle="round,pad=0.02,rounding_size=0.18",
                                    facecolor="none", edgecolor=INK, lw=1.0))
    ax.text(0.62, 2.38, r"$\Omega$", ha="center", va="center", fontsize=FS + 5)
    ax.text(5.02, 2.38, r"$\mathcal{S}$", ha="center", va="center", fontsize=FS + 5)
    ax.add_patch(Ellipse((1.85, 1.3), 2.1, 1.15, facecolor=BLUE, alpha=SOFT, edgecolor="none"))
    ax.add_patch(Ellipse((1.85, 1.3), 2.1, 1.15, facecolor="none", edgecolor=BLUE, lw=1.2))
    ax.add_patch(Ellipse((6.25, 1.3), 1.5, 1.0, facecolor=BLUE, alpha=SOFT, edgecolor="none"))
    ax.add_patch(Ellipse((6.25, 1.3), 1.5, 1.0, facecolor="none", edgecolor=BLUE, lw=1.2))
    ax.text(1.85, 1.3, r"$S_t^{-1}(F)$", ha="center", va="center", fontsize=FS + 4)
    ax.text(6.25, 1.3, r"$F$", ha="center", va="center", fontsize=FS + 4)
    arrow(ax, (5.45, 1.3), (2.95, 1.3), color=BLUE, lw=1.6, ms=14)
    ax.text(4.0, 1.52, r"$S_t$", ha="center", va="bottom", fontsize=FS + 4, color=BLUE)
    ax.set_xlim(0, 8)
    ax.set_ylim(0, 3)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig


# ---------- 그림 10 ~ 14: flow ----------

def fig15():
    fig, ax = plt.subplots(figsize=(WIDTH, 3.5))
    unrolled(ax)
    f0, f1 = (30.0, -50.0), (70.0, -20.0)
    g0, g1 = ex2(f0, 1.5), ex2(f1, 1.5)
    ax.add_patch(Rectangle(f0, f1[0] - f0[0], f1[1] - f0[1], facecolor=BLUE, alpha=SOFT, edgecolor="none"))
    ax.add_patch(Rectangle(g0, g1[0] - g0[0], g1[1] - g0[1], facecolor=BLUE, alpha=SOFT, edgecolor="none"))
    ax.add_patch(Rectangle(g0, g1[0] - g0[0], g1[1] - g0[1], facecolor="none", edgecolor=BLUE, lw=1.3))
    for c in ((30, -50), (70, -50), (30, -20), (70, -20)):
        d = ex2(c, 1.5)
        ax.plot([c[0], d[0]], [c[1], d[1]], color=GRAY, lw=0.8, linestyle=(0, (2, 3)), zorder=3)
    ax.text(18, -35, r"$F$", ha="center", va="center", fontsize=FS + 3)
    ax.text(140, -6, r"$T_u(F)$", ha="center", va="center", fontsize=FS + 3)
    fig.subplots_adjust(left=0.12, right=0.95, bottom=0.22, top=0.96)
    return fig


def fig17():
    ys = {170: (106, 120, 134), 340: (92, 120, 148), 510: (74, 122, 166)}
    return timeline(
        236,
        axis=(90, 40, 190),
        vlines=[(170, 40, 190, "시각 $0$", 214, False), (340, 40, 190, "시각 $t$", 214, False),
                (510, 40, 190, "시각 $t+u$", 214, False)],
        gates=[(170, 98, 142), (340, 84, 156), (510, 64, 176)],
        curves=[("M110 104 C 140 104, 150 106, 170 106 C 230 106, 290 92, 340 92 C 400 92, 460 74, 510 74 C 540 74, 565 73, 590 72", HI),
                ("M110 122 C 140 122, 150 120, 170 120 C 230 120, 290 120, 340 120 C 400 120, 460 122, 510 122 C 540 122, 565 123, 590 123", HI),
                ("M110 138 C 140 136, 150 134, 170 134 C 230 134, 290 148, 340 148 C 400 148, 460 166, 510 166 C 540 166, 565 167, 590 168", HI)],
        dots=[(x, y, "hi") for x, col in ys.items() for y in col],
        texts=[(78, 115, r"$\mathcal{S}$", "right", 4), (182, 84, "$F$", "left", 3),
               (352, 70, "$T_t(F)$", "left", 3), (522, 50, "$T_{t+u}(F)$", "left", 3)],
    )


GRID = [(15.0 + 45.0 * i, y) for y in (-48.0, -24.0, 0.0, 24.0, 48.0) for i in range(8)]


def field(ax, step, mark=None):
    for p in GRID:
        if mark is not None and p == mark:
            continue
        arrow(ax, p, step(p, 1.0), color=GRAY, lw=0.9, ms=7)
    if mark is not None:
        q = step(mark, 1.0)
        arrow(ax, mark, q, color=BLUE, lw=1.8, ms=10, z=5)
        ax.text((mark[0] + q[0]) / 2, mark[1] + 12.5, r"$s\,\overset{u}{\longrightarrow}\,s'$",
                ha="center", va="center", fontsize=FS + 1, color=BLUE)


def fig18():
    fig, (a, b) = plt.subplots(1, 2, figsize=(WIDTH, 2.6))
    unrolled(a)
    unrolled(b)
    field(a, ex1, mark=(150.0, 0.0))
    field(b, ex2)
    b.axhline(20, color=INK, lw=0.8, linestyle=":")
    b.text(368, 20, r"$a$", ha="left", va="center", fontsize=FS + 2, clip_on=False)
    a.set_title("Example 1", fontsize=FS + 1)
    b.set_title("Example 2", fontsize=FS + 1)
    b.set_ylabel("")
    fig.subplots_adjust(left=0.1, right=0.955, bottom=0.3, top=0.88, wspace=0.24)
    return fig


def fig19():
    fig = plt.figure(figsize=(WIDTH, 2.9))
    a = fig.add_axes([0.0, 0.02, 0.34, 0.96])
    m = fig.add_axes([0.33, 0.02, 0.2, 0.96])
    b = fig.add_axes([0.655, 0.34, 0.3, 0.46])
    pos = {"북": (0, 1.25), "동": (1.25, 0), "남": (0, -1.25), "서": (-1.25, 0)}
    ang = {"북": 90, "동": 0, "남": 270, "서": 180}
    h = 0.3
    for name, (x, y) in pos.items():
        a.add_patch(Rectangle((x - h, y - h), 2 * h, 2 * h, facecolor="white", edgecolor=INK, lw=1.0, zorder=3))
        a.add_patch(Wedge((x, y), h * 0.95, ang[name] - 30, ang[name] + 30, facecolor=BLUE, alpha=0.4,
                          edgecolor="none", zorder=4))
        a.plot([x], [y], "o", color=INK, markersize=3, zorder=5)
        ox, oy = (0.62 * math.cos(math.radians(ang[name] + 180)), 0.62 * math.sin(math.radians(ang[name] + 180)))
        a.text(x - 0.0 + (-0.55 if name in ("북", "남") else 0), y + (0.0 if name in ("북", "남") else 0.52),
               name, ha="center", va="center", fontsize=FS)
    order = ["북", "동", "남", "서"]
    for i, name in enumerate(order):
        x, y = pos[name]
        nx, ny = pos[order[(i + 1) % 4]]
        d = np.array([nx - x, ny - y])
        d = d / np.linalg.norm(d)
        arrow(a, (x + 0.48 * d[0], y + 0.48 * d[1]), (nx - 0.48 * d[0], ny - 0.48 * d[1]),
              color=INK, lw=1.0, ms=10, rad=-0.22)
        r = math.radians(ang[name])
        ux, uy = math.cos(r), math.sin(r)
        px, py = -uy, ux
        p1 = (x + (h + 0.03) * ux + 0.16 * px, y + (h + 0.03) * uy + 0.16 * py)
        p2 = (x + (h + 0.03) * ux - 0.16 * px, y + (h + 0.03) * uy - 0.16 * py)
        arrow(a, p1, p2, color=INK, lw=1.0, ms=8, rad=-1.9)
    a.text(1.18, 1.12, r"$\mathcal{P}_{ss'}$", ha="center", va="center", fontsize=FS + 2)
    a.set_xlim(-2.25, 2.25)
    a.set_ylim(-2.2, 2.2)
    a.set_aspect("equal")
    a.axis("off")
    m.axis("off")
    m.set_xlim(0, 1)
    m.set_ylim(0, 1)
    for y, (l, r_) in ((0.62, ("노드", r"$\mathcal{S}$의 원소")), (0.4, ("간선", "화살표"))):
        m.text(0.02, y, l, ha="left", va="center", fontsize=FS)
        m.annotate("", xy=(0.52, y), xytext=(0.3, y), arrowprops=dict(arrowstyle="<->", color=GRAY, lw=0.9))
        m.text(0.57, y, r_, ha="left", va="center", fontsize=FS)
    unrolled(b)
    field(b, ex1)
    return fig


# ---------- 공용: 시간선 그림 ----------

HI = dict(color=BLUE, lw=2.0)
LO = dict(color=GRAY, lw=1.5, alpha=0.6)
PLAIN = dict(color=GRAY, lw=1.5)
DASH = dict(color=GRAY, lw=1.5, linestyle="--")


def bezier(d):
    """SVG path의 M과 C만 읽어 matplotlib Path로 바꾼다."""
    nums = [float(v) for v in re.findall(r"-?\d+(?:\.\d+)?", d)]
    verts = [(nums[0], nums[1])]
    codes = [MPath.MOVETO]
    for i in range(2, len(nums), 6):
        verts += [(nums[i], nums[i + 1]), (nums[i + 2], nums[i + 3]), (nums[i + 4], nums[i + 5])]
        codes += [MPath.CURVE4] * 3
    return MPath(verts, codes)


def timeline(height, vlines=(), curves=(), gates=(), dots=(), texts=(), legend=(), titles=(), axis=None):
    """3.7의 시간선 그림. 좌표는 가로 680, 세로 height이고 왼쪽 위가 원점이다.

    vlines: (x, y0, y1, 아래 라벨, 라벨 y, 실선 여부)
    curves: (path 문자열, 선 모양)          gates: (x, y0, y1)
    dots:   (x, y, "hi" | "lo" | "point" | "start")
    texts:  (x, y, 글자, ha, 크기 보탬)
    legend: (x, y, [선 모양, ...], 글자)     titles: (x, y, 글자)
    """
    fig = plt.figure(figsize=(WIDTH, WIDTH * height / 680.0))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 680)
    ax.set_ylim(height, 0)
    ax.axis("off")
    if axis is not None:
        x, y0, y1 = axis
        ax.plot([x, x], [y0, y1], color=INK, lw=1.0)
    for x, y0, y1, label, ly, solid in vlines:
        ax.plot([x, x], [y0, y1], color=GRAY, lw=0.8, linestyle="-" if solid else (0, (2, 3)), zorder=1)
        if label:
            ax.text(x, ly, label, ha="center", va="center", fontsize=FS)
    for x, y0, y1 in gates:
        ax.plot([x, x], [y0, y1], color=BLUE, lw=7, alpha=0.45, solid_capstyle="round", zorder=2)
    for d, style in curves:
        kw = dict(style)
        kw["edgecolor"] = kw.pop("color")
        ax.add_patch(PathPatch(bezier(d), fill=False, zorder=3, **kw))
    for x, y, kind in dots:
        color, size = {"hi": (BLUE, 6.5), "lo": (GRAY, 5.5), "point": (POINT, 7.0), "start": (GRAY, 4.0)}[kind]
        ax.plot([x], [y], "o", color=color, markersize=size, zorder=5)
    for x, y, text, ha, plus in texts:
        ax.text(x, y, text, ha=ha, va="center", fontsize=FS + plus)
    for x, y, text in titles:
        ax.text(x, y, text, ha="center", va="center", fontsize=FS + 1)
    for x, y, styles, text in legend:
        for style in styles:
            ax.plot([x, x + 30], [y, y], **style)
            x += 36
        ax.text(x + 2, y, text, ha="left", va="center", fontsize=FS)
    return fig


# ---------- 그림 5 ~ 14: 운동과 시각 t의 state ----------

def fig05():
    ends = (90, 160, 225)
    starts = (70, 140, 215)
    return timeline(
        280,
        vlines=[(130, 45, 240, "시각 $0$", 262, True), (470, 45, 240, "시각 $t$", 262, True)],
        curves=[("M130 70 C 240 60, 340 120, 470 90", LO), ("M130 140 C 240 170, 340 120, 470 160", LO),
                ("M130 215 C 240 230, 340 190, 470 225", LO)],
        dots=[(130, y, "start") for y in starts] + [(470, y, "hi") for y in ends],
        texts=[(118, y, f"운동 {i + 1}", "right", 0) for i, y in enumerate(starts)]
        + [(484, y, name, "left", 3) for y, name in zip(ends, ("$s$", "$s'$", "$s''$"))]
        + [(470, 30, r"$\mathcal{S}$", "center", 4)],
    )


def fig06():
    starts = (70, 120, 175, 225)
    return timeline(
        300,
        vlines=[(130, 45, 240, "시각 $0$", 262, False), (470, 45, 240, "시각 $t$", 262, False)],
        gates=[(470, 70, 160)],
        curves=[("M130 70 C 240 60, 340 110, 470 90", HI), ("M130 120 C 240 150, 340 110, 470 140", HI),
                ("M130 175 C 240 190, 340 170, 470 195", LO), ("M130 225 C 240 235, 340 215, 470 232", LO)],
        dots=[(470, 90, "hi"), (470, 140, "hi"), (470, 195, "lo"), (470, 232, "lo")],
        texts=[(118, y, f"운동 {i + 1}", "right", 0) for i, y in enumerate(starts)]
        + [(488, 115, "$F$", "left", 3), (470, 30, r"$\mathcal{S}$", "center", 4)],
        legend=[(120, 284, [HI], "명제가 참인 운동"), (380, 284, [LO], "명제가 거짓인 운동")],
    )


def fig07():
    fig, ax = plt.subplots(figsize=(WIDTH, 3.3))
    for x0 in (0.3, 4.7):
        ax.add_patch(FancyBboxPatch((x0, 0.3), 3.0, 2.4, boxstyle="round,pad=0.02,rounding_size=0.18",
                                    facecolor="none", edgecolor=INK, lw=1.0))
    ax.text(0.62, 2.38, r"$\Omega$", ha="center", va="center", fontsize=FS + 5)
    ax.text(5.02, 2.38, r"$\mathcal{S}$", ha="center", va="center", fontsize=FS + 5)
    left = [(2.55, 2.2), (2.55, 1.72), (2.55, 1.24), (2.55, 0.72)]
    right = [(5.75, 2.0), (5.75, 1.45), (5.75, 0.78)]
    ax.add_patch(FancyBboxPatch((1.25, 1.02), 1.55, 1.42, boxstyle="round,pad=0.02,rounding_size=0.15",
                                facecolor=BLUE, alpha=SOFT, edgecolor="none"))
    ax.add_patch(FancyBboxPatch((5.4, 1.2), 1.15, 1.05, boxstyle="round,pad=0.02,rounding_size=0.15",
                                facecolor=BLUE, alpha=SOFT, edgecolor="none"))
    ax.text(6.95, 1.72, "$F$", ha="center", va="center", fontsize=FS + 3)
    for (x, y), j in zip(left, (0, 0, 1, 2)):
        tx, ty = right[j]
        dy = 0.05 if (x, y) == left[0] else (-0.05 if (x, y) == left[1] else 0.0)
        arrow(ax, (x + 0.1, y), (tx - 0.12, ty + dy), color=GRAY, lw=0.8, ms=8)
    for i, (x, y) in enumerate(left):
        ax.plot([x], [y], "o", color=INK, markersize=5, zorder=5)
        ax.text(x - 0.16, y, f"운동 {i + 1}", ha="right", va="center", fontsize=FS)
    for (x, y), name in zip(right, ("$s$", "$s'$", "$s''$")):
        ax.plot([x], [y], "o", color=INK, markersize=5, zorder=5)
        ax.text(x + 0.18, y, name, ha="left", va="center", fontsize=FS + 3)
    ax.add_patch(Rectangle((0.45, -0.22), 0.5, 0.26, facecolor=BLUE, alpha=SOFT, edgecolor="none"))
    ax.text(1.1, -0.09, "진리집합", ha="left", va="center", fontsize=FS)
    ax.set_xlim(0, 8)
    ax.set_ylim(-0.45, 3)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig


def fig08():
    return timeline(
        280,
        vlines=[(300, 48, 240, "시각 $t$", 262, False), (480, 48, 240, "시각 $t+u$", 262, False)],
        gates=[(480, 62, 118)],
        curves=[("M120 80 C 190 80, 240 130, 300 140 C 360 150, 420 100, 480 90", HI),
                ("M120 210 C 190 210, 240 150, 300 140 C 360 130, 420 190, 480 200", PLAIN)],
        dots=[(480, 90, "hi"), (480, 200, "lo"), (300, 140, "point")],
        texts=[(108, 80, "운동 1", "right", 0), (108, 210, "운동 2", "right", 0), (290, 122, "$s$", "right", 3),
               (496, 88, "$F$", "left", 3), (300, 32, r"$\mathcal{S}$", "center", 4),
               (480, 32, r"$\mathcal{S}$", "center", 4)],
    )


def fig10():
    left = {110: (69, 114, 169), 180: (92, 132, 162), 250: (73, 114, 173)}
    right = {420: (69, 114, 169), 500: (92, 132, 162), 580: (73, 114, 173)}
    return timeline(
        232,
        titles=[(180, 20, "이산 시간"), (500, 20, "연속 시간")],
        vlines=[(64, 54, 190, "", 0, True), (376, 54, 190, "", 0, True),
                (110, 54, 190, "시각 $0$", 210, False), (180, 54, 190, "시각 $1$", 210, False),
                (250, 54, 190, "시각 $2$", 210, False), (420, 54, 190, "시각 $0$", 210, False),
                (500, 54, 190, "시각 $t$", 210, False), (580, 54, 190, "시각 $t+u$", 210, False)],
        curves=[("M420 69 C 453 62, 472 99, 500 92 C 528 84, 552 62, 580 73", LO),
                ("M420 114 C 453 129, 472 121, 500 132 C 528 143, 552 121, 580 114", LO),
                ("M420 169 C 453 173, 472 158, 500 162 C 528 166, 552 177, 580 173", LO)],
        dots=[(x, y, "hi") for col in (left, right) for x, c in col.items() for y in c],
        texts=[(54, 122, r"$\mathcal{S}$", "right", 4), (366, 122, r"$\mathcal{S}$", "right", 4),
               (110, 42, "$S_0$", "center", 3), (180, 42, "$S_1$", "center", 3), (250, 42, "$S_2$", "center", 3),
               (420, 42, "$S_0$", "center", 3), (500, 42, "$S_t$", "center", 3), (580, 42, "$S_{t+u}$", "center", 3)]
        + [(262, y, f"운동 {i + 1}", "left", 0) for i, y in enumerate(left[250])]
        + [(592, y, f"운동 {i + 1}", "left", 0) for i, y in enumerate(right[580])],
    )


def fig11():
    return timeline(
        304,
        vlines=[(250, 62, 245, "시각 $t$", 266, False), (450, 62, 245, "시각 $t+u$", 266, False)],
        gates=[(250, 70, 132), (450, 95, 155)],
        curves=[("M110 70 C 160 70, 200 80, 250 85 C 320 92, 380 106, 450 110", HI),
                ("M110 110 C 160 110, 200 114, 250 118 C 320 124, 380 196, 450 205", LO),
                ("M110 160 C 160 162, 200 166, 250 170 C 320 176, 380 146, 450 140", LO),
                ("M110 220 C 160 220, 200 216, 250 215 C 320 214, 380 226, 450 228", LO)],
        dots=[(250, 85, "hi"), (250, 118, "hi"), (250, 170, "lo"), (250, 215, "lo"),
              (450, 110, "hi"), (450, 205, "lo"), (450, 140, "hi"), (450, 228, "lo")],
        texts=[(250, 46, "$F_1$", "center", 3), (466, 124, "$F_2$", "left", 3)],
        legend=[(100, 288, [HI], r"$S_t^{-1}(F_1)\cap S_{t+u}^{-1}(F_2)$"), (400, 288, [LO], "그 밖의 운동")],
    )


def fig12():
    return timeline(
        290,
        titles=[(180, 28, "운동을 정했을 때"), (500, 28, "운동을 정하지 않았을 때")],
        vlines=[(230, 48, 226, "시각 $t$", 246, False), (550, 48, 226, "시각 $t$", 246, False)],
        curves=[("M60 70 C 120 75, 170 60, 230 70 C 260 75, 290 78, 310 78", LO),
                ("M60 210 C 120 205, 170 190, 230 195 C 260 197, 290 205, 310 210", LO),
                ("M60 150 C 120 150, 170 110, 230 120 C 260 125, 290 140, 310 150", HI),
                ("M380 225 C 450 228, 520 200, 630 215", LO),
                ("M380 70 C 440 70, 500 120, 550 130 C 580 136, 610 172, 630 182", HI),
                ("M380 140 C 440 140, 500 132, 550 130 C 580 129, 610 136, 630 138", HI),
                ("M380 195 C 440 195, 500 140, 550 130 C 580 124, 610 98, 630 90", HI)],
        dots=[(230, 120, "point"), (550, 130, "point")],
        texts=[(240, 104, "$s$", "left", 3), (560, 110, "$s$", "left", 3)],
        legend=[(60, 272, [HI], "정한 운동"), (380, 272, [HI], r"$S_t^{-1}(\{s\})$")],
    )


def fig13():
    fig, (a, b) = plt.subplots(1, 2, figsize=(WIDTH, 3.5))
    motion_table(a, column=2, outline={(1, 2): POINT}, title="한 칸과 한 열", top=[(2, r"$S_t$")])
    motion_table(b, outline={(r, 2): BLUE for r in range(4)}, names=range(4), title="행들의 집합",
                 top=[(2, r"$F=\{$동$\}$")],
                 legend=(("outline", "$F$ 안의 칸"), ("fill", "$S_t^{-1}(F)$")))
    a.set_ylim(b.get_ylim())
    fig.subplots_adjust(left=0.01, right=0.99, bottom=0.02, top=0.98, wspace=0.05)
    return fig


PAST_LEGEND = [PLAIN, DASH]


def fig14():
    return timeline(
        276,
        titles=[(175, 22, "전제 2가 성립하는 경우"), (515, 22, "성립하지 않는 경우")],
        vlines=[(180, 46, 200, "시각 $t$", 220, False), (270, 46, 200, "시각 $t+u$", 220, False),
                (520, 46, 200, "시각 $t$", 220, False), (610, 46, 200, "시각 $t+u$", 220, False)],
        curves=[("M80 170 C 113 155, 147 140, 180 125", PLAIN), ("M80 80 C 113 95, 147 110, 180 125", DASH),
                ("M180 125 C 210 111.5, 240 98, 270 84.5", HI), ("M180 125 C 210 138.5, 240 152, 270 165.5", HI),
                ("M420 170 C 453 155, 487 140, 520 125", PLAIN), ("M420 80 C 453 95, 487 110, 520 125", DASH),
                ("M520 125 C 550 111.5, 580 98, 610 84.5", PLAIN), ("M520 125 C 550 138.5, 580 152, 610 165.5", DASH)],
        dots=[(270, 84.5, "hi"), (270, 165.5, "hi"), (610, 84.5, "lo"), (610, 165.5, "lo"),
              (180, 125, "point"), (520, 125, "point")],
        texts=[(180, 104, "$s$", "center", 3), (520, 104, "$s$", "center", 3),
               (424, 190, "운동 1", "left", 0), (424, 64, "운동 2", "left", 0),
               (620, 84, "운동 1만", "left", 0), (620, 166, "운동 2만", "left", 0)],
        legend=[(110, 256, PAST_LEGEND, "서로 다른 과거"), (340, 256, [HI], "$u$초 뒤에 놓일 수 있는 state")],
    )


def fig16():
    return timeline(
        304,
        vlines=[(250, 62, 245, "시각 $t$", 266, False), (450, 62, 245, "시각 $t+u$", 266, False)],
        gates=[(250, 70, 132), (450, 92, 178)],
        curves=[("M110 70 C 160 70, 200 80, 250 85 C 320 92, 380 98, 450 100", HI),
                ("M110 110 C 160 110, 200 104, 250 102 C 320 100, 380 128, 450 135", HI),
                ("M110 150 C 160 150, 200 128, 250 122 C 320 114, 380 160, 450 170", HI),
                ("M110 220 C 160 220, 200 216, 250 215 C 320 214, 380 226, 450 228", LO)],
        dots=[(250, 85, "hi"), (250, 102, "hi"), (250, 122, "hi"), (250, 215, "lo"),
              (450, 100, "hi"), (450, 135, "hi"), (450, 170, "hi"), (450, 228, "lo")],
        texts=[(250, 46, "$F$", "center", 3), (466, 135, "$T_u(F)$", "left", 3)],
        legend=[(100, 288, [HI], "시각 $t$에 $F$ 안에 있는 운동"), (400, 288, [LO], "그 밖의 운동")],
    )


def fig20():
    return timeline(
        300,
        titles=[(175, 28, "화살표가 하나일 때"), (500, 28, "화살표가 여럿일 때")],
        vlines=[(180, 50, 232, "시각 $t$", 252, False), (290, 50, 232, "시각 $t+u$", 252, False),
                (500, 50, 232, "시각 $t$", 252, False), (620, 50, 232, "시각 $t+u$", 252, False)],
        curves=[("M60 80 C 110 80, 140 130, 180 140", PLAIN), ("M60 210 C 110 210, 140 150, 180 140", DASH),
                ("M180 140 C 215 150, 255 110, 290 100", HI),
                ("M380 80 C 430 80, 460 130, 500 140", PLAIN), ("M380 210 C 430 210, 460 150, 500 140", DASH),
                ("M500 140 C 540 140, 580 90, 620 82", HI), ("M500 140 C 540 142, 580 146, 620 145", HI),
                ("M500 140 C 540 140, 580 195, 620 205", HI)],
        dots=[(290, 100, "hi"), (620, 82, "hi"), (620, 145, "hi"), (620, 205, "hi"),
              (180, 140, "point"), (500, 140, "point")],
        texts=[(172, 122, "$s$", "right", 3), (492, 122, "$s$", "right", 3), (300, 94, "$s'$", "left", 3),
               (630, 76, "$s'$", "left", 3), (548, 96, r"$\mathcal{P}_{ss'}$", "center", 2)],
        legend=[(110, 282, PAST_LEGEND, "서로 다른 과거"), (380, 282, [HI], "시각 $t$ 뒤의 운동")],
    )


FIGURES = [
    ("01-fig01-room-and-camera", fig01), ("01-fig02-views", fig02), ("01-fig03-uncut-tip", fig03),
    ("01-fig04-state-space", fig04), ("01-fig05-motions-and-states", fig05), ("01-fig06-truth-set", fig06),
    ("01-fig07-motions-to-states", fig07), ("01-fig08-same-state-different-later", fig08),
    ("01-fig09-symbol-map", fig09), ("01-fig10-state-at-each-time", fig10), ("01-fig11-two-times", fig11),
    ("01-fig12-one-state-and-event", fig12), ("01-fig13-table", fig13),
    ("01-fig14-past-independence", fig14), ("01-fig15-operator-and-arrow", fig15),
    ("01-fig16-two-gates", fig16), ("01-fig17-composition", fig17), ("01-fig18-examples", fig18),
    ("01-fig19-graph-and-flow", fig19), ("01-fig20-one-or-many", fig20),
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--png", type=Path, default=None, help="확인용 PNG를 쓸 폴더")
    args = ap.parse_args()
    setup()
    check_values()
    if args.png:
        args.png.mkdir(parents=True, exist_ok=True)
    for name, make in FIGURES:
        fig = make()
        fig.savefig(HERE / f"{name}.svg", metadata={"Date": None})
        if args.png:
            fig.savefig(args.png / f"{name}.png", dpi=100)
        plt.close(fig)
        print("wrote", name)


if __name__ == "__main__":
    main()
