# Project Report: AI-Based Network Intrusion Detection System (NIDS)

## 1. Introduction
Network Intrusion Detection Systems (NIDS) monitor traffic for malicious behavior. Traditional signature-based systems struggle with new attack patterns. This project uses machine learning to classify network traffic and detect attacks.

## 2. Existing System
- Rule-based and signature-based IDS dominate many deployments.
- High maintenance for signature updates.
- Limited accuracy on unseen or evolving attacks.

## 3. Proposed System
- ML-based classification using NSL-KDD.
- Automatic model selection (Random Forest, Decision Tree, SVM).
- Dashboard with metrics, predictions, and optional live alerts.

## 4. Objectives
- Detect malicious traffic and classify attack categories.
- Provide clear visualizations of model performance.
- Offer a beginner-friendly dashboard suitable for demos and viva.

## 5. Dataset
- **NSL-KDD** with 41 features and a label column.
- Preprocessing steps: encoding categorical features, scaling numeric values.

## 6. Methodology
1. Load dataset and assign column names (if missing).
2. Map attack labels to categories (Normal, DoS, Probe, R2L, U2R).
3. Encode categorical fields and scale features.
4. Train multiple models and select the best based on F1-score.
5. Save model artifacts and evaluate on test data.

## 7. System Architecture
See `docs/diagrams/architecture.md` for the mermaid diagram.

## 8. Flowchart
See `docs/diagrams/flowchart.md` for the mermaid flowchart.

## 9. Results
- Metrics include accuracy, precision, recall, F1-score, and confusion matrix.
- Best model is stored in `trained_model/` for reuse.

## 10. Advantages
- Faster detection than manual rules.
- Scalable to large datasets.
- Easy visualization and reporting for evaluation.

## 11. Applications
- Campus network monitoring.
- Enterprise security labs.
- Educational demos for cybersecurity courses.

## 12. Limitations
- Live packet prediction uses simplified features.
- Dataset-driven training may not generalize to all real traffic patterns.

## 13. Future Enhancements
- Real-time feature extraction pipeline.
- Deep learning models (LSTM/CNN).
- Streaming dashboards and alert notifications.

## 14. Conclusion
The AI-based NIDS provides an end-to-end ML workflow for detecting network intrusions, with a user-friendly dashboard and optional live monitoring suitable for academic evaluation.
