import argparse
from spatialreasoning.benchmark_orchestrator import BenchmarkConfig, run_full_benchmark
from spatialreasoning.benchmark_analysis import analyze_results


def _run(args):
    config = BenchmarkConfig(
        models=args.models,
        model_aliases={},
        repeats=args.repeats,
        task_directory=args.task_dir,
        output_directory=args.output_dir,
        filter_tags=args.filter_tags or [],
        think=args.think,
    )
    run_full_benchmark(config)


def _analyze(args):
    analyze_results(
        output_dir=args.output_dir,
        save_dir=args.save_dir,
        filter_tags=args.filter_tags or [],
        tag_plot_title=args.tag_title,
        plot_overall_accuracy=not args.no_overall,
    )


def main():
    parser = argparse.ArgumentParser(prog="spatialreasoning")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_p = subparsers.add_parser("run", help="Run the benchmark")
    run_p.add_argument("--models", nargs="+", required=True)
    run_p.add_argument("--task-dir", default="./tasks")
    run_p.add_argument("--output-dir", default="./results")
    run_p.add_argument("--repeats", type=int, default=1)
    run_p.add_argument("--filter-tags", nargs="*")
    run_p.add_argument("--think", action="store_true")
    run_p.set_defaults(func=_run)

    analyze_p = subparsers.add_parser("analyze", help="Analyze saved results")
    analyze_p.add_argument("--output-dir", default="./results")
    analyze_p.add_argument("--save-dir", default="./analysis")
    analyze_p.add_argument("--filter-tags", nargs="*")
    analyze_p.add_argument("--tag-title", default="")
    analyze_p.add_argument("--no-overall", action="store_true")
    analyze_p.set_defaults(func=_analyze)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
