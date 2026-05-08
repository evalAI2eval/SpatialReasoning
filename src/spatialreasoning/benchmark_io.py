import yaml
import os
import csv
import dataclasses
from datetime import datetime
from .benchmark_types import Task





# Loads task config from a config.yml file in the given folder.
# Expected keys: system_prompt, scoring_functions, tags
def load_task_config(folder_path):
    config_path = os.path.join(folder_path, "config.yml")
    if not os.path.exists(config_path):
        return {}
    with open(config_path, 'r') as f:
        return yaml.safe_load(f) or {}


# This function scans a directory for task folders. Each folder should contain:
#   - template.txt: prompt template with {placeholder} variables
#   - values.csv: CSV with columns matching placeholders; must include "correct_answer"
#   - config.yml (optional): task-level config with keys:
#       system_prompt: string
#       scoring_functions: list of function names
#       tags: list of tags
# Returns a list of task dicts, each with: prompt, correct_answer, system_prompt, scoring_functions, tags, task_name
def generate_prompts_from_directory(directory_path):
    tasks = []

    for folder_name in sorted(os.listdir(directory_path)):
        folder_path = os.path.join(directory_path, folder_name)
        if not os.path.isdir(folder_path):
            continue

        template_path = os.path.join(folder_path, "template.txt")
        values_path = os.path.join(folder_path, "values.csv")

        if not (os.path.exists(template_path) and os.path.exists(values_path)):
            continue

        config = load_task_config(folder_path)
        system_prompt = config.get("system_prompt", "")
        scoring_functions = config.get("scoring_functions", [])
        tags = config.get("tags", [])

        with open(template_path, 'r') as f:
            template = f.read()

        with open(values_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                prompt = template
                for key, value in row.items():
                    prompt = prompt.replace(f'{{{key}}}', value)
                tasks.append(Task(
                    task_name=folder_name,
                    prompt=prompt,
                    correct_answer=row.get("correct_answer", ""),
                    system_prompt=system_prompt,
                    scoring_functions=scoring_functions,
                    tags=tags,
                ))

    return tasks


def filter_tasks_by_tags(tasks: list, tags: list) -> list:
    """Return tasks whose tag list overlaps with `tags`. Empty/None filter returns all tasks."""
    if not tags:
        return tasks
    return [t for t in tasks if any(tag in t.tags for tag in tags)]


def save_results(model_results_list: list, output_dir: str, model_aliases: dict[str, str] = None) -> None:
    """Serialize each ModelResults to a timestamped YAML file under {output_dir}/{model}/."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    for model_results in model_results_list:
        # use alias if provided
        model_name = model_aliases.get(model_results.model, model_results.model) if model_aliases else model_results.model
        # remove invalid path characters from model name for directory naming
        safe_model_name = "".join(c for c in model_name if c.isalnum() or c in (" ", ".", "_")).rstrip()
        safe_model_name = safe_model_name.replace(":", "_")
        model_dir = os.path.join(output_dir, safe_model_name)
        os.makedirs(model_dir, exist_ok=True)
        filepath = os.path.join(model_dir, f"{timestamp}.yml")
        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(dataclasses.asdict(model_results), f, allow_unicode=True, default_flow_style=False)
        print(f"Saved results to {filepath}")


def load_results(output_dir: str) -> list:
    """Walk output_dir and return all saved result dicts (raw YAML loads)."""
    results = []
    for root, _, files in os.walk(output_dir):
        for filename in sorted(files):
            if filename.endswith('.yml'):
                filepath = os.path.join(root, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    if data:
                        results.append(data)
    return results


def view_saved_results(output_dir: str) -> None:
    """Print a summary of all saved benchmark results in output_dir."""
    results = load_results(output_dir)
    if not results:
        print(f"No saved results found in {output_dir}")
        return
    for result in results:
        avg = result.get('average_score', 0.0)
        total_scores = result.get('total_scores', [])
        total_correct = sum(s['calculated_score'] for repeat in total_scores for s in repeat)
        total_possible = sum(len(repeat) for repeat in total_scores)
        print(f"Model: {result['model']}")
        print(f"  Score:  {int(total_correct)} / {total_possible}  ({avg:.1%})")
        for tag, scores in (result.get('scores_by_tag') or {}).items():
            tag_correct = sum(s['calculated_score'] for s in scores)
            print(f"  Tag [{tag}]: {int(tag_correct)} / {len(scores)}")
        print()


# Example/Debugging usage
if __name__ == "__main__":
    directory_path = "./benchmark_redux/tasks"
    tasks = generate_prompts_from_directory(directory_path)
    for task in tasks:
        print(f"Task:              {task.task_name}")
        print(f"Tags:              {task.tags}")
        print(f"Scoring Functions: {task.scoring_functions}")
        print(f"System Prompt:     {task.system_prompt}")
        print(f"Prompt:            {task.prompt}")
        print(f"Correct Answer:    {task.correct_answer}\n")

