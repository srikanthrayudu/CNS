1. **What is NIDS?**
   A Network Intrusion Detection System monitors traffic to identify malicious activity.
2. **Why use ML for NIDS?**
   ML can learn patterns from data and detect unknown or evolving attacks.
3. **What is the NSL-KDD dataset?**
   An improved version of KDD Cup 99 with reduced redundancy and labeled attack types.
4. **Which attack categories are supported?**
   Normal, DoS, Probe, R2L, and U2R.
5. **How are categorical features handled?**
   Label encoding is applied to protocol_type, service, and flag.
6. **Why Random Forest?**
   It handles non-linear patterns well and reduces overfitting with ensembles.
7. **How is the best model selected?**
   The system compares models using weighted F1-score and picks the highest.
8. **What evaluation metrics are used?**
   Accuracy, precision, recall, F1-score, and confusion matrix.
9. **What is a confusion matrix?**
   A table showing correct vs incorrect predictions across classes.
10. **What are the limitations of this project?**
    Live packet features are simplified and may not match full dataset features.
11. **What is the role of scaling?**
    It normalizes feature ranges for better model performance, especially for SVM.
12. **Can the model detect zero-day attacks?**
    It can generalize patterns but cannot guarantee detection of unseen attacks.
13. **How is live packet capture implemented?**
    Using Scapy to capture packets and map basic fields to NSL-KDD features.
14. **How can accuracy be improved?**
    Use more features, tune hyperparameters, or add deep learning models.
15. **What is the future scope?**
    Real-time streaming, advanced models, and alert notifications.
