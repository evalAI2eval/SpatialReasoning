from typing import List
from datetime import datetime
from .ollama_wrapper import ModelQuery
from .benchmark_types import Task, TaskResult, BenchmarkResult


class BenchmarkRunner:
    """Class responsible for running a benchmark for a given model and set of tasks, producing a BenchmarkResult with responses and correct answers."""
    def __init__(self, model: str = 'gemma3', tasks: List[Task] = None, debug_mode: bool = True):
        self.model = model
        self.tasks: List[Task] = tasks or []
        self.result: BenchmarkResult = None
        self.debug_mode = debug_mode

    def run_benchmark(self, repeat_index: int = 0, think: bool = False) -> BenchmarkResult:
        task_results = []
        task_count = 0
        task_total = len(self.tasks)
        for task in self.tasks:
            if self.debug_mode: print(f"Running task: {task_count}/{task_total} (Repeat {repeat_index + 1})")
            query = ModelQuery(
                model=self.model,
                system_prompt=task.system_prompt,
                role='user',
                prompt_content=[task.prompt],
                think=think
            )
            query.run_query()
            response_text = query.responses[0].message.content
            task_results.append(TaskResult(task=task, response=response_text))
            if self.debug_mode:
                print(f"Response: {response_text}\nCorrect Answer: {task.correct_answer}\n")
                task_count += 1

        self.result = BenchmarkResult(
            model=self.model,
            task_results=task_results,
            repeat_index=repeat_index,
            timestamp=datetime.now().isoformat(timespec='seconds'),
        )
        return self.result

    def get_response_correct_response_pairs(self):
        if self.result is None:
            raise ValueError("Benchmark has not been run yet. Call run_benchmark() first.")
        return self.result.get_response_correct_pairs()


# Example usage/Debugging
if __name__ == "__main__":
    from src.spatialreasoning.benchmark_io import generate_prompts_from_directory

    tasks = generate_prompts_from_directory("./benchmark_redux/tasks")
    runner = BenchmarkRunner(model='gemma3', tasks=tasks)
    result = runner.run_benchmark()

    for response, correct_answer in result.get_response_correct_pairs():
        print(f'Response:       {response}')
        print(f'Correct Answer: {correct_answer}\n')

