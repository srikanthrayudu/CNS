# AI-Based Network Intrusion Detection System (NIDS)

A final-year mini project that uses machine learning to detect malicious network traffic and classify attacks (DoS, Probe, R2L, U2R) using the NSL-KDD dataset.

## Features
- Dataset upload, preprocessing, and training
- Model comparison (Decision Tree, Random Forest, SVM) with auto-selection
- Metrics: accuracy, precision, recall, F1-score, confusion matrix
- Prediction from CSV files
- Optional live packet monitoring using Scapy
- Flask dashboard with charts and alerts

## Project Structure
```
AI_NIDS/
├── app.py
├── main.py
├── requirements.txt
├── dataset/
├── models/
├── static/
│   ├── css/
│   └── js/
├── templates/
├── notebooks/
├── utils/
├── trained_model/
├── docs/
└── screenshots/
```

## Setup
1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the web app:

```bash
python app.py
```

3. Open the dashboard at `http://127.0.0.1:5000/dashboard`.

## Usage
1. Upload the NSL-KDD CSV file on the dashboard.
2. Train the model (Auto, Random Forest, Decision Tree, SVM).
3. View metrics and confusion matrix charts.
4. Upload a CSV for predictions.
5. (Optional) Start live packet monitoring if Scapy is installed and permitted.

## CLI (Optional)
Train and predict from the terminal:

```bash
python main.py train --data dataset/KDDTrain+.csv --model auto
python main.py predict --data dataset/KDDTest+.csv --out dataset/predictions.csv
python main.py metrics
```

## Dashboard Highlights
- Confusion matrix chart + table
- Attack category distribution from predictions
- Live alert stream with clear button

## Dataset Notes
- NSL-KDD has 41 features and a label column.
- The trainer accepts files with or without headers. If headers are missing, the standard NSL-KDD column names are applied.

## Dataset Download (KaggleHub)
If the dataset path you provide does not exist, the trainer will try to auto-download NSL-KDD using `kagglehub` (if installed). You can also run it manually:

```python
import kagglehub

# Download latest version
path = kagglehub.dataset_download("hassan06/nslkdd")
print("Path to dataset files:", path)
```

Then point the dashboard or CLI to the CSV in the downloaded folder.

## Architecture Diagram
See `docs/diagrams/architecture.md` for the mermaid diagram.

## Flowchart
See `docs/diagrams/flowchart.md` for the mermaid flowchart.

## Screenshots
Place screenshots in `screenshots/` and update `screenshots/README.md` with actual images.

## Documents
- Report: `docs/report.md`
- Presentation: `docs/presentation.md`
- Viva Q&A: `docs/viva_questions.md`

## Sample Output
- Training metrics are saved to `trained_model/metrics.json`.
- Model artifacts are saved to `trained_model/`.

## Limitations
- Live packet features are simplified compared to NSL-KDD.
- Real-time predictions depend on system permissions for packet capture.

## Future Enhancements
- Stream-based feature extraction
- Deep learning models (CNN/LSTM)
- Ensemble stacking for higher accuracy
- Web-based report export

## Fine-Tuning Notes
- If a `KDDTrain+.csv` and `KDDTest+.csv` pair is available, the trainer uses it automatically.
- If no test file is found, a stratified random split is used (default 70/30).
- Optional class weighting helps with imbalance (`balanced` by default).
- Use `--tune` in the CLI for a small parameter grid search.

Example:

```bash
python main.py train --data dataset/KDDTrain+.csv --test dataset/KDDTest+.csv --model random_forest --class-weight balanced --tune
```
# CNS
