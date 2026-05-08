from dataclasses import dataclass
from .benchmark_types import Score

"""This module contains functions for scoring model predictions against correct answers using specified scoring functions. 
The main function is score_prediction, which takes a prediction, target, and list of scoring function names, and returns a 
list of Score dataclasses with the calculated scores for each function.

To Add New Scoring Functions:
1. Implement a new scoring function that takes a prediction and target and returns a calculated score (e.g., a float between 0 and 1).
2. Add a new case in the score_prediction function to call your new scoring function when its name is included in the scoring_function_name list.
3. Use the new scoring function in your task configurations by including its name in the scoring_functions list for a task.
"""



# TODO: Expand these with more complex scoring functions and have them take in the entire task result for more context

def binary_match_score(pred, target):
    """A simple scoring function that returns 1.0 if the prediction exactly matches the target (after stripping whitespace, lowercasing, 
    and removing newlines), and 0.0 otherwise.
    """

    if isinstance(pred, str) and isinstance(target, str):
        pred = pred.strip().lower().replace("\n", " ")
        target = target.strip().lower().replace("\n", " ")

    return 1.0 if pred == target else 0.0

def debug_binary_match_score(pred, target):
    score = binary_match_score(pred, target)
    print(f"Predicted: '{pred}', Target: '{target}', Score: {score}")
    return score


def score_prediction(pred, target, scoring_function_name: list=['binary_match']):
    """Given a prediction and target, calculate scores using the specified scoring functions. Returns a list of Score dataclasses with function names and calculated scores."""
    
    scores = []
    for scoring_function in scoring_function_name:
        if scoring_function == 'binary_match':
            scores.append(Score(score_function='binary_match', calculated_score=binary_match_score(pred, target)))
        elif scoring_function == 'debug_binary_match':
            scores.append(Score(score_function='debug_binary_match', calculated_score=debug_binary_match_score(pred, target)))
        else:
            raise ValueError(f"Unknown scoring function: {scoring_function}")
    return scores