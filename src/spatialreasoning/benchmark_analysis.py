import os
import csv
import numpy as np
import matplotlib.pyplot as plt
from .benchmark_io import load_results


# ---------------------------------------------------------------------------
# Data loading & metric computation
# ---------------------------------------------------------------------------

def load_analysis_data(output_dir: str) -> dict[str, dict]:
    """Load all saved YAML results from output_dir and group by model name.

    Returns a dict keyed by model name. Each value is a dict with:
        repeat_accuracies: list[float]  — one accuracy per repeat (pooled across files)
        scores_by_tag:     dict[str, list[float]]  — per-tag scores (pooled)
    """
    raw_results = load_results(output_dir)
    grouped: dict[str, dict] = {}

    for result in raw_results:
        model = result.get("model", "unknown")
        if model not in grouped:
            grouped[model] = {"repeat_accuracies": [], "scores_by_tag": {}}

        # Per-repeat accuracies
        for repeat_scores in result.get("total_scores", []):
            if not repeat_scores:
                continue
            correct = sum(s["calculated_score"] for s in repeat_scores)
            accuracy = correct / len(repeat_scores)
            grouped[model]["repeat_accuracies"].append(accuracy)

        # Per-tag scores
        for tag, scores in (result.get("scores_by_tag") or {}).items():
            grouped[model]["scores_by_tag"].setdefault(tag, []).extend(
                s["calculated_score"] for s in scores
            )

    return grouped


def compute_tag_accuracies(model_data: dict, filter_tags: list[str]) -> dict[str, float]:
    """Return per-tag accuracy for a single model. Empty/None filter = all tags."""
    scores_by_tag = model_data.get("scores_by_tag", {})
    tags = filter_tags if filter_tags else list(scores_by_tag.keys())
    return {
        tag: (sum(scores_by_tag[tag]) / len(scores_by_tag[tag]) if scores_by_tag.get(tag) else 0.0)
        for tag in tags
        if tag in scores_by_tag
    }


# ---------------------------------------------------------------------------
# CSV export
# ---------------------------------------------------------------------------

def save_analysis_csv(analysis_data: dict[str, dict], save_path: str, filter_tags: list[str] = None) -> None:
    """Write one CSV row per model with per-repeat and per-tag accuracy columns."""
    # Determine max repeat count and all tags across models
    max_repeats = max((len(d["repeat_accuracies"]) for d in analysis_data.values()), default=0)
    all_tags = filter_tags if filter_tags else sorted(
        {tag for d in analysis_data.values() for tag in d["scores_by_tag"]}
    )

    repeat_cols = [f"repeat_{i}" for i in range(max_repeats)]
    tag_cols = [f"tag_{tag}" for tag in all_tags]
    fieldnames = ["model", "average_accuracy"] + repeat_cols + tag_cols

    os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
    with open(save_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for model, data in analysis_data.items():
            rep_accs = data["repeat_accuracies"]
            avg = float(np.mean(rep_accs)) if rep_accs else 0.0
            row = {"model": model, "average_accuracy": f"{avg:.4f}"}
            for i, col in enumerate(repeat_cols):
                row[col] = f"{rep_accs[i]:.4f}" if i < len(rep_accs) else ""
            tag_accs = compute_tag_accuracies(data, all_tags)
            for tag, col in zip(all_tags, tag_cols):
                row[col] = f"{tag_accs.get(tag, 0.0):.4f}"
            writer.writerow(row)

    print(f"Saved analysis CSV to {save_path}")


# ---------------------------------------------------------------------------
# Plots
# ---------------------------------------------------------------------------

def plot_model_accuracy(analysis_data: dict[str, dict], save_dir: str) -> None:
    """Bar chart: one bar per model, height = mean repeat accuracy, error bars = std dev."""
    models = list(analysis_data.keys())
    means = []
    stds = []
    for data in analysis_data.values():
        rep_accs = data["repeat_accuracies"]
        means.append(float(np.mean(rep_accs)) if rep_accs else 0.0)
        stds.append(float(np.std(rep_accs)) if len(rep_accs) > 1 else 0.0)

    fig, ax = plt.subplots(figsize=(max(6, len(models) * 1.5), 5))
    x = np.arange(len(models))
    bars = ax.bar(x, means, yerr=stds, capsize=5, color="steelblue", alpha=0.85, edgecolor="black")
    ax.set_xticks(x)
    ax.set_xticklabels(models, rotation=15, ha="right")
    ax.set_ylabel("Accuracy")
    ax.set_title("Per-Model Average Accuracy")
    ax.set_ylim(0, 1.05)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))
    for bar, mean in zip(bars, means):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
                f"{mean:.1%}", ha="center", va="bottom", fontsize=9)
    fig.tight_layout()
    os.makedirs(save_dir, exist_ok=True)
    path = os.path.join(save_dir, "model_accuracy.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Saved model accuracy plot to {path}")


