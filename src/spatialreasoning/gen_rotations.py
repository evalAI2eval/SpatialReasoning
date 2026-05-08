"""
gen_rotations.py - generate rotation benchmark rows into a task folder's values.csv.

Usage:
    python gen_rotations.py <task_folder> <n> [--dim 2|3] [--mode single|multi] [--seed N] [--append]

Arguments:
    task_folder   Path to the task folder (absolute, or relative to this script's tasks/ sibling).
                  e.g.  WIP_2d_rotations_single
                        PLACEHOLDER_3d_rotations_multi
    n             Number of rows to generate.

Options:
    --dim         2 or 3  (default: auto-detected from folder name; falls back to 2)
    --mode        single or multi  (default: auto-detected from folder name; falls back to single)
    --seed        Random seed (default: 42)
    --append      Append to existing values.csv instead of overwriting

Examples:
    python gen_rotations.py WIP_2d_rotations_single 20
    python gen_rotations.py PLACEHOLDER_3d_rotations_multi 15 --append
    python gen_rotations.py WIP_2d_rotations_multi 10 --dim 2 --mode multi --seed 7
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

# 2D rotation section
# Directions are ordered clockwise in 45-degree steps starting from north.
# A clockwise rotation increases the index in the list.

DIRS_2D = ["north", "northeast", "east", "southeast", "south", "southwest", "west", "northwest"]
DIR_TO_IDX_2D = {d: i for i, d in enumerate(DIRS_2D)}

def rotate_2d(direction, amount_deg, axis):
    """
    Rotate a 2D facing direction.
    axis: 'clockwise' or 'counterclockwise'
    amount_deg: a multiple of 45
    Returns the new direction as a string.
    """
    steps = (amount_deg // 45) % 8
    idx = DIR_TO_IDX_2D[direction]
    if axis == "clockwise":
        new_idx = (idx + steps) % 8
    else:
        new_idx = (idx - steps) % 8
    return DIRS_2D[new_idx]

def gen_2d_single(n):
    amounts = [45, 90, 135, 180, 225, 270, 315]
    axes = ["clockwise", "counterclockwise"]
    rows = []
    attempts = 0
    while len(rows) < n and attempts < 10000:
        attempts += 1
        obj = random.choice(OBJECTS)
        direction = random.choice(DIRS_2D)
        amount = random.choice(amounts)
        axis = random.choice(axes)
        result = rotate_2d(direction, amount, axis)
        if result == direction:
            continue  # the net rotation works out to a full circle, so skip this one
        rows.append({
            "object": obj,
            "direction": direction,
            "rotationamount": amount,
            "rotationaxis": axis,
            "correct_answer": result,
        })
    return rows

def gen_2d_multi(n):
    axes = ["clockwise", "counterclockwise"]
    amounts = [45, 90, 135, 180, 225, 270]
    rows = []
    attempts = 0
    while len(rows) < n and attempts < 10000:
        attempts += 1
        obj = random.choice(OBJECTS)
        direction = random.choice(DIRS_2D)
        n_steps = random.randint(2, 4)
        steps = [(random.choice(amounts), random.choice(axes)) for _ in range(n_steps)]

        # Build the transformation string and track where we end up
        current = direction
        parts = []
        for amt, ax in steps:
            current = rotate_2d(current, amt, ax)
            parts.append(f"{amt} degrees {ax}")
        transformation = "rotated " + " then ".join(parts)

        if current == direction:
            continue  # net rotation is trivial
        rows.append({
            "object": obj,
            "direction": direction,
            "transformation": transformation,
            "correct_answer": current,
        })
    return rows

# 3D rotation section
# Facing direction is represented as an (x, y, z) unit vector.
# Axis conventions: X is left/right, Y is up/down, Z is forward/backward (positive Z faces toward the viewer).
# Clockwise means clockwise when viewed from the positive end of that axis.

FACING_3D = {
    "north":  (0, 0,  1),
    "south":  (0, 0, -1),
    "east":   (1, 0,  0),
    "west":   (-1, 0, 0),
    "up":     (0, 1,  0),
    "down":   (0, -1, 0),
}
VEC_TO_FACING_3D = {v: k for k, v in FACING_3D.items()}

def _rot90_cw(vec, axis):
    """Apply a single 90-degree clockwise rotation around the given axis."""
    x, y, z = vec
    if axis == "Y":
        # Clockwise from above: north to east to south to west. Vector goes from (x,y,z) to (z,y,-x).
        return (z, y, -x)
    elif axis == "X":
        # Clockwise from the right: north to up to south to down. Vector goes from (x,y,z) to (x,z,-y).
        return (x, z, -y)
    elif axis == "Z":
        # Clockwise from the front: up to east to down to west. Vector goes from (x,y,z) to (y,-x,z).
        return (y, -x, z)
    raise ValueError(f"Unknown axis: {axis}")

def rotate_3d(direction, amount_deg, rot_direction, axis):
    """
    Rotate a 3D facing direction.
    rot_direction: 'clockwise' or 'counterclockwise'
    amount_deg: a multiple of 90
    axis: 'X', 'Y', or 'Z'
    Returns the new direction as a string, or None if the result is not a named cardinal direction.
    """
    steps = (amount_deg // 90) % 4
    if rot_direction == "counterclockwise":
        steps = (4 - steps) % 4

    vec = FACING_3D[direction]
    for _ in range(steps):
        vec = _rot90_cw(vec, axis)

    return VEC_TO_FACING_3D.get(vec)  # returns None if the result is not a named cardinal direction

def gen_3d_single(n):
    amounts = [90, 180, 270]
    rot_dirs = ["clockwise", "counterclockwise"]
    axes = ["X", "Y", "Z"]
    rows = []
    attempts = 0
    while len(rows) < n and attempts < 10000:
        attempts += 1
        obj = random.choice(OBJECTS)
        direction = random.choice(list(FACING_3D.keys()))
        amount = random.choice(amounts)
        rot_dir = random.choice(rot_dirs)
        axis = random.choice(axes)

        result = rotate_3d(direction, amount, rot_dir, axis)
        if result is None or result == direction:
            continue  # skip if the rotation lands on a non-cardinal direction or has no net effect

        rows.append({
            "object": obj,
            "direction": direction,
            "rotationamount": amount,
            "rotationdirection": rot_dir,
            "rotationaxis": axis,
            "correct_answer": result,
        })
    return rows

def gen_3d_multi(n):
    amounts = [90, 180, 270]
    rot_dirs = ["clockwise", "counterclockwise"]
    axes = ["X", "Y", "Z"]
    rows = []
    attempts = 0
    while len(rows) < n and attempts < 10000:
        attempts += 1
        obj = random.choice(OBJECTS)
        direction = random.choice(list(FACING_3D.keys()))
        n_steps = random.randint(2, 4)
        steps = [(random.choice(amounts), random.choice(rot_dirs), random.choice(axes)) for _ in range(n_steps)]

        current = direction
        parts = []
        valid = True
        for amt, rd, ax in steps:
            result = rotate_3d(current, amt, rd, ax)
            if result is None:
                valid = False
                break
            parts.append(f"{amt} degrees {rd} around the {ax} axis")
            current = result

        if not valid or current == direction:
            continue  # skip if any step hit a non-cardinal direction or the net rotation cancelled out

        rows.append({
            "object": obj,
            "direction": direction,
            "transformations": " then ".join(parts),
            "correct_answer": current,
        })
    return rows

# Column definitions for the CSV output

COLS = {
    ("2", "single"): ["object", "direction", "rotationamount", "rotationaxis", "correct_answer"],
    ("2", "multi"):  ["object", "direction", "transformation", "correct_answer"],
    ("3", "single"): ["object", "direction", "rotationamount", "rotationdirection", "rotationaxis", "correct_answer"],
    ("3", "multi"):  ["object", "direction", "transformations", "correct_answer"],
}

GENERATORS = {
    ("2", "single"): gen_2d_single,
    ("2", "multi"):  gen_2d_multi,
    ("3", "single"): gen_3d_single,
    ("3", "multi"):  gen_3d_multi,
}

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
        description="Generate rotation benchmark rows into a task folder's values.csv.",
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
    dim  = args.dim  or _detect(folder_name, {"2d": "2", "3d": "3"}, "2")
    mode = args.mode or _detect(folder_name, {"single": "single", "multi": "multi"}, "single")

    key = (dim, mode)
    gen_fn = GENERATORS.get(key)
    cols   = COLS.get(key)
    if gen_fn is None:
        print(f"Error: no generator for dim={dim} mode={mode}", file=sys.stderr)
        sys.exit(1)

    print(f"Generating {args.n} rows  |  dim={dim}  mode={mode}  seed={args.seed}  append={args.append}")
    print(f"Target: {folder}")

    rows = gen_fn(args.n)
    out_path = os.path.join(folder, "values.csv")
    write_csv(out_path, cols, rows, append=args.append)

    print(f"Wrote {len(rows)} rows to {out_path}")
    for r in rows:
        print(" ", r)


if __name__ == "__main__":
    main()
