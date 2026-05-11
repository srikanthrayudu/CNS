# Architecture Diagram

```mermaid
graph TD
    A[User / Admin] --> B[Flask Dashboard]
    B --> C[Dataset Upload]
    B --> D[Model Training]
    B --> E[Prediction Service]
    D --> F[Preprocessing
(Encoding + Scaling)]
    F --> G[Model Selection
RF / DT / SVM]
    G --> H[Saved Artifacts]
    E --> H
    B --> I[Metrics & Charts]
    B --> J[Live Packet Monitor
(Optional)]
    J --> E
```
