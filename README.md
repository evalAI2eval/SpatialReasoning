# Spatial Reasoning Benchmark

A benchmark suite for evaluating the spatial reasoning abilities of large language models.
Tasks cover 2D and 3D rotations, translations, and combined transformations, each phrased
as a multiple-choice question drawn from a fixed answer bank.

---

## Running the Benchmark

### Prerequisites
1. Ensure Ollama is installed and running
2. Ensure any models you want to benchmark are downloaded (ollama pull [model_name])

### Installation and Running
Recommended to create .venv
Install module with pip install . -e
Example benchmark in experiment/experiment.ipynb

### BenchTools
TODO: FILL OUT

## Task types

| Folder | Description |
|--------|-------------|
| `final_2d_rotations_single` | One rotation step, 2D compass directions |
| `final_2d_rotations_multi` | Multiple rotation steps, 2D |
| `final_3d_rotations_single` | One rotation step, 3D with axis |
| `final_3d_rotations_multi` | Multiple rotation steps, 3D |
| `final_2d_translations_single` | One move step, 2D grid |
| `final_2d_translations_multi` | Multiple move steps, 2D |
| `final_3d_translations_single` | One move step, 3D grid |
| `final_3d_translations_multi` | Multiple move steps, 3D |
| `final_2d_combined_transformations_multi` | Mixed rotations and moves, 2D |
| `final_3d_combined_transformations_multi` | Mixed rotations and moves, 3D |

TODO: ADD/FILL OUT COMPLEX

For the integrated benchmarker, each task folder contains:

- `config.yml` - system prompt, answer bank, scoring function, and category tags
- `template.txt` - prompt template referencing CSV column names
- `values.csv` - generated question rows (object, transformations, correct answer, etc.)

Scoring uses `binary_match`: the model's response is stripped, lowercased, and compared
to the expected answer string.

---

## Populating more task data

Both populate_tasks scripts regenerate `values.csv` in every task folder using a fixed random seed so
task generations/results are reproducible. 
NOTE: "common-sense" style questions are human authored and are static / not generated

TODO: INTEGRATE RUBIX/DICE GENERATION INTO SCRIPTS

### Linux / macOS / WSL (Bash)

```bash
# from the repo root — uses default seed=42, n=20
bash populate_tasks.sh

# custom seed and count
bash populate_tasks.sh --seed 123 --n 50
```

Both scripts print a summary line for each task folder as they go, and exit non-zero on
the first failure.

---

## Task Generator scripts

Task generation takes place in the following scripts

### gen_rotations.py

Generates rotation questions. Supports 2D (compass directions) and 3D (facing vectors
with rotation axis).

```
python gen_rotations.py <task_folder> <n> [--dim 2|3] [--mode single|multi] [--seed N] [--append]
```

When `--dim` and `--mode` are omitted the script infers them from the folder name.

### gen_translations.py

Generates translation questions. An object starts at a random grid position, moves
through one or more steps, and the question asks for the dominant axis direction from
start to end.

```
python gen_translations.py <task_folder> <n> [--dim 2|3] [--mode single|multi] [--seed N] [--append]
```

### gen_combined.py

Generates combined rotation + translation questions. Each row always contains at least
one rotation step and one translation step. The question is randomly one of two forms:

- "Which direction is the object facing?" (tests orientation tracking)
- "Where is the object relative to its starting position?" (tests position tracking)

Only multi-step mode is supported.

```
python gen_combined.py <task_folder> <n> [--dim 2|3] [--seed N] [--append]
```

### Rubix

### Dice

---

## Utility Scripts

### task_to_benchtools.sh

Copies and reformats tasks into the benchtools folder/format.



