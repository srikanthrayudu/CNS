from flask import Flask, render_template, request, jsonify
import os
from werkzeug.utils import secure_filename

from utils.model_trainer import train_model, predict_file, load_metrics, predict_live_packet
from utils.data_processing import resolve_train_test_paths

try:
    from utils.packet_sniffer import PacketSniffer
    SNIFFER_AVAILABLE = True
except Exception:
    PacketSniffer = None
    SNIFFER_AVAILABLE = False

app = Flask(__name__)

UPLOAD_DIR = "dataset"

sniffer = PacketSniffer() if SNIFFER_AVAILABLE else None
live_alerts = []


def _save_uploaded_file(file_storage):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    filename = secure_filename(file_storage.filename)
    file_path = os.path.join(UPLOAD_DIR, filename)
    file_storage.save(file_path)
    return file_path


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/api/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    file_path = _save_uploaded_file(file)
    return jsonify({"success": True, "path": file_path})


@app.route("/api/train", methods=["POST"])
def train():
    data = request.json or {}
    path = data.get("path")
    model_type = data.get("model_type", "auto")
    test_path = data.get("test_path")
    test_size = float(data.get("test_size", 0.3))
    class_weight = data.get("class_weight", "balanced")
    tune = bool(data.get("tune", False))
    if not path:
        return jsonify({"error": "Dataset path is required."}), 400
    res = train_model(
        path,
        model_type=model_type,
        test_path=test_path,
        test_size=test_size,
        class_weight=class_weight,
        tune=tune,
    )
    return jsonify(res)


@app.route("/api/predict", methods=["POST"])
def predict():
    if "file" in request.files:
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400
        path = _save_uploaded_file(file)
    else:
        data = request.json or {}
        path = data.get("path")

    if not path:
        return jsonify({"error": "Prediction dataset path is required."}), 400

    result = predict_file(path)

    predictions = result.get("predictions", [])
    summary = result.get("summary", {})
    label_summary = result.get("label_summary", {})

    return jsonify(
        {
            "success": True,
            "summary": summary,
            "label_summary": label_summary,
            "sample_predictions": predictions[:10],
        }
    )


@app.route("/api/metrics", methods=["GET"])
def metrics():
    data = load_metrics()
    if data is None:
        return jsonify({"error": "No metrics available. Train a model first."}), 404
    return jsonify(data)


@app.route("/api/live/start", methods=["POST"])
def live_start():
    if not SNIFFER_AVAILABLE:
        return jsonify({"error": "Scapy is not installed."}), 400
    if not sniffer.sniffing:
        sniffer.start()
    return jsonify({"success": True})


@app.route("/api/live/stop", methods=["POST"])
def live_stop():
    if not SNIFFER_AVAILABLE:
        return jsonify({"error": "Scapy is not installed."}), 400
    sniffer.stop()
    return jsonify({"success": True})


@app.route("/api/live/alerts", methods=["GET"])
def live_alerts_api():
    if not SNIFFER_AVAILABLE:
        return jsonify({"error": "Scapy is not installed."}), 400

    alerts = []
    for packet in sniffer.latest_packets():
        try:
            prediction = predict_live_packet(packet["features"])
            label = prediction["predictions"][0]
            binary = prediction["binary"][0]
            if binary == "ATTACK":
                alerts.append(
                    {
                        "src": packet["src"],
                        "dst": packet["dst"],
                        "category": label,
                        "timestamp": packet["timestamp"],
                    }
                )
        except Exception:
            continue

    live_alerts.extend(alerts)
    live_alerts[:] = live_alerts[-50:]

    return jsonify({"alerts": live_alerts, "sniffing": sniffer.sniffing})


@app.route("/api/live/clear", methods=["POST"])
def live_clear():
    if not SNIFFER_AVAILABLE:
        return jsonify({"error": "Scapy is not installed."}), 400
    live_alerts.clear()
    return jsonify({"success": True})


@app.route("/api/dataset/auto", methods=["POST"])
def dataset_auto():
    data = request.json or {}
    hint = data.get("hint", "train")
    train_path, test_path = resolve_train_test_paths(hint)
    if not train_path:
        return jsonify({"error": "Dataset not found. Install kagglehub or provide local files."}), 404
    return jsonify({"train_path": train_path, "test_path": test_path})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
