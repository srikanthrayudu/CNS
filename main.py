import argparse
import json
import os
import pandas as pd

from utils.model_trainer import train_model, predict_file, load_metrics


def _write_predictions(input_path, result, output_path):
    df = pd.read_csv(input_path)
    df["prediction"] = result.get("predictions", [])
    df["binary"] = result.get("binary", [])
    df.to_csv(output_path, index=False)


def _print_json(payload):
    print(json.dumps(payload, indent=2))


def _add_train_args(subparsers):
    train_parser = subparsers.add_parser("train", help="Train a model on NSL-KDD CSV")
    train_parser.add_argument("--data", required=True, help="Path to NSL-KDD CSV or directory")
    train_parser.add_argument(
        "--model",
        default="auto",
        choices=["auto", "random_forest", "decision_tree", "svm"],
        help="Model type to train",
    )
    train_parser.add_argument("--test", default=None, help="Optional test CSV path")
    train_parser.add_argument("--test-size", default=0.3, type=float, help="Holdout size if no test file")
    train_parser.add_argument(
        "--class-weight",
        default="balanced",
        choices=["balanced", "none"],
        help="Class weighting strategy",
    )
    train_parser.add_argument("--tune", action="store_true", help="Enable lightweight parameter tuning")


def _add_predict_args(subparsers):
    predict_parser = subparsers.add_parser("predict", help="Predict labels for a CSV file")
    predict_parser.add_argument("--data", required=True, help="Path to CSV for prediction")
    predict_parser.add_argument(
        "--out",
        default=None,
        help="Optional output CSV with prediction columns",
    )


def _add_metrics_args(subparsers):
    subparsers.add_parser("metrics", help="Print latest training metrics")


def main():
    parser = argparse.ArgumentParser(description="AI-Based NIDS CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    _add_train_args(subparsers)
    _add_predict_args(subparsers)
    _add_metrics_args(subparsers)

    args = parser.parse_args()

    if args.command == "train":
        response = train_model(
            args.data,
            args.model,
            test_path=args.test,
            test_size=args.test_size,
            class_weight=args.class_weight,
            tune=args.tune,
        )
        _print_json(response)
        return

    if args.command == "predict":
        if not os.path.exists(args.data):
            _print_json({"error": "Prediction dataset not found."})
            return
        result = predict_file(args.data)
        if args.out:
            _write_predictions(args.data, result, args.out)
            _print_json({"success": True, "output": args.out, "summary": result.get("summary", {})})
        else:
            _print_json(result)
        return

    if args.command == "metrics":
        metrics = load_metrics()
        if metrics is None:
            _print_json({"error": "No metrics available. Train a model first."})
            return
        _print_json(metrics)


if __name__ == "__main__":
    main()
