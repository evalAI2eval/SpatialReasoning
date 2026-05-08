"""
gen_combined.py - generate combined rotation and translation benchmark rows.

Each row interleaves rotation and translation steps. The object has both a
facing direction and an (x,y) or (x,y,z) position. Rotations only affect
facing; translations only affect position.

Each row ends with one of two randomly chosen questions:
  - "Which direction is the object facing?"
  - "Where is the object relative to its starting position?"

Valid 2D answers: north, east, south, west
Valid 3D answers: north, south, east, west, up, down

Usage:
    python gen_combined.py <task_folder> <n> [--dim 2|3] [--seed N] [--append]

Arguments:
    task_folder   Path to the task folder (absolute, or relative to this
                  script's tasks/ sibling).
                  e.g.  WIP_2d_combined_transformations_multi
                        WIP_3d_combined_transformations_multi
    n             Number of rows to generate.

Options:
    --dim         2 or 3  (default: auto-detected from folder name; falls back to 3)
    --seed        Random seed (default: 42)
    --append      Append to existing values.csv instead of overwriting

Examples:
    python gen_combined.py WIP_3d_combined_transformations_multi 20
    python gen_combined.py WIP_2d_combined_transformations_multi 20 --dim 2
    python gen_combined.py WIP_3d_combined_transformations_multi 10 --append
"""

import argparse
import csv
import os
import random
import sys

DEFAULT_BASE = os.path.join(os.path.dirname(__file__), "tasks")

OBJECTS = [
    "arrow", "airplane", "car", "boat", "person", "compass",
    "ship", "rocket", "tank", "bicycle", "drone", "helicopter",
    "submarine", "train", "cannon", "cursor", "pointer",
]

COLS = ["object", "direction", "position", "transformations", "question", "correct_answer"]

QUESTION_FACING   = "Which direction is the object facing?"
QUESTION_POSITION = "Where is the object relative to its starting position?"

# 2D section

# All 8 compass directions used during rotation steps.
DIRS_2D = ["north", "northeast", "east", "southeast", "south", "southwest", "west", "northwest"]
DIR_TO_IDX_2D = {d: i for i, d in enumerate(DIRS_2D)}
# Only the four cardinal directions are valid answers in the answer bank.
CARDINALS_2D = {"north", "east", "south", "west"}

TRANS_DIRS_2D = ["up", "down", "left", "right"]
VECTORS_2D = {
    "up":    (0,  1),
    "down":  (0, -1),
    "left":  (-1, 0),
    "right": (1,  0),
}
ROT_AMOUNTS_2D = [45, 90, 135, 180, 225, 270]
ROT_AXES_2D = ["clockwise", "counterclockwise"]