def plot_tag_accuracy(analysis_data: dict[str, dict], save_dir: str, filter_tags: list[str] = None, tag_plot_title: str = "") -> None:
    """Grouped bar chart: x-axis = tags, one bar group per model."""
    all_tags = filter_tags if filter_tags else sorted(
        {tag for d in analysis_data.values() for tag in d["scores_by_tag"]}
    )
    if not all_tags:
        print("No tags found — skipping tag accuracy plot.")
        return

    models = list(analysis_data.keys())
    n_models = len(models)
    n_tags = len(all_tags)
    bar_width = 0.8 / n_models
    x = np.arange(n_tags)

    fig, ax = plt.subplots(figsize=(max(8, n_tags * 1.8), 5))
    for i, (model, data) in enumerate(analysis_data.items()):
        tag_accs = compute_tag_accuracies(data, all_tags)
        heights = [tag_accs.get(tag, 0.0) for tag in all_tags]
        offsets = x + (i - n_models / 2 + 0.5) * bar_width
        bars = ax.bar(offsets, heights, width=bar_width, label=model, alpha=0.85, edgecolor="black")
        for bar, h in zip(bars, heights):
            ax.text(bar.get_x() + bar.get_width() / 2, h + 0.01, f"{h:.0%}",
                    ha="center", va="bottom", fontsize=5, rotation=0 if n_models > 2 else 0)

    ax.set_xticks(x)
    ax.set_xticklabels(all_tags, rotation=15, ha="right")
    ax.set_ylabel("Accuracy")
    ax.set_title(tag_plot_title if tag_plot_title else "Per-Tag Accuracy by Model")
    ax.set_ylim(0, 1.15)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))
    ax.legend(title="Model")
    fig.tight_layout()
    os.makedirs(save_dir, exist_ok=True)
    path = os.path.join(save_dir, "tag_accuracy.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Saved tag accuracy plot to {path}")


# ---------------------------------------------------------------------------
# Top-level orchestration
# ---------------------------------------------------------------------------

def analyze_results(output_dir: str, save_dir: str, filter_tags: list[str] = None, tag_plot_title: str = "", plot_overall_accuracy: bool = True) -> None:
    """Load saved results, compute metrics, save CSV, and generate plots."""
    analysis_data = load_analysis_data(output_dir)
    if not analysis_data:
        print(f"No results found in {output_dir}")
        return

    csv_path = os.path.join(save_dir, "analysis.csv")
    save_analysis_csv(analysis_data, csv_path, filter_tags=filter_tags)
    if plot_overall_accuracy:
        plot_model_accuracy(analysis_data, save_dir)
    plot_tag_accuracy(analysis_data, save_dir, filter_tags=filter_tags, tag_plot_title=tag_plot_title)


# Example/Debugging usage
if __name__ == "__main__":
    analyze_results(
        output_dir="./benchmark_redux/results",
        save_dir="./benchmark_redux/analysis",
        filter_tags=[],  # empty = all tags; e.g. ['2d'] to restrict
        tag_plot_title="Custom Tag Plot Title",
        plot_overall_accuracy=True
    )
