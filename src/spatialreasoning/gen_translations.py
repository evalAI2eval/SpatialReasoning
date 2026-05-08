"""
gen_translations.py - generate translation benchmark rows into a task folder's values.csv.

Usage:
    python gen_translations.py <task_folder> <n> [--dim 2|3] [--mode single|multi] [--seed N] [--append]

Arguments:
    task_folder   Path to the task folder (absolute, or relative to this script's tasks/ sibling).
                  e.g.  final_2d_translations_single
                        d:/path/to/PLACEHOLDER_3d_translations_multi
    n             Number of rows to generate.

Options:
    --dim         2 or 3  (default: auto-detected from folder name; falls back to 3)
    --mode        single or multi  (default: auto-detected from folder name; falls back to single)
    --seed        Random seed (default: 42)
    --append      Append to existing values.csv instead of overwriting

Examples:
    python gen_translations.py final_2d_translations_single 20
    python gen_translations.py PLACEHOLDER_3d_translations_multi 15 --append
    python gen_translations.py final_2d_translations_multi 10 --dim 2 --mode multi --seed 7
"""

import argparse
import csv
import os
import random
import sys

DEFAULT_BASE = os.path.join(os.path.dirname(__file__), "tasks")

OBJECTS = [
    "lamp", "vase", "cup", "book", "plant", "clock", "mug",
    "bowl", "candle", "phone", "key", "pen", "bag", "box",
    "bottle", "remote", "pillow", "shoe", "hat", "umbrella"
]

# 2D translation section

DIRECTIONS_2D = ["up", "down", "left", "right"]

VECTORS_2D = {
    "up":    (0,  1),
    "down":  (0, -1),
    "left":  (-1, 0),
    "right": (1,  0),
}

def relative_direction_2d(fx, fy, ax, ay):
    """Return the dominant-axis relative direction between two 2D points.
    Returns None if the two points are the same or if the distances on each axis are tied."""
    dx, dy = fx - ax, fy - ay
    if dx == 0 and dy == 0:
        return None
    adx, ady = abs(dx), abs(dy)
    if adx == ady:
        return None
    if ady > adx:
        return "Up" if dy > 0 else "Down"
    return "Right" if dx > 0 else "Left"

def fmt_pos_2d(x, y):
    return f"({x},{y})"

def build_transformations_2d(steps):
    """Given a list of (distance, direction) pairs, build the transformation description string
    and return the total displacement as (string, total_dx, total_dy)."""
    tdx, tdy = 0, 0
    parts = []
    for dist, d in steps:
        vx, vy = VECTORS_2D[d]
        tdx += dist * vx
        tdy += dist * vy
        parts.append(f"{dist} units {d}")
    return " then ".join(parts), tdx, tdy

def pick_two_objects():
    a, b = random.sample(OBJECTS, 2)
    return a, b

def gen_2d_single(n):
    rows = []
    attempts = 0
    while len(rows) < n and attempts < 10000:
        attempts += 1
        obj, another = pick_two_objects()
        sx, sy = random.randint(-8, 8), random.randint(-8, 8)
        dist = random.randint(2, 8)
        direction = random.choice(DIRECTIONS_2D)
        ax, ay = random.randint(-8, 8), random.randint(-8, 8)
        vx, vy = VECTORS_2D[direction]
        fx, fy = sx + dist * vx, sy + dist * vy
        rel = relative_direction_2d(fx, fy, ax, ay)
        if rel is None:
            continue
        rows.append({
            "object": obj,
            "position": fmt_pos_2d(sx, sy),
            "distance": dist,
            "direction": direction,
            "another_object": another,
            "another_position": fmt_pos_2d(ax, ay),
            "correct_answer": rel,
        })
    return rows