def rotate_2d(direction, amount_deg, axis):
    """Rotate a 2D compass direction by the given number of degrees, clockwise or counterclockwise."""
    steps = (amount_deg // 45) % 8
    idx = DIR_TO_IDX_2D[direction]
    if axis == "clockwise":
        new_idx = (idx + steps) % 8
    else:
        new_idx = (idx - steps) % 8
    return DIRS_2D[new_idx]


def relative_cardinal_2d(dx, dy):
    """Return the dominant-axis cardinal direction (north, south, east, or west) for a displacement.
    Returns None if the displacement is zero or if the two largest axes are tied."""
    if dx == 0 and dy == 0:
        return None
    adx, ady = abs(dx), abs(dy)
    if adx == ady:
        return None
    if ady > adx:
        return "north" if dy > 0 else "south"
    return "east" if dx > 0 else "west"


def fmt_pos_2d(x, y):
    return f"({x},{y})"


def gen_2d_multi(n):
    """Generate n rows of combined 2D rotation and translation steps."""
    rows = []
    attempts = 0
    while len(rows) < n and attempts < 50000:
        attempts += 1
        obj = random.choice(OBJECTS)
        # Start from a cardinal direction so facing answers are always in the answer bank.
        direction = random.choice(list(CARDINALS_2D))
        sx, sy = random.randint(-8, 8), random.randint(-8, 8)

        n_steps = random.randint(2, 4)
        # Guarantee at least one rotation and one translation.
        step_types = ["rotation", "translation"] + [
            random.choice(["rotation", "translation"]) for _ in range(n_steps - 2)
        ]
        random.shuffle(step_types)

        current_dir = direction
        cx, cy = sx, sy
        parts = []
        for stype in step_types:
            if stype == "rotation":
                amt = random.choice(ROT_AMOUNTS_2D)
                ax = random.choice(ROT_AXES_2D)
                current_dir = rotate_2d(current_dir, amt, ax)
                parts.append(f"rotate {amt} degrees {ax}")
            else:
                dist = random.randint(2, 6)
                d = random.choice(TRANS_DIRS_2D)
                vx, vy = VECTORS_2D[d]
                cx += dist * vx
                cy += dist * vy
                parts.append(f"move {dist} units {d}")

        transformations = " then ".join(parts)
        question_type = random.choice(["facing", "position"])

        if question_type == "facing":
            if current_dir not in CARDINALS_2D:
                continue  # diagonal result, not in the answer bank
            question = QUESTION_FACING
            correct_answer = current_dir
        else:
            rel = relative_cardinal_2d(cx - sx, cy - sy)
            if rel is None:
                continue  # tied axes or no net movement
            question = QUESTION_POSITION
            correct_answer = rel

        rows.append({
            "object": obj,
            "direction": direction,
            "position": fmt_pos_2d(sx, sy),
            "transformations": transformations,
            "question": question,
            "correct_answer": correct_answer,
        })
    return rows


# 3D section

FACING_3D = {
    "north":  (0,  0,  1),
    "south":  (0,  0, -1),
    "east":   (1,  0,  0),
    "west":   (-1, 0,  0),
    "up":     (0,  1,  0),
    "down":   (0, -1,  0),
}
VEC_TO_FACING_3D = {v: k for k, v in FACING_3D.items()}

TRANS_DIRS_3D = ["up", "down", "left", "right", "forward", "backward"]
VECTORS_3D = {
    "up":       (0,  1,  0),
    "down":     (0, -1,  0),
    "left":     (-1, 0,  0),
    "right":    (1,  0,  0),
    "forward":  (0,  0,  1),
    "backward": (0,  0, -1),
}
ROT_AMOUNTS_3D = [90, 180, 270]
ROT_DIRS_3D = ["clockwise", "counterclockwise"]
ROT_AXES_3D = ["X", "Y", "Z"]


def _rot90_cw(vec, axis):
    """Apply a single 90-degree clockwise rotation around the given axis."""
    x, y, z = vec
    if axis == "Y":
        return (z, y, -x)
    elif axis == "X":
        return (x, z, -y)
    elif axis == "Z":
        return (y, -x, z)
    raise ValueError(f"Unknown axis: {axis}")


def rotate_3d(direction, amount_deg, rot_direction, axis):
    """Rotate a 3D facing direction by the given amount around the given axis.
    Returns the new direction name, or None if the result does not land on a named cardinal direction."""
    steps = (amount_deg // 90) % 4
    if rot_direction == "counterclockwise":
        steps = (4 - steps) % 4
    vec = FACING_3D[direction]
    for _ in range(steps):
        vec = _rot90_cw(vec, axis)
    return VEC_TO_FACING_3D.get(vec)


def relative_cardinal_3d(dx, dy, dz):
    """Return the dominant-axis direction (north, south, east, west, up, or down) for a 3D displacement.
    Returns None if the displacement is zero or if the two largest axes are tied."""
    if dx == 0 and dy == 0 and dz == 0:
        return None
    axes = sorted([("x", abs(dx)), ("y", abs(dy)), ("z", abs(dz))], key=lambda t: t[1], reverse=True)
    if axes[0][1] == axes[1][1]:
        return None  # the two largest axes are tied, so there is no clear dominant direction
    dominant = axes[0][0]
    if dominant == "y":
        return "up" if dy > 0 else "down"
    if dominant == "x":
        return "east" if dx > 0 else "west"
    return "north" if dz > 0 else "south"


def fmt_pos_3d(x, y, z):
    return f"({x},{y},{z})"


def gen_3d_multi(n):
    """Generate n rows of combined 3D rotation and translation steps."""
    rows = []
    attempts = 0
    while len(rows) < n and attempts < 50000:
        attempts += 1
        obj = random.choice(OBJECTS)
        direction = random.choice(list(FACING_3D.keys()))
        sx, sy, sz = random.randint(-8, 8), random.randint(-8, 8), random.randint(-8, 8)

        n_steps = random.randint(2, 4)
        # Guarantee at least one rotation and one translation.
        step_types = ["rotation", "translation"] + [
            random.choice(["rotation", "translation"]) for _ in range(n_steps - 2)
        ]
        random.shuffle(step_types)

        current_dir = direction
        cx, cy, cz = sx, sy, sz
        parts = []
        valid = True
        for stype in step_types:
            if stype == "rotation":
                amt = random.choice(ROT_AMOUNTS_3D)
                rd = random.choice(ROT_DIRS_3D)
                ax = random.choice(ROT_AXES_3D)
                result = rotate_3d(current_dir, amt, rd, ax)
                if result is None:
                    valid = False
                    break
                current_dir = result
                parts.append(f"rotate {amt} degrees {rd} around the {ax} axis")
            else:
                dist = random.randint(2, 6)
                d = random.choice(TRANS_DIRS_3D)
                vx, vy, vz = VECTORS_3D[d]
                cx += dist * vx
                cy += dist * vy
                cz += dist * vz
                parts.append(f"move {dist} units {d}")

        if not valid:
            continue

        transformations = " then ".join(parts)
        question_type = random.choice(["facing", "position"])

        if question_type == "facing":
            question = QUESTION_FACING
            correct_answer = current_dir
        else:
            rel = relative_cardinal_3d(cx - sx, cy - sy, cz - sz)
            if rel is None:
                continue  # tied axes or no net movement
            question = QUESTION_POSITION
            correct_answer = rel

        rows.append({
            "object": obj,
            "direction": direction,
            "position": fmt_pos_3d(sx, sy, sz),
            "transformations": transformations,
            "question": question,
            "correct_answer": correct_answer,
        })
    return rows


# Helper functions

def write_csv(path, rows, append=False):
    mode = "a" if append else "w"
    write_header = not append or not os.path.exists(path) or os.path.getsize(path) == 0
    with open(path, mode, newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
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
    if os.path.isabs(task_folder):
        return task_folder
    candidate = os.path.join(DEFAULT_BASE, task_folder)
    if os.path.isdir(candidate):
        return candidate
    if os.path.isdir(task_folder):
        return os.path.abspath(task_folder)
    return candidate


# Command line entry point

def main():
    parser = argparse.ArgumentParser(
        description="Generate combined rotation+translation benchmark rows.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("task_folder", help="Task folder name or path")
    parser.add_argument("n", type=int, help="Number of rows to generate")
    parser.add_argument("--dim",    choices=["2", "3"], default=None, help="2D or 3D (auto-detected if omitted)")
    parser.add_argument("--seed",   type=int, default=42, help="Random seed (default: 42)")
    parser.add_argument("--append", action="store_true", help="Append to existing values.csv instead of overwriting")
    args = parser.parse_args()

    random.seed(args.seed)

    folder = resolve_folder(args.task_folder)
    if not os.path.isdir(folder):
        print(f"Error: folder not found: {folder}", file=sys.stderr)
        sys.exit(1)

    folder_name = os.path.basename(folder)
    dim = args.dim or _detect(folder_name, {"2d": "2", "3d": "3"}, "3")

    print(f"Generating {args.n} rows  |  dim={dim}  seed={args.seed}  append={args.append}")
    print(f"Target: {folder}")

    if dim == "2":
        rows = gen_2d_multi(args.n)
    else:
        rows = gen_3d_multi(args.n)

    out_path = os.path.join(folder, "values.csv")
    write_csv(out_path, rows, append=args.append)

    print(f"Wrote {len(rows)} rows to {out_path}")
    for r in rows:
        print(" ", r)


if __name__ == "__main__":
    main()
