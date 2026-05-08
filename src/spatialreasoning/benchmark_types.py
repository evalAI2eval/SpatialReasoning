from dataclasses import dataclass, field
from typing import List

@dataclass
class Score:
    score_function: str
    calculated_score: float

@dataclass
class Task:
    task_name: str
    prompt: str
    correct_answer: str
    system_prompt: str = ""
    scoring_functions: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)


@dataclass
class TaskResult:
    task: Task
    response: str


@dataclass
class BenchmarkResult:
    model: str
    task_results: List[TaskResult]
    repeat_index: int = 0
    timestamp: str = ""

    def get_response_correct_pairs(self):
        return [(tr.response, tr.task.correct_answer) for tr in self.task_results]