#!/usr/bin/env bash
# task_to_benchtools.sh
# Copies task folders from ./src/spatialreasoning/tasks to ./SpatialReasoning_Benchtools/tasks,
# then in the COPIES:
#   1. Renames the correct_answer column to reference in the header row of values.csv
#   2. Prepends the system_prompt from config.yml to template.txt
#   3. Removes config.yml

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$SCRIPT_DIR/src/spatialreasoning/tasks"
DEST="$SCRIPT_DIR/SpatialReasoning_Benchtools/tasks"
PYTHON="${PYTHON:-python}"

for task_dir in "$SRC"/*/; do
    [ -d "$task_dir" ] || continue
    task_name=$(basename "$task_dir")
    dest_task="$DEST/$task_name"

    echo "Copying $task_name ..."
    mkdir -p "$dest_task"
    cp -r "$task_dir/." "$dest_task/"

    config_file="$dest_task/config.yml"
    template_file="$dest_task/template.txt"
    values_file="$dest_task/values.csv"

    # 1. Replace correct_answer with reference in header row of values.csv
    if [ -f "$values_file" ]; then
        tmpcsv=$(mktemp)
        sed '1s/correct_answer/reference/g' "$values_file" > "$tmpcsv"
        mv "$tmpcsv" "$values_file"
    fi

    # 2. Extract system_prompt from config.yml and prepend to template.txt
    if [ -f "$config_file" ] && [ -f "$template_file" ]; then
        tmpprompt=$(mktemp)
        "$PYTHON" - "$config_file" > "$tmpprompt" <<'PYEOF'
import yaml, sys
with open(sys.argv[1]) as f:
    config = yaml.safe_load(f)
sys.stdout.write(config.get('system_prompt', ''))
PYEOF
        cat "$template_file" >> "$tmpprompt"
        mv "$tmpprompt" "$template_file"
    fi

    # 3. Remove config.yml
    if [ -f "$config_file" ]; then
        rm "$config_file"
    fi
done

echo "Done."
