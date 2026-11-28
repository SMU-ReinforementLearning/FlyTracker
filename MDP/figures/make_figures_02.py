"""02-fly-markov-process.md의 그림 열두 장을 만든다.

    python docs/mdp-v1/figures/make_figures_02.py            # SVG 열두 장을 이 폴더에 쓴다
    python docs/mdp-v1/figures/make_figures_02.py --png DIR  # 확인용 PNG도 DIR에 쓴다

그림의 내용과 값은 docs/mdp-v1/02-figures.md를 따른다. 설정, 색, 시간선 함수는 make_figures.py의 것을 쓴다.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Ellipse, FancyBboxPatch, Polygon, Rectangle, Wedge  # noqa: E402

import make_figures as base  # noqa: E402
from make_figures import (BLUE, DASH, FS, GRAY, HI, INK, LO, PLAIN, POINT, SOFT, WIDTH,  # noqa: E402
                          arrow, bezier, clip, timeline, unrolled)

PAST = ["M120 80 C 190 80, 240 130, 300 140", "M120 210 C 190 210, 240 150, 300 140"]
FAN = ["M300 140 C 350 140, 410 90, 460 82", "M300 140 C 350 142, 410 146, 460 145",
       "M300 140 C 350 140, 410 195, 460 205"]
L_PAST = ["M60 80 C 110 80, 140 130, 180 140", "M60 210 C 110 210, 140 150, 180 140"]
R_PAST = ["M380 80 C 430 80, 460 130, 500 140", "M380 210 C 430 210, 460 150, 500 140"]
R_FAN = ["M500 140 C 540 140, 580 90, 620 82", "M500 140 C 540 142, 580 146, 620 145",
         "M500 140 C 540 140, 580 195, 620 205"]
LEG_PAST = [PLAIN, DASH]
T, TU = "시각 $t$", "시각 $t+u$"


def yaw_of(p, p0=(2.0, 2.0)):
    return math.degrees(math.atan2(p[0] - p0[0], p[1] - p0[1]))


EDGES = {("북", "동"): 0.7, ("북", "북"): 0.3, ("동", "남"): 0.6, ("동", "동"): 0.4,
         ("남", "서"): 0.5, ("남", "남"): 0.5, ("서", "북"): 0.8, ("서", "서"): 0.2}


def check_values() -> None:
    assert abs(yaw_of((3.3, 2.75)) - 60.0) <= 0.1
    assert abs((0.4 - 0.3) / (0.5 - 0.2) - 1 / 3) <= 1e-9
    for n in "북동남서":
        assert abs(sum(v for (a, _), v in EDGES.items() if a == n) - 1.0) <= 1e-9


def fig01():
    fig = base.fig01()
    ax = fig.axes[0]
    p0 = np.array([2.0, 2.0, 1.0])
    psi, th = math.radians(30), math.radians(10)
    ef = np.array([math.cos(th) * math.sin(psi), math.cos(th) * math.cos(psi), math.sin(th)])
    er = np.array([math.cos(psi), -math.sin(psi), 0.0])
    az, el = math.radians(38), math.radians(24)
    right = np.array([math.cos(az), math.sin(az), 0.0])
    fwd = np.array([-math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), -math.sin(el)])
    up = np.cross(right, fwd)

    def pr(v):
        return float(np.dot(v, right)), float(np.dot(v, up))

    fly = p0 + 1.5 * ef
    a, b = pr(fly), pr(fly + 0.5 * er)
    arrow(ax, a, b, color=POINT, lw=1.6, ms=11, z=7)
    ax.plot([a[0]], [a[1]], "o", color=POINT, markersize=6, zorder=8)
    ax.annotate("초파리", a, xytext=(a[0] - 0.2, a[1] + 1.0), fontsize=FS + 1,
                arrowprops=dict(arrowstyle="-", color=GRAY, lw=0.7), ha="center", va="center")
    return fig


def fig02():
    return timeline(
        280,
        vlines=[(300, 40, 222, T, 238, False), (480, 40, 222, TU, 238, False)],
        curves=[(PAST[0], PLAIN), (PAST[1], DASH),
                ("M300 140 C 360 150, 420 110, 480 100 C 520 94, 560 96, 600 92", HI)],
        dots=[(300, 140, "point"), (480, 100, "hi")],
        texts=[(292, 120, r"$s_{\mathrm{cam}}$", "right", 3), (490, 82, r"$s'_{\mathrm{cam}}$", "left", 3)],
        legend=[(120, 266, LEG_PAST, "서로 다른 과거"), (400, 266, [HI], "시각 $t$ 뒤의 운동")],
    )


def fig03():
    fig = plt.figure(figsize=(WIDTH, 3.3))
    a = fig.add_axes([0.09, 0.42, 0.4, 0.46])
    b = fig.add_axes([0.6, 0.36, 0.32, 0.56])
    unrolled(a)
    a.plot([30], [10], "o", color=POINT, markersize=7, zorder=6)
    a.text(48, 24, r"$s_{\mathrm{cam}}$", ha="left", va="center", fontsize=FS + 3)
    b.add_patch(Rectangle((0, 0), 4, 3, facecolor="none", edgecolor=INK, lw=1.0))
    b.text(2, 3.25, "화면", ha="center", va="center", fontsize=FS + 1)
    arrow(b, (2.7, 1.9), (2.05, 1.35), color=POINT, lw=1.6, ms=11, z=5)
    b.plot([2.7], [1.9], "o", color=POINT, markersize=7, zorder=6)
    b.text(2.9, 2.2, r"$s_{\mathrm{fly}}$", ha="left", va="center", fontsize=FS + 3)
    b.set_xlim(-0.1, 4.1)
    b.set_ylim(-0.1, 3.5)
    b.set_aspect("equal")
    b.axis("off")
    c = fig.add_axes([0, 0, 1, 0.2])
    c.set_xlim(0, 1)
    c.set_ylim(0, 1)
    c.axis("off")
    c.plot([0.12, 0.12, 0.9, 0.9], [0.95, 0.72, 0.72, 0.95], color=GRAY, lw=0.9)
    c.text(0.51, 0.34, r"$s=(s_{\mathrm{cam}},\,s_{\mathrm{fly}})$", ha="center", va="center", fontsize=FS + 4)
    return fig


def fig04():
    fig, ax = plt.subplots(figsize=(WIDTH, 4.4))
    ax.add_patch(Rectangle((0, 0), 4, 4, facecolor="none", edgecolor=INK, lw=1.0))
    p0 = np.array([2.0, 2.0])
    sq = [(np.array([1.0, 0.0]), 4.0), (np.array([-1.0, 0.0]), 0.0),
          (np.array([0.0, 1.0]), 4.0), (np.array([0.0, -1.0]), 0.0)]

    def d(yaw):
        r = math.radians(yaw)
        return np.array([math.sin(r), math.cos(r)])

    poly = [p0, p0 + 20 * d(0), p0 + 20 * d(60)]
    for n, dd in sq:
        poly = clip(poly, n, dd)
    ax.add_patch(Polygon(poly, closed=True, facecolor=BLUE, alpha=SOFT, edgecolor="none"))
    ax.add_patch(Polygon(poly, closed=True, facecolor="none", edgecolor=BLUE, lw=0.9))
    from matplotlib.patches import PathPatch
    ax.add_patch(PathPatch(bezier("M2.6 3.4 C 3.0 3.5, 3.3 3.2, 3.3 2.75"), fill=False,
                           edgecolor=BLUE, lw=2.0, zorder=4))
    ax.add_patch(PathPatch(bezier("M3.3 2.75 C 3.4 2.5, 3.2 2.2, 2.9 2.0"), fill=False,
                           edgecolor=GRAY, lw=1.5, linestyle="--", zorder=4))
    ax.plot([2.6], [3.4], "o", color=BLUE, markersize=6.5, zorder=6)
    ax.plot([3.3], [2.75], "o", color=POINT, markersize=7, zorder=6)
    ax.plot([2], [2], "o", color=INK, markersize=5, zorder=6)
    ax.text(1.78, 2.2, r"$p_0$", ha="center", va="center", fontsize=FS + 3)
    ax.text(0.45, 3.7, r"$\mathrm{Room}$", ha="center", va="center", fontsize=FS + 2)
    ax.annotate(r"$s_{\mathrm{end}}$", (3.3, 2.75), xytext=(4.75, 2.45), fontsize=FS + 3,
                arrowprops=dict(arrowstyle="-", color=GRAY, lw=0.7), ha="center", va="center")
    ax.annotate(r"$\mathrm{View}(s_{\mathrm{cam}})$", (3.6, 3.75), xytext=(5.05, 3.6), fontsize=FS + 2,
                arrowprops=dict(arrowstyle="-", color=GRAY, lw=0.7), ha="center", va="center")
    ax.plot([0.3, 0.75], [-0.42, -0.42], color=BLUE, lw=2.0)
    ax.text(0.85, -0.42, "화면 안의 초파리", ha="left", va="center", fontsize=FS)
    ax.plot([2.9, 3.35], [-0.42, -0.42], color=GRAY, lw=1.5, linestyle="--")
    ax.text(3.45, -0.42, "화면 밖", ha="left", va="center", fontsize=FS)
    ax.set_xlim(-0.7, 6.2)
    ax.set_ylim(-0.75, 4.3)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig


def fig05():
    return timeline(
        300,
        vlines=[(180, 50, 232, T, 252, False), (290, 50, 232, TU, 252, False),
                (500, 50, 232, T, 252, False), (620, 50, 232, TU, 252, False)],
        curves=[(L_PAST[0], PLAIN), (L_PAST[1], DASH), ("M180 140 C 215 150, 255 110, 290 100", HI),
                (R_PAST[0], PLAIN), (R_PAST[1], DASH)] + [(c, HI) for c in R_FAN],
        dots=[(180, 140, "point"), (290, 100, "hi"), (500, 140, "point"),
              (620, 82, "hi"), (620, 145, "hi"), (620, 205, "hi")],
        texts=[(176, 106, r"$s_{\mathrm{cam}}$", "right", 3), (298, 86, r"$s'_{\mathrm{cam}}$", "left", 3),
               (496, 106, r"$s_{\mathrm{fly}}$", "right", 3)],
        titles=[(180, 28, "카메라의 state"), (520, 28, "초파리의 state")],
        legend=[(120, 282, LEG_PAST, "서로 다른 과거"), (400, 282, [HI], "시각 $t$ 뒤의 운동")],
    )


def fig06():
    return timeline(
        300,
        vlines=[(300, 40, 235, T, 255, False), (460, 40, 235, TU, 255, False)],
        curves=[(PAST[0], PLAIN), (PAST[1], DASH)] + [(c, HI) for c in FAN],
        gates=[(460, 70, 217)],
        dots=[(300, 140, "point"), (460, 82, "hi"), (460, 145, "hi"), (460, 205, "hi")],
        texts=[(292, 120, "$s$", "right", 3), (474, 112, r"$T_u(\{s\})$", "left", 3)],
        legend=[(120, 282, LEG_PAST, "서로 다른 과거"), (400, 282, [HI], "시각 $t$ 뒤의 운동")],
    )


def fig07():
    fig, ax = plt.subplots(figsize=(WIDTH, WIDTH * 0.4))
    h = 1.0
    ax.add_patch(Rectangle((0.3, 0), 0.1, h, facecolor=BLUE, alpha=SOFT, edgecolor="none"))
    ax.plot([0.2, 0.2, 0.5, 0.5], [0, h, h, 0], color=INK, lw=1.2)
    ax.plot([0.3, 0.3], [0, h], color=POINT, lw=1.6)
    ax.text(0.35, h / 2, r"$\frac{1}{3}$", ha="center", va="center", fontsize=FS + 7)
    ax.text(0.3, h + 0.13, "$0$", ha="center", va="center", fontsize=FS + 3, color=POINT)
    ax.set_xlim(0.1, 0.6)
    ax.set_ylim(0, 1.45)
    ax.set_xticks([0.2, 0.3, 0.4, 0.5])
    ax.set_yticks([])
    ax.set_xlabel("빠르기 (m/s)")
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    fig.subplots_adjust(left=0.12, right=0.88, bottom=0.2, top=0.95)
    return fig


def fig08():
    return timeline(
        300,
        vlines=[(300, 40, 235, T, 255, False), (460, 40, 235, TU, 255, False)],
        curves=[(PAST[0], PLAIN), (PAST[1], DASH), (FAN[0], HI), (FAN[1], HI), (FAN[2], LO)],
        gates=[(460, 70, 157)],
        dots=[(300, 140, "point"), (460, 82, "hi"), (460, 145, "hi"), (460, 205, "lo")],
        texts=[(292, 120, "$s$", "right", 3), (474, 112, "$F$", "left", 3)],
        legend=[(90, 282, [HI], "시각 $t+u$에 $F$ 안에 놓이는 운동"), (440, 282, [LO], "그 밖의 운동")],
    )


def fig09():
    lfan = ["M180 140 C 220 140, 260 90, 300 82", "M180 140 C 220 142, 260 146, 300 145",
            "M180 140 C 220 140, 260 195, 300 205"]
    return timeline(
        300,
        vlines=[(180, 50, 232, T, 252, False), (300, 50, 232, TU, 252, False),
                (500, 50, 232, T, 252, False), (620, 50, 232, TU, 252, False)],
        curves=[(L_PAST[0], PLAIN), (L_PAST[1], DASH)] + [(c, HI) for c in lfan]
               + [(R_PAST[0], PLAIN), (R_PAST[1], DASH)] + [(c, HI) for c in R_FAN],
        gates=[(300, 70, 217), (620, 70, 157)],
        dots=[(180, 140, "point"), (300, 82, "hi"), (300, 145, "hi"), (300, 205, "hi"),
              (500, 140, "point"), (620, 82, "hi"), (620, 145, "hi"), (620, 205, "hi")],
        texts=[(174, 120, "$s$", "right", 3), (312, 112, r"$T_u(\{s\})$", "left", 3),
               (494, 120, "$s$", "right", 3), (632, 112, "$F$", "left", 3),
               (612, 58, r"$\mathcal{P}_u(s,F)$", "right", 2)],
        titles=[(190, 26, "flow의 조건 2"), (520, 26, "Definition 3")],
        legend=[(120, 282, LEG_PAST, "서로 다른 과거"), (400, 282, [HI], "시각 $t$ 뒤의 운동")],
    )


def fig10():
    thin = dict(color=BLUE, lw=1.2, alpha=0.6)
    fig = timeline(
        300,
        vlines=[(200, 40, 262, T, 282, False), (480, 40, 262, TU, 282, False)],
        curves=[("M200 150 C 290 150, 390 150, 480 150", HI),
                ("M260 150 C 330 140, 410 95, 480 80", thin), ("M320 150 C 380 148, 430 118, 480 108", thin),
                ("M300 150 C 370 160, 430 190, 480 200", thin), ("M380 150 C 420 152, 450 172, 480 178", thin),
                ("M240 150 C 300 170, 360 235, 420 250", LO)],
        gates=[(480, 70, 118), (480, 168, 210)],
        dots=[(200, 150, "point"), (480, 150, "hi"), (480, 80, "hi"), (480, 108, "hi"),
              (480, 200, "hi"), (480, 178, "hi"), (420, 250, "lo")],
        texts=[(190, 132, "$s$", "right", 3), (494, 150, r"$s'$", "left", 3), (526, 150, r"$e^{-ku}$", "left", 3),
               (494, 94, r"$1-e^{-ku}$", "left", 3), (432, 250, r"$s_{\mathrm{end}}$", "left", 3)],
    )
    fig.axes[0].plot([578, 590, 590, 494], [94, 94, 189, 189], color=GRAY, lw=0.8)
    return fig


def fig11():
    first = ["M150 150 C 210 150, 260 100, 320 90", "M150 150 C 210 150, 260 150, 320 150",
             "M150 150 C 210 150, 260 205, 320 215"]
    second = [("M320 90 C 380 88, 430 82, 490 80", True), ("M320 90 C 380 96, 430 118, 490 125", True),
              ("M320 150 C 380 144, 430 116, 490 110", True), ("M320 150 C 380 156, 430 178, 490 185", False),
              ("M320 215 C 380 212, 430 204, 490 200", False), ("M320 215 C 380 220, 430 236, 490 240", False)]
    ends = [(80, True), (125, True), (110, True), (185, False), (200, False), (240, False)]
    return timeline(
        304,
        vlines=[(150, 40, 252, "시각 $0$", 268, False), (320, 40, 252, T, 268, False),
                (490, 40, 252, TU, 268, False)],
        curves=[(first[0], HI), (first[1], HI), (first[2], LO)] + [(c, HI if on else LO) for c, on in second],
        gates=[(490, 70, 135)],
        dots=[(150, 150, "point"), (320, 90, "hi"), (320, 150, "hi"), (320, 215, "lo")]
             + [(490, y, "hi" if on else "lo") for y, on in ends],
        texts=[(140, 132, "$s$", "right", 3), (326, 166, r"$s'$", "left", 3), (504, 100, "$F$", "left", 3)],
        legend=[(90, 290, [HI], "시각 $t+u$에 $F$ 안에 놓이는 운동"), (440, 290, [LO], "그 밖의 운동")],
    )


def fig12():
    fig = plt.figure(figsize=(WIDTH, 3.0))
    a = fig.add_axes([0.0, 0.02, 0.4, 0.96])
    m = fig.add_axes([0.4, 0.02, 0.2, 0.96])
    b = fig.add_axes([0.6, 0.1, 0.39, 0.8])
    pos = {"북": (0, 1.25), "동": (1.25, 0), "남": (0, -1.25), "서": (-1.25, 0)}
    ang = {"북": 90, "동": 0, "남": 270, "서": 180}
    h = 0.3
    order = ["북", "동", "남", "서"]
    for i, name in enumerate(order):
        x, y = pos[name]
        a.add_patch(Rectangle((x - h, y - h), 2 * h, 2 * h, facecolor="white", edgecolor=INK, lw=1.0, zorder=3))
        a.add_patch(Wedge((x, y), h * 0.95, ang[name] - 30, ang[name] + 30, facecolor=BLUE, alpha=0.4,
                          edgecolor="none", zorder=4))
        a.plot([x], [y], "o", color=INK, markersize=3, zorder=5)
        nxt = order[(i + 1) % 4]
        nx, ny = pos[nxt]
        d = np.array([nx - x, ny - y]) / math.hypot(nx - x, ny - y)
        arrow(a, (x + 0.48 * d[0], y + 0.48 * d[1]), (nx - 0.48 * d[0], ny - 0.48 * d[1]),
              color=INK, lw=1.0, ms=10, rad=-0.22)
        mid = np.array([(x + nx) / 2, (y + ny) / 2])
        out = mid / np.linalg.norm(mid)
        a.text(*(mid + 0.42 * out), f"{EDGES[(name, nxt)]:.1f}", ha="center", va="center", fontsize=FS)
        r = math.radians(ang[name])
        ux, uy = math.cos(r), math.sin(r)
        px, py = -uy, ux
        p1 = (x + (h + 0.03) * ux + 0.16 * px, y + (h + 0.03) * uy + 0.16 * py)
        p2 = (x + (h + 0.03) * ux - 0.16 * px, y + (h + 0.03) * uy - 0.16 * py)
        arrow(a, p1, p2, color=INK, lw=1.0, ms=8, rad=-1.9)
        a.text(x + 0.98 * ux, y + 0.98 * uy, f"{EDGES[(name, name)]:.1f}", ha="center", va="center", fontsize=FS)
        a.text(x - 0.5 * px - 0.05 * ux, y - 0.5 * py - 0.05 * uy, name, ha="center", va="center", fontsize=FS)
    a.set_xlim(-2.6, 2.6)
    a.set_ylim(-2.55, 2.55)
    a.set_aspect("equal")
    a.axis("off")
    m.axis("off")
    m.set_xlim(0, 1)
    m.set_ylim(0, 1)
    m.text(0.02, 0.5, "간선의 수", ha="left", va="center", fontsize=FS)
    m.annotate("", xy=(0.72, 0.5), xytext=(0.48, 0.5), arrowprops=dict(arrowstyle="<->", color=GRAY, lw=0.9))
    m.text(0.76, 0.5, "kernel", ha="left", va="center", fontsize=FS)
    b.add_patch(FancyBboxPatch((0.2, 0.3), 3.6, 2.4, boxstyle="round,pad=0.02,rounding_size=0.18",
                               facecolor="none", edgecolor=INK, lw=1.0))
    b.text(0.55, 2.38, r"$\mathcal{S}$", ha="center", va="center", fontsize=FS + 5)
    b.add_patch(Ellipse((2.9, 1.35), 1.2, 1.3, facecolor=BLUE, alpha=SOFT, edgecolor="none"))
    b.add_patch(Ellipse((2.9, 1.35), 1.2, 1.3, facecolor="none", edgecolor=BLUE, lw=1.2))
    b.text(2.9, 1.35, "$F$", ha="center", va="center", fontsize=FS + 4)
    arrow(b, (0.95, 1.35), (2.28, 1.35), color=BLUE, lw=1.6, ms=13)
    b.plot([0.85], [1.35], "o", color=POINT, markersize=7, zorder=6)
    b.text(0.85, 1.05, "$s$", ha="center", va="center", fontsize=FS + 3)
    b.text(1.6, 1.62, r"$\mathcal{P}_u(s,F)$", ha="center", va="center", fontsize=FS + 2, color=BLUE)
    b.set_xlim(0, 4)
    b.set_ylim(0, 3)
    b.set_aspect("equal")
    b.axis("off")
    return fig


FIGURES = [("02-fig01-room-camera-fly", fig01), ("02-fig02-one-continuation", fig02), ("02-fig03-pair", fig03),
           ("02-fig04-end", fig04), ("02-fig05-components", fig05), ("02-fig06-many-continuations", fig06),
           ("02-fig07-point-and-region", fig07), ("02-fig08-kernel", fig08),
           ("02-fig09-possible-and-probable", fig09), ("02-fig10-example", fig10),
           ("02-fig11-composition", fig11), ("02-fig12-graph-and-kernel", fig12)]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--png", type=Path, default=None, help="확인용 PNG를 쓸 폴더")
    args = ap.parse_args()
    base.setup()
    plt.rcParams["svg.hashsalt"] = "02-figures"
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
