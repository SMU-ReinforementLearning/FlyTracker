"""01-camera-markov-process.md의 그림 열네 장을 만든다.

    python docs/mdp/figures/make_figures.py            # SVG 열네 장을 이 폴더에 쓴다
    python docs/mdp/figures/make_figures.py --png DIR  # 확인용 PNG도 DIR에 쓴다

그림의 내용과 값은 docs/mdp/01-figures.md를 따른다.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager as fm
from matplotlib.patches import (Circle, Ellipse, FancyArrowPatch,
                                FancyBboxPatch, Polygon, Rectangle, Wedge)

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
    if top is not None:
        c, text = top
        x, y, w, h = cell(-1, c)
        ax.text(x + w / 2, ytop + 0.22, text, ha="center", va="bottom", fontsize=FS + 2, color=BLUE)
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
                ax.plot([x1, x2], [y1, y2], color=GRAY, lw=0.8, zorder=1)
    faces = [f for f in faces if len(f) >= 3]
    faces.sort(key=lambda f: -float(np.dot(np.mean(f, axis=0), fwd)))
    for f in faces:
        ax.add_patch(Polygon([pr(v) for v in f], closed=True, facecolor=BLUE, alpha=0.22,
                             edgecolor=BLUE, lw=0.8, zorder=2))
    x0, y0 = pr(p0)
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

    for yaw, color, name in ((30, BLUE, "$q$"), (150, ORANGE, "$q'$"), (270, GREEN, "$q''$")):
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
    ax.annotate(r"$\mathrm{View}(q)$", (far[0], far[1]), xytext=(5.0, 3.5), fontsize=FS + 2,
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
    ax.add_patch(Wedge(p0, 0.8, -32.5, 12.5, facecolor=POINT, alpha=0.55, edgecolor="none"))
    ax.add_patch(Circle(p0, 0.8, facecolor="none", edgecolor=INK, lw=0.9, linestyle="--"))
    ax.plot([p0[0]], [p0[1]], "o", color=INK, markersize=5, zorder=6)
    ax.text(1.72, 1.0, r"$p_0$", ha="center", va="center", fontsize=FS + 3)
    ax.text(1.55, 1.95, r"$D$", ha="center", va="center", fontsize=FS + 3)
    ax.text(0.5, 3.6, r"$\mathrm{Room}$", ha="center", va="center", fontsize=FS + 3)
    ax.text(3.35, 0.85, r"$\mathrm{View}(q)$", ha="center", va="center", fontsize=FS + 2, color=BLUE)
    tip = p0 + 3.5 * dhi
    ax.text(tip[0] + 0.1, tip[1] + 0.22, r"$\mathrm{Cone}(q)$", ha="center", va="center", fontsize=FS + 2)
    ax.set_xlim(-0.4, 6.0)
    ax.set_ylim(-1.1, 4.3)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig


THREE = (((30, 0), BLUE), ((150, 30), ORANGE), ((270, -30), GREEN))


def fig04():
    fig, (a, b) = plt.subplots(1, 2, figsize=(WIDTH, 3.3), gridspec_kw={"width_ratios": [1, 1.45]})
    R, ry, h0, h1, front = 1.0, 0.4, -1.0, 1.0, 210.0
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
        a.plot([x], [y], "o", markersize=8, markerfacecolor=color if vis else "white",
               markeredgecolor=color, markeredgewidth=1.6, zorder=5)
    for yaw, name in ((0, "북"), (90, "동"), (180, "남"), (270, "서")):
        rel = math.radians(yaw - front)
        a.text(0.62 * R * math.sin(rel), h1 - 0.62 * ry * math.cos(rel), name, ha="center", va="center", fontsize=FS)
    a.text(R + 0.4, h1 + 0.25, r"$\mathcal{S}$", ha="center", va="center", fontsize=FS + 5)
    arrow(a, (-R - 0.3, h0), (-R - 0.3, h1), color=INK, lw=0.8)
    a.text(-R - 0.42, 0, r"$s_{\mathrm{pitch}}$", ha="right", va="center", fontsize=FS + 1)
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

def fig05():
    fig, ax = plt.subplots(figsize=(WIDTH, 3.9))
    motion_table(ax, outline={(r, 2): BLUE for r in range(4)}, names=range(4),
                 legend=(("outline", "$F$ 안의 칸"), ("fill", "$S_t^{-1}(F)$")))
    return fig


def fig06():
    fig, ax = plt.subplots(figsize=(WIDTH, 3.0))
    motion_table(ax, outline={(0, 2): GRAY, (1, 2): GRAY, (0, 3): BLUE, (1, 3): BLUE}, names=(0, 1))
    return fig


def fig07():
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


def fig08():
    fig, ax = plt.subplots(figsize=(WIDTH, 3.9))
    out = {(r, 2): BLUE for r in range(4)}
    out.update({(r, 3): BLUE for r in (0, 2, 4)})
    motion_table(ax, outline=out, names=(0, 2),
                 legend=(("outline", "조건에 맞는 칸"), ("fill", r"$S_t^{-1}(F_1)\cap S_{t+u}^{-1}(F_2)$")))
    return fig


def fig09():
    fig, (a, b) = plt.subplots(1, 2, figsize=(WIDTH, 2.6))
    motion_table(a, outline={(1, 2): POINT}, names=(1,), title="운동을 정했을 때")
    motion_table(b, column=2, title="운동을 정하지 않았을 때", top=(2, r"$S_t$"))
    a.set_ylim(b.get_ylim())
    fig.subplots_adjust(left=0.01, right=0.99, bottom=0.02, top=0.98, wspace=0.05)
    return fig


# ---------- 그림 10 ~ 14: flow ----------

def fig10():
    fig, ax = plt.subplots(figsize=(WIDTH, 3.3))
    L, M, Rr = 1.2, 3.6, 6.0
    past = [(L, 2.25), (L, 0.95)]
    nxt = [(Rr, 2.25), (Rr, 0.95)]
    mid = (M, 1.6)
    r = 0.2
    for (x, y), ls in zip(past, ("-", "--")):
        arrow(ax, (x + r, y), (M - r - 0.03, mid[1] + (0.07 if y > mid[1] else -0.07)), color=GRAY, lw=1.4, ms=12, ls=ls)
        ax.add_patch(Circle((x, y), r, facecolor="white", edgecolor=GRAY, lw=1.4, zorder=4))
    for (x, y) in nxt:
        arrow(ax, (M + r, mid[1] + (0.07 if y > mid[1] else -0.07)), (x - r - 0.03, y), color=BLUE, lw=1.6, ms=12)
        ax.add_patch(Circle((x, y), r, facecolor=BLUE, alpha=0.30, edgecolor="none", zorder=4))
        ax.add_patch(Circle((x, y), r, facecolor="none", edgecolor=BLUE, lw=1.4, zorder=5))
    ax.add_patch(Circle(mid, r, facecolor=POINT, edgecolor=POINT, lw=1.4, zorder=5))
    ax.text(M, mid[1] + 0.42, r"$s$", ha="center", va="center", fontsize=FS + 4)
    for x, t in ((L, "시각 $t$ 이전"), (M, "시각 $t$"), (Rr, "시각 $t+u$")):
        ax.text(x, 3.0, t, ha="center", va="center", fontsize=FS + 1)
    y = 0.1
    ax.plot([0.5, 0.95], [y, y], color=GRAY, lw=1.4)
    ax.plot([1.05, 1.5], [y, y], color=GRAY, lw=1.4, linestyle="--")
    ax.text(1.65, y, "서로 다른 과거", ha="left", va="center", fontsize=FS)
    ax.plot([3.75, 4.2], [y, y], color=BLUE, lw=1.6)
    ax.text(4.35, y, "$u$초 뒤에 놓일 수 있는 state", ha="left", va="center", fontsize=FS)
    ax.set_xlim(0.2, 7.6)
    ax.set_ylim(-0.2, 3.3)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig


def fig11():
    fig, ax = plt.subplots(figsize=(WIDTH, 3.5))
    unrolled(ax)
    f0, f1 = (30.0, -50.0), (70.0, -20.0)
    g0, g1 = ex2(f0, 1.5), ex2(f1, 1.5)
    ax.add_patch(Rectangle(f0, f1[0] - f0[0], f1[1] - f0[1], facecolor=BLUE, alpha=SOFT, edgecolor="none"))
    ax.add_patch(Rectangle(g0, g1[0] - g0[0], g1[1] - g0[1], facecolor=BLUE, alpha=SOFT, edgecolor="none"))
    ax.add_patch(Rectangle(g0, g1[0] - g0[0], g1[1] - g0[1], facecolor="none", edgecolor=BLUE, lw=1.3))
    for c in ((30, -50), (70, -50), (30, -20), (70, -20)):
        arrow(ax, c, ex2(c, 1.5), color=GRAY, lw=0.8, ms=8)
    s = (50.0, -35.0)
    s2 = ex2(s, 1.5)
    arrow(ax, s, s2, color=POINT, lw=1.8, ms=12, z=5)
    ax.plot([s[0], s2[0]], [s[1], s2[1]], "o", color=POINT, markersize=5, zorder=6)
    ax.text(s[0] + 2, s[1] - 7, r"$s$", ha="center", va="center", fontsize=FS + 3)
    ax.text(s2[0] + 1, s2[1] + 8, r"$s'$", ha="center", va="center", fontsize=FS + 3)
    ax.text(18, -35, r"$F$", ha="center", va="center", fontsize=FS + 3)
    ax.text(140, -6, r"$T_u(F)$", ha="center", va="center", fontsize=FS + 3)
    fig.subplots_adjust(left=0.12, right=0.95, bottom=0.22, top=0.96)
    return fig


def fig12():
    fig, ax = plt.subplots(figsize=(WIDTH, 3.5))
    unrolled(ax)
    s = (40.0, -50.0)
    s1 = ex2(s, 2)
    s2 = ex2(s1, 3)
    arrow(ax, s, s2, color=POINT, lw=1.6, ms=12, z=3)
    arrow(ax, s, s1, color=BLUE, lw=1.8, ms=12, z=4)
    arrow(ax, s1, s2, color=BLUE, lw=1.8, ms=12, z=4)
    ax.plot([s[0], s1[0], s2[0]], [s[1], s1[1], s2[1]], "o", color=INK, markersize=5, zorder=6)
    ax.text(s[0] - 8, s[1], r"$s$", ha="center", va="center", fontsize=FS + 3)
    ax.text(s1[0] - 4, s1[1] + 11, r"$s'$", ha="center", va="center", fontsize=FS + 3)
    ax.text(s2[0] + 9, s2[1] + 2, r"$s''$", ha="center", va="center", fontsize=FS + 3)
    ax.text(60, -22, r"$t$", ha="center", va="center", fontsize=FS + 3, color=BLUE)
    ax.text(140, 14, r"$u$", ha="center", va="center", fontsize=FS + 3, color=BLUE)
    ax.text(130, -32, r"$t+u$", ha="center", va="center", fontsize=FS + 3, color=POINT)
    fig.subplots_adjust(left=0.12, right=0.95, bottom=0.22, top=0.96)
    return fig


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


def fig13():
    fig, (a, b) = plt.subplots(1, 2, figsize=(WIDTH, 2.6))
    unrolled(a)
    unrolled(b)
    field(a, ex1, mark=(150.0, 0.0))
    field(b, ex2)
    b.axhline(20, color=INK, lw=0.8, linestyle=":")
    b.text(352, 27, r"$a$", ha="right", va="center", fontsize=FS + 2)
    a.set_title("Example 1", fontsize=FS + 1)
    b.set_title("Example 2", fontsize=FS + 1)
    b.set_ylabel("")
    fig.subplots_adjust(left=0.1, right=0.955, bottom=0.3, top=0.88, wspace=0.24)
    return fig


def fig14():
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


FIGURES = [
    ("01-fig01-room-and-camera", fig01), ("01-fig02-views", fig02), ("01-fig03-uncut-tip", fig03),
    ("01-fig04-state-space", fig04), ("01-fig05-motions-and-truth-set", fig05),
    ("01-fig06-same-state-different-later", fig06), ("01-fig07-symbol-map", fig07),
    ("01-fig08-two-times", fig08), ("01-fig09-cell-and-column", fig09),
    ("01-fig10-past-independence", fig10), ("01-fig11-operator-and-arrow", fig11),
    ("01-fig12-composition", fig12), ("01-fig13-examples", fig13), ("01-fig14-graph-and-flow", fig14),
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
        fig.savefig(HERE / f"{name}.svg")
        if args.png:
            fig.savefig(args.png / f"{name}.png", dpi=100)
        plt.close(fig)
        print("wrote", name)


if __name__ == "__main__":
    main()
