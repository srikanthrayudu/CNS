import json
import os
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler

from utils.data_schema import (
    NSL_KDD_COLUMNS,
    NSL_KDD_COLUMNS_WITH_DIFFICULTY,
    CATEGORICAL_COLUMNS,
    map_attack_to_category,
)


NSL_KDD_KAGGLE_DATASET = "hassan06/nslkdd"


def load_nsl_kdd(dataset_path):
    df = pd.read_csv(dataset_path)

    if "label" not in df.columns:
        if df.shape[1] == len(NSL_KDD_COLUMNS_WITH_DIFFICULTY):
            df.columns = NSL_KDD_COLUMNS_WITH_DIFFICULTY
        elif df.shape[1] == len(NSL_KDD_COLUMNS):
            df.columns = NSL_KDD_COLUMNS
        else:
            df.columns = [f"feature_{i}" for i in range(df.shape[1])]

    if "difficulty" in df.columns:
        df = df.drop(columns=["difficulty"])

    if "label" not in df.columns:
        df = df.rename(columns={df.columns[-1]: "label"})

    return df


def build_attack_category(df):
    df = df.copy()
    df["attack_category"] = df["label"].apply(map_attack_to_category)
    return df


def _fit_label_encoder(series):
    series = series.astype(str).fillna("unknown")
    if "unknown" not in series.values:
        series = series.tolist() + ["unknown"]
    le = LabelEncoder()
    le.fit(series)
    return le


def _transform_with_encoder(le, series):
    series = series.astype(str).fillna("unknown")
    unknown_value = "unknown" if "unknown" in le.classes_ else le.classes_[0]
    series = series.apply(lambda v: v if v in le.classes_ else unknown_value)
    return le.transform(series)


def prepare_features(df, encoders=None, scaler=None, fit=False):
    df = df.copy()
    feature_columns = [col for col in df.columns if col not in ("label", "attack_category")]
    X = df[feature_columns]

    if encoders is None:
        encoders = {}

    for col in CATEGORICAL_COLUMNS:
        if col not in X.columns:
            continue
        if fit or col not in encoders:
            encoders[col] = _fit_label_encoder(X[col])
        X[col] = _transform_with_encoder(encoders[col], X[col])

    X = X.fillna(0)

    if scaler is None:
        scaler = StandardScaler()

    if fit:
        X_scaled = scaler.fit_transform(X)
    else:
        X_scaled = scaler.transform(X)

    return X_scaled, encoders, scaler, feature_columns


def encode_labels(labels, label_encoder=None, fit=False):
    if label_encoder is None:
        label_encoder = LabelEncoder()

    labels = labels.astype(str)

    if fit:
        if "Unknown" not in labels.values:
            labels = labels.tolist() + ["Unknown"]
        encoded = label_encoder.fit_transform(labels)
    else:
        known = set(label_encoder.classes_)
        fallback = "Unknown" if "Unknown" in known else label_encoder.classes_[0]
        labels = labels.apply(lambda v: v if v in known else fallback)
        encoded = label_encoder.transform(labels)

    return encoded, label_encoder


def save_feature_columns(columns, path):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(columns, handle, indent=2)


def load_feature_columns(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _download_nsl_kdd():
    try:
        import kagglehub
    except Exception:
        return None

    try:
        return kagglehub.dataset_download(NSL_KDD_KAGGLE_DATASET)
    except Exception:
        return None


def _find_csv_paths(root_dir):
    csv_paths = []
    for root, _dirs, files in os.walk(root_dir or ""):
        for filename in files:
            if filename.lower().endswith(".csv"):
                csv_paths.append(os.path.join(root, filename))
    return csv_paths


def _pick_candidate(csv_paths, dataset_path):
    if not csv_paths:
        return None

    candidate_name = os.path.basename(dataset_path) if dataset_path else ""
    if candidate_name:
        for path in csv_paths:
            if os.path.basename(path) == candidate_name:
                return path

    hint = (dataset_path or "").lower()
    if "test" in hint:
        for path in csv_paths:
            if "test" in os.path.basename(path).lower():
                return path
    if "train" in hint:
        for path in csv_paths:
            if "train" in os.path.basename(path).lower():
                return path

    for name in ("KDDTrain+.csv", "KDDTest+.csv"):
        for path in csv_paths:
            if os.path.basename(path) == name:
                return path

    return sorted(csv_paths)[0]


def resolve_dataset_path(dataset_path):
    if dataset_path and os.path.exists(dataset_path):
        return dataset_path

    download_dir = _download_nsl_kdd()
    if not download_dir:
        return dataset_path

    csv_paths = _find_csv_paths(download_dir)
    candidate = _pick_candidate(csv_paths, dataset_path)
    return candidate or dataset_path


def resolve_train_test_paths(train_path, test_path=None):
    resolved_train = train_path
    resolved_test = test_path

    if train_path and os.path.isdir(train_path):
        csv_paths = _find_csv_paths(train_path)
        resolved_train = _pick_candidate(csv_paths, "train")
        resolved_test = _pick_candidate(csv_paths, "test")
        return resolved_train, resolved_test

    if train_path and os.path.exists(train_path):
        if not test_path:
            csv_paths = _find_csv_paths(os.path.dirname(train_path))
            resolved_test = _pick_candidate(csv_paths, "test")
        if resolved_test and os.path.exists(resolved_test):
            return train_path, resolved_test
        return train_path, None

    download_dir = _download_nsl_kdd()
    if not download_dir:
        return train_path, test_path

    csv_paths = _find_csv_paths(download_dir)
    resolved_train = _pick_candidate(csv_paths, train_path or "train")
    resolved_test = _pick_candidate(csv_paths, test_path or "test")
    return resolved_train, resolved_test


def summarize_dataset(df, label_column="attack_category"):
    df = df.copy()
    summary = {
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "missing_values": int(df.isna().sum().sum()),
    }

    if label_column in df.columns:
        counts = df[label_column].value_counts(dropna=False)
        summary["class_distribution"] = counts.to_dict()

    return summary
