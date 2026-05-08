from pathlib import Path
from .benchmark_runner import BenchmarkRunner
from .benchmark_io import generate_prompts_from_directory, filter_tasks_by_tags, save_results, view_saved_results
from .benchmark_scoring import score_prediction
from .benchmark_types import BenchmarkResult, Score
from .benchmark_validation import validate_benchmark

from dataclasses import dataclass, field

_DEFAULT_TASK_DIR = str(Path(__file__).parent / "tasks")


@dataclass
class BenchmarkConfig:
    """Configuration for running benchmarks, including which models to test, how many repeats, where to find tasks, and where to save results."""
    models: list[str]
    model_aliases: dict[str, str]   # optional mapping of model names to display aliases
    repeats: int
    task_directory: str = field(default_factory=lambda: _DEFAULT_TASK_DIR)
    output_directory: str = "./benchmark_redux/results"
    filter_tags: list[str] = field(default_factory=list)
    think: bool = False  # whether to use "think" mode for model queries (if supported by the API)


@dataclass
class ModelResults:
    """Results for a single model across all repeats, including calculated scores and averages."""
    model: str
    repeat: int
    results: list[BenchmarkResult]
    total_scores: list[list[Score]]
    average_score: float
    scores_by_tag: dict = field(default_factory=dict)


def run_benchmarks(config: BenchmarkConfig, tasks: list) -> list[ModelResults]:
    """Run each model for the configured number of repeats and return ModelResults."""
    all_results = []
    for model in config.models:
        model_name = config.model_aliases.get(model, model) if config.model_aliases else model
        cur_model_results = ModelResults(model=model_name, repeat=config.repeats, results=[], total_scores=[], average_score=0.0)
        for repeat in range(config.repeats):
            print(f"Running benchmark for model: {model_name}, Repeat: {repeat + 1}/{config.repeats}")
            runner = BenchmarkRunner(model=model, tasks=tasks)
            result = runner.run_benchmark(repeat_index=repeat, think=config.think)
            cur_model_results.results.append(result)
        all_results.append(cur_model_results)
    return all_results


def score_results(model_results_list: list[ModelResults]) -> None:
    """Score all task results in place, populating total_scores, scores_by_tag, and average_score."""
    for model_result in model_results_list:
        scores_by_tag: dict[str, list[Score]] = {}

        per_repeat_scores = []
        for benchmark_result in model_result.results:
            repeat_scores = []
            for task_result in benchmark_result.task_results:
                scoring_fns = task_result.task.scoring_functions or ['binary_match']
                scores = score_prediction(task_result.response, task_result.task.correct_answer, scoring_function_name=scoring_fns)
                repeat_scores.extend(scores)
                for tag in task_result.task.tags:
                    scores_by_tag.setdefault(tag, []).extend(scores)
            model_result.total_scores.append(repeat_scores)
            per_repeat_scores.append(repeat_scores)
        
            # Calculate average score for this repeat and print it
            total_correct = sum(s.calculated_score for s in repeat_scores)
            total_possible = len(repeat_scores)
            average_score = total_correct / total_possible if total_possible > 0 else 0.0
            print(f"Model: {model_result.model}, Repeat: {benchmark_result.repeat_index + 1}, Score: {int(total_correct)} / {total_possible} ({average_score:.1%})")
            


        total_correct = sum(s.calculated_score for repeat in model_result.total_scores for s in repeat)
        total_possible = sum(len(repeat) for repeat in model_result.total_scores)
        model_result.average_score = total_correct / total_possible if total_possible > 0 else 0.0
        model_result.scores_by_tag = scores_by_tag


def display_results(model_results_list: list[ModelResults]) -> None:
    """Print overall score and per-tag breakdown for each model."""
    for model_result in model_results_list:
        total_correct = sum(s.calculated_score for repeat in model_result.total_scores for s in repeat)
        total_possible = sum(len(repeat) for repeat in model_result.total_scores)
        print(f"Model: {model_result.model}")
        print(f"  Overall Score: {int(total_correct)} / {total_possible}  ({model_result.average_score:.1%})")
        for tag, scores in model_result.scores_by_tag.items():
            tag_correct = sum(s.calculated_score for s in scores)
            print(f"  Tag [{tag}]: {int(tag_correct)} / {len(scores)}")
        print()


def run_full_benchmark(config: BenchmarkConfig) -> None:
    """Convenience function to run the full benchmark workflow from loading tasks to saving results."""
    tasks = generate_prompts_from_directory(config.task_directory)
    tasks = filter_tasks_by_tags(tasks, config.filter_tags)
    if not validate_benchmark(config, tasks):
        raise ValueError("Benchmark validation failed. Please fix the errors above before running the benchmark.")
    all_results = run_benchmarks(config, tasks)
    score_results(all_results)
    save_results(all_results, config.output_directory, config.model_aliases)
    display_results(all_results)

# This is just a sample main block to demonstrate how to run the benchmarks. For the full experiment, we'll want to run this in 
# a more robust way (either CLI with recorded outputs or a notebook with saved results).
if __name__ == "__main__":
    #view_saved_results("./benchmark_redux/results")

    config = BenchmarkConfig(
        models=['gemma4'],
        repeats=1,
        task_directory="./benchmark_redux/tasks",
        output_directory="./benchmark_redux/results",
        filter_tags=[],  # empty = run all tasks; e.g. ['2d'] to filter by tag
        think=False
    )

    tasks = generate_prompts_from_directory(config.task_directory)
    tasks = filter_tasks_by_tags(tasks, config.filter_tags)

    all_results = run_benchmarks(config, tasks)
    score_results(all_results)
    save_results(all_results, config.output_directory)
    display_results(all_results)