def gen_2d_multi(n):
    rows = []
    attempts = 0
    while len(rows) < n and attempts < 10000:
        attempts += 1
        obj, another = pick_two_objects()
        sx, sy = random.randint(-6, 6), random.randint(-6, 6)
        ax, ay = random.randint(-6, 6), random.randint(-6, 6)
        steps = [(random.randint(2, 6), random.choice(DIRECTIONS_2D)) for _ in range(random.randint(2, 4))]
        trans_str, tdx, tdy = build_transformations_2d(steps)
        rel = relative_direction_2d(sx + tdx, sy + tdy, ax, ay)
        if rel is None:
            continue
        rows.append({
            "object": obj,
            "position": fmt_pos_2d(sx, sy),
            "transformations": trans_str,
            "another_object": another,
            "another_position": fmt_pos_2d(ax, ay),
            "correct_answer": rel,
        })
    return rows

# 3D translation section

DIRECTIONS_3D = ["up", "down", "left", "right", "forward", "backward"]

VECTORS_3D = {
    "up":       (0,  1,  0),
    "down":     (0, -1,  0),
    "left":     (-1, 0,  0),
    "right":    (1,  0,  0),
    "forward":  (0,  0,  1),
    "backward": (0,  0, -1),
}

def relative_direction_3d(fx, fy, fz, ax, ay, az):
    """Return the dominant-axis relative direction between two 3D points.
    Returns None if the two points are the same or if the top two axes are tied."""
    dx, dy, dz = fx - ax, fy - ay, fz - az
    if dx == 0 and dy == 0 and dz == 0:
        return None
    axes = sorted([("x", abs(dx)), ("y", abs(dy)), ("z", abs(dz))], key=lambda t: t[1], reverse=True)
    if axes[0][1] == axes[1][1]:
        return None  # the two largest axes are tied, so there is no clear dominant direction
    dominant = axes[0][0]
    if dominant == "y":
        return "Up" if dy > 0 else "Down"
    if dominant == "x":
        return "Right" if dx > 0 else "Left"
    return "Forward" if dz > 0 else "Backward"

def fmt_pos_3d(x, y, z):
    return f"({x},{y},{z})"

def build_transformations_3d(steps):
    """Given a list of (distance, direction) pairs, build the transformation description string
    and return the total displacement as (string, tdx, tdy, tdz)."""
    tdx, tdy, tdz = 0, 0, 0
    parts = []
    for dist, d in steps:
        vx, vy, vz = VECTORS_3D[d]
        tdx += dist * vx
        tdy += dist * vy
        tdz += dist * vz
        parts.append(f"{dist} units {d}")
    return " then ".join(parts), tdx, tdy, tdz

def gen_3d_single(n):
    rows = []
    attempts = 0
    while len(rows) < n and attempts < 10000:
        attempts += 1
        obj, another = pick_two_objects()
        sx, sy, sz = random.randint(-8, 8), random.randint(-8, 8), random.randint(-8, 8)
        dist = random.randint(2, 8)
        direction = random.choice(DIRECTIONS_3D)
        ax, ay, az = random.randint(-8, 8), random.randint(-8, 8), random.randint(-8, 8)
        vx, vy, vz = VECTORS_3D[direction]
        fx, fy, fz = sx + dist * vx, sy + dist * vy, sz + dist * vz
        rel = relative_direction_3d(fx, fy, fz, ax, ay, az)
        if rel is None:
            continue
        rows.append({
            "object": obj,
            "position": fmt_pos_3d(sx, sy, sz),
            "distance": dist,
            "direction": direction,
            "another_object": another,
            "another_position": fmt_pos_3d(ax, ay, az),
            "correct_answer": rel,
        })
    return rows

