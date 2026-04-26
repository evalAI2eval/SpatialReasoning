#!/usr/bin/env bash
# populate_tasks.sh
# Regenerates values.csv for every benchmark task folder with 20 rows at a fixed seed.
# Run this from the repo root or from anywhere - it uses the script's own location to find benchmark folder (SpatialReasoning).
# Usage: bash populate_tasks.sh
# Optional: bash populate_tasks.sh --seed 99 --n 30

set -e

SEED=42
N=20

while [[ $# -gt 0 ]]; do
    case "$1" in
        --seed) SEED="$2"; shift 2 ;;
        --n)    N="$2";    shift 2 ;;
        *) echo "Unknown argument: $1"; exit 1 ;;
    esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BENCH_DIR="$SCRIPT_DIR/src/spatialreasoning"
PYTHON="${PYTHON:-python}"

run_generator() {
    local script="$1"
    local folder="$2"
    local dim="$3"
    local mode="$4"

    echo "  Populating $folder ..."
    if [[ -n "$mode" ]]; then
        "$PYTHON" "$script" "$folder" "$N" --dim "$dim" --mode "$mode" --seed "$SEED"
    else
        "$PYTHON" "$script" "$folder" "$N" --dim "$dim" --seed "$SEED"
    fi
}

cd "$BENCH_DIR"

echo ""
echo "Populating rotation tasks (seed=$SEED, n=$N)"
echo "----------------------------------------------"
run_generator gen_rotations.py final_2d_rotations_single 2 single
run_generator gen_rotations.py final_2d_rotations_multi  2 multi
run_generator gen_rotations.py final_3d_rotations_single 3 single
run_generator gen_rotations.py final_3d_rotations_multi  3 multi

echo ""
echo "Populating translation tasks (seed=$SEED, n=$N)"
echo "------------------------------------------------"
run_generator gen_translations.py final_2d_translations_single 2 single
run_generator gen_translations.py final_2d_translations_multi  2 multi
run_generator gen_translations.py final_3d_translations_single 3 single
run_generator gen_translations.py final_3d_translations_multi  3 multi

echo ""
echo "Populating combined transformation tasks (seed=$SEED, n=$N)"
echo "-------------------------------------------------------------"
run_generator gen_combined.py final_2d_combined_transformations_multi 2 ""
run_generator gen_combined.py final_3d_combined_transformations_multi 3 ""

echo ""
echo "Done. All task folders populated."
