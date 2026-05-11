import json
import os
import joblib
import pandas as pd
from sklearn.base import clone
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.model_selection import train_test_split, ParameterGrid
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

from utils.data_processing import (
    load_nsl_kdd,
    build_attack_category,
    prepare_features,
    encode_labels,
    save_feature_columns,
    load_feature_columns,
    resolve_dataset_path,
    resolve_train_test_paths,
    summarize_dataset,
)

ARTIFACT_DIR = "trained_model"
MODEL_PATH = os.path.join(ARTIFACT_DIR, "model.pkl")
SCALER_PATH = os.path.join(ARTIFACT_DIR, "scaler.pkl")
ENCODERS_PATH = os.path.join(ARTIFACT_DIR, "encoders.pkl")
LABEL_ENCODER_PATH = os.path.join(ARTIFACT_DIR, "label_encoder.pkl")
FEATURE_COLUMNS_PATH = os.path.join(ARTIFACT_DIR, "feature_columns.json")
METRICS_PATH = os.path.join(ARTIFACT_DIR, "metrics.json")
MODEL_INFO_PATH = os.path.join(ARTIFACT_DIR, "model_info.json")


def _ensure_artifact_dir():
    os.makedirs(ARTIFACT_DIR, exist_ok=True)


def _evaluate_model(y_true, y_pred):
    return {
        "accuracy": round(accuracy_score(y_true, y_pred), 4),
        "precision": round(precision_score(y_true, y_pred, average="weighted", zero_division=0), 4),
        "recall": round(recall_score(y_true, y_pred, average="weighted", zero_division=0), 4),
        "f1": round(f1_score(y_true, y_pred, average="weighted", zero_division=0), 4),
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
    }


def _get_models(class_weight=None):
    return {
        "random_forest": RandomForestClassifier(
            n_estimators=150,
            random_state=42,
            class_weight=class_weight,
        ),
        "decision_tree": DecisionTreeClassifier(random_state=42, class_weight=class_weight),
        "svm": SVC(kernel="rbf", probability=True, random_state=42, class_weight=class_weight),
    }


def _get_param_grids():
    return {
        "random_forest": {
            "n_estimators": [150, 250],
            "max_depth": [None, 24],
            "min_samples_split": [2, 4],
        },
        "decision_tree": {
            "max_depth": [None, 24, 32],
            "min_samples_split": [2, 4],
        },
        "svm": {
            "C": [1.0, 3.0],
            "gamma": ["scale"],
        },
    }