def gen_3d_multi(n):
    rows = []
    attempts = 0
    while len(rows) < n and attempts < 10000:
        attempts += 1
        obj, another = pick_two_objects()
        sx, sy, sz = random.randint(-6, 6), random.randint(-6, 6), random.randint(-6, 6)
        ax, ay, az = random.randint(-6, 6), random.randint(-6, 6), random.randint(-6, 6)
        steps = [(random.randint(2, 6), random.choice(DIRECTIONS_3D)) for _ in range(random.randint(2, 4))]
        trans_str, tdx, tdy, tdz = build_transformations_3d(steps)
        rel = relative_direction_3d(sx + tdx, sy + tdy, sz + tdz, ax, ay, az)
        if rel is None:
            continue
        rows.append({
            "object": obj,
            "position": fmt_pos_3d(sx, sy, sz),
            "transformations": trans_str,
            "another_object": another,
            "another_position": fmt_pos_3d(ax, ay, az),
            "correct_answer": rel,
        })
    return rows

# Column definitions for the CSV output

SINGLE_COLS = ["object", "position", "distance", "direction", "another_object", "another_position", "correct_answer"]
MULTI_COLS  = ["object", "position", "transformations", "another_object", "another_position", "correct_answer"]

# Helper functions

def write_csv(path, cols, rows, append=False):
    mode = "a" if append else "w"
    write_header = not append or not os.path.exists(path) or os.path.getsize(path) == 0
    with open(path, mode, newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        if write_header:
            w.writeheader()
        for row in rows:
            w.writerow(row)

def _detect(folder_name, keyword_map, default):
    name = folder_name.lower()
    for keyword, value in keyword_map.items():
        if keyword in name:
            return value
    return default

def resolve_folder(task_folder):
    """Return the absolute path to the task folder.
    If the path is not absolute, first look for it inside the tasks/ folder next to this script.
    Falls back to treating it as a path relative to the current working directory.
    """
    if os.path.isabs(task_folder):
        return task_folder
    candidate = os.path.join(DEFAULT_BASE, task_folder)
    if os.path.isdir(candidate):
        return candidate
    # also try the raw path as-is (relative to cwd)
    if os.path.isdir(task_folder):
        return os.path.abspath(task_folder)
    return candidate  # let the caller report the error if this path does not exist

# Command line entry point

def main():
    parser = argparse.ArgumentParser(
        description="Generate translation benchmark rows into a task folder's values.csv.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("task_folder", help="Task folder name or path")
    parser.add_argument("n", type=int, help="Number of rows to generate")
    parser.add_argument("--dim",    choices=["2", "3"], default=None, help="2D or 3D (auto-detected if omitted)")
    parser.add_argument("--mode",   choices=["single", "multi"], default=None, help="single or multi (auto-detected if omitted)")
    parser.add_argument("--seed",   type=int, default=42, help="Random seed (default: 42)")
    parser.add_argument("--append", action="store_true", help="Append to existing values.csv instead of overwriting")
    args = parser.parse_args()

    random.seed(args.seed)

    folder = resolve_folder(args.task_folder)
    if not os.path.isdir(folder):
        print(f"Error: folder not found: {folder}", file=sys.stderr)
        sys.exit(1)

    folder_name = os.path.basename(folder)

    dim  = int(args.dim)  if args.dim  else _detect(folder_name, {"2d": 2, "3d": 3}, 3)
    mode = args.mode      if args.mode else _detect(folder_name, {"single": "single", "multi": "multi"}, "single")

    print(f"Generating {args.n} rows  |  dim={dim}  mode={mode}  seed={args.seed}  append={args.append}")
    print(f"Target: {folder}")

    if dim == 2:
        rows = gen_2d_single(args.n) if mode == "single" else gen_2d_multi(args.n)
        cols = SINGLE_COLS if mode == "single" else MULTI_COLS
    else:
        rows = gen_3d_single(args.n) if mode == "single" else gen_3d_multi(args.n)
        cols = SINGLE_COLS if mode == "single" else MULTI_COLS

    out_path = os.path.join(folder, "values.csv")
    write_csv(out_path, cols, rows, append=args.append)

    print(f"Wrote {len(rows)} rows to {out_path}")
    for r in rows:
        print(" ", r)


if __name__ == "__main__":
    main()

