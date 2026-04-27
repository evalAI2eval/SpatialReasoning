import ollama
from .benchmark_types import Task

# Names that must match the elif chain in benchmark_scoring.score_prediction
VALID_SCORING_FUNCTIONS: set[str] = {
    'binary_match',
    'debug_binary_match',
}

# Enforced task tags for categorization and analysis. Each task must have at least one of these tags.
VALID_TASK_CATEGORIES: list[str] = ['2d_rotation_multi', 
                                    '2d_rotation_single', 
                                    '2d_translation_single', 
                                    '2d_translation_multi',
                                    '2d_combined_transformations_multi', 
                                    '3d_rotation_single', 
                                    '3d_rotation_multi',
                                    '3d_translation_single',
                                    '3d_translation_multi', 
                                    '3d_rotations_multi_die', 
                                    '3d_rotations_single_common_sense',
                                    '3d_translations_single_common_sense',
                                    '3d_combined_transformations_multi',
                                    '3d_combined_transformations_common_sense',
                                    ]


def validate_models_queryable(models: list[str]) -> list[str]:
    """Check that every model in `models` is available in the local Ollama instance.
    Returns a list of error strings (empty = all models available).
    """
    errors = []
    try:
        available = {m.model for m in ollama.list().models}
    except Exception as e:
        return [f"Could not connect to Ollama to check model availability: {e}"]

    for model in models:
        if model not in available:
            errors.append(f"Model '{model}' is not available in Ollama (available: {sorted(available)})")
    return errors


def validate_tasks_exist(tasks: list[Task]) -> list[str]:
    """Check that the task list is not empty.
    Returns a list of error strings (empty = tasks exist).
    """
    if not tasks:
        return ["No tasks found — task list is empty"]
    return []


def validate_task_scoring_functions(tasks: list[Task]) -> list[str]:
    """Check that every task has at least one scoring function and all named
    functions are registered in VALID_SCORING_FUNCTIONS.
    Returns a list of error strings (empty = all tasks valid).
    """
    errors = []
    for task in tasks:
        if not task.scoring_functions:
            errors.append(f"Task '{task.task_name}': no scoring functions defined")
            continue
        for fn in task.scoring_functions:
            if fn not in VALID_SCORING_FUNCTIONS:
                errors.append(f"Task '{task.task_name}': unknown scoring function '{fn}'")
    return errors


def validate_task_tags(tasks: list[Task]) -> list[str]:
    """Check that every task has at least one tag belonging to VALID_TASK_CATEGORIES.
    Skips the check when VALID_TASK_CATEGORIES is empty (not yet configured).
    Returns a list of error strings (empty = all tasks valid).
    """
    if not VALID_TASK_CATEGORIES:
        return []

    errors = []
    valid_set = set(VALID_TASK_CATEGORIES)
    for task in tasks:
        if not any(tag in valid_set for tag in task.tags):
            errors.append(
                f"Task '{task.task_name}': none of its tags {task.tags} are in VALID_TASK_CATEGORIES"
            )
    return errors


def validate_benchmark(config, tasks: list[Task]) -> bool:
    """Run all validation checks against `config` and `tasks`.
    Prints each error found. Returns True if every check passes, False otherwise.
    """
    all_errors: list[str] = []

    all_errors += validate_models_queryable(config.models)
    all_errors += validate_tasks_exist(tasks)
    all_errors += validate_task_scoring_functions(tasks)
    all_errors += validate_task_tags(tasks)

    for error in all_errors:
        print(f"[VALIDATION ERROR] {error}")

    if not all_errors:
        print("[VALIDATION] All checks passed.")
        return True

    return False