def train_model(dataset_path, model_type="auto", test_path=None, test_size=0.3, class_weight="balanced", tune=False):
    try:
        train_path, resolved_test_path = resolve_train_test_paths(dataset_path, test_path)
        if not train_path or not os.path.exists(train_path):
            return {
                "error": "Dataset not found. Provide a valid CSV path or install kagglehub for auto-download."
            }

        df_train = load_nsl_kdd(train_path)
        df_train = build_attack_category(df_train)
        train_summary = summarize_dataset(df_train)

        X_scaled, encoders, scaler, feature_columns = prepare_features(df_train, fit=True)
        y_encoded, label_encoder = encode_labels(df_train["attack_category"], fit=True)

        test_summary = None
        if resolved_test_path and os.path.exists(resolved_test_path):
            df_test = load_nsl_kdd(resolved_test_path)
            df_test = build_attack_category(df_test)
            test_summary = summarize_dataset(df_test)
            X_test, _enc, _scaler, _cols = prepare_features(
                df_test, encoders=encoders, scaler=scaler, fit=False
            )
            y_test, _ = encode_labels(df_test["attack_category"], label_encoder=label_encoder, fit=False)
            X_train, y_train = X_scaled, y_encoded
        else:
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled,
                y_encoded,
                test_size=test_size,
                random_state=42,
                stratify=y_encoded,
            )

        models = _get_models(class_weight=class_weight if class_weight != "none" else None)
        selected_models = models
        if model_type in models:
            selected_models = {model_type: models[model_type]}

        best_name = None
        best_model = None
        best_metrics = None

        param_grids = _get_param_grids()

        for name, model in selected_models.items():
            if tune and name in param_grids:
                for params in ParameterGrid(param_grids[name]):
                    candidate = clone(model).set_params(**params)
                    candidate.fit(X_train, y_train)
                    y_pred = candidate.predict(X_test)
                    metrics = _evaluate_model(y_test, y_pred)
                    if best_metrics is None or metrics["f1"] > best_metrics["f1"]:
                        best_name = name
                        best_model = candidate
                        best_metrics = metrics
            else:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
                metrics = _evaluate_model(y_test, y_pred)
                if best_metrics is None or metrics["f1"] > best_metrics["f1"]:
                    best_name = name
                    best_model = model
                    best_metrics = metrics

        _ensure_artifact_dir()
        joblib.dump(best_model, MODEL_PATH)
        joblib.dump(scaler, SCALER_PATH)
        joblib.dump(encoders, ENCODERS_PATH)
        joblib.dump(label_encoder, LABEL_ENCODER_PATH)
        save_feature_columns(feature_columns, FEATURE_COLUMNS_PATH)

        metrics_payload = {
            **best_metrics,
            "labels": label_encoder.classes_.tolist(),
            "best_model": best_name,
            "test_source": resolved_test_path or "random_split",
            "class_weight": class_weight,
            "tuned": bool(tune),
            "train_summary": train_summary,
            "test_summary": test_summary,
        }

        with open(METRICS_PATH, "w", encoding="utf-8") as handle:
            json.dump(metrics_payload, handle, indent=2)

        with open(MODEL_INFO_PATH, "w", encoding="utf-8") as handle:
            json.dump({"best_model": best_name, "model_type": model_type}, handle, indent=2)

        response = {
            "success": True,
            "best_model": best_name,
            "metrics": best_metrics,
            "train_summary": train_summary,
            "test_summary": test_summary,
        }
        return response

    except Exception as exc:
        return {"error": str(exc)}


def load_artifacts():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError("Model artifacts not found. Train a model first.")

    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    encoders = joblib.load(ENCODERS_PATH)
    label_encoder = joblib.load(LABEL_ENCODER_PATH)
    feature_columns = load_feature_columns(FEATURE_COLUMNS_PATH)
    return model, scaler, encoders, label_encoder, feature_columns


def _align_features(df, feature_columns):
    for col in feature_columns:
        if col not in df.columns:
            df[col] = 0
    return df[feature_columns]


def predict_dataframe(df):
    model, scaler, encoders, label_encoder, feature_columns = load_artifacts()
    df = df.copy()
    df = _align_features(df, feature_columns)

    X_scaled, _, _scaler, _columns = prepare_features(
        df, encoders=encoders, scaler=scaler, fit=False
    )

    preds = model.predict(X_scaled)
    labels = label_encoder.inverse_transform(preds)
    binary = ["NORMAL" if label == "Normal" else "ATTACK" for label in labels]

    summary = {"NORMAL": 0, "ATTACK": 0}
    for item in binary:
        summary[item] += 1

    label_summary = {}
    for label in labels:
        label_summary[label] = label_summary.get(label, 0) + 1

    return {
        "predictions": labels.tolist(),
        "binary": binary,
        "summary": summary,
        "label_summary": label_summary,
    }


def predict_file(dataset_path):
    dataset_path = resolve_dataset_path(dataset_path)
    if not dataset_path or not os.path.exists(dataset_path):
        raise FileNotFoundError(
            "Prediction dataset not found. Provide a valid CSV path or install kagglehub."
        )
    df = load_nsl_kdd(dataset_path)
    if "label" in df.columns:
        df = df.drop(columns=["label"])
    return predict_dataframe(df)


def predict_live_packet(feature_dict):
    df = pd.DataFrame([feature_dict])
    return predict_dataframe(df)


def load_metrics():
    if not os.path.exists(METRICS_PATH):
        return None
    with open(METRICS_PATH, "r", encoding="utf-8") as handle:
        return json.load(handle)
