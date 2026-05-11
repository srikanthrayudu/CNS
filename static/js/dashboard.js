let uploadedPath = "";
let metricsChart = null;
let confusionChart = null;
let attackChart = null;
let liveInterval = null;
let datasetAutoTried = false;
let autoTrainTriggered = false;

function setUploadStatus(message) {
    document.getElementById("uploadPath").innerText = message;
}

function uploadFile() {
    const fileInput = document.getElementById("dataset");
    if (!fileInput.files.length) {
        alert("Please select a dataset file.");
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    fetch("/api/upload", { method: "POST", body: formData })
        .then((res) => res.json())
        .then((data) => {
            if (data.success) {
                uploadedPath = data.path;
                setUploadStatus(`Uploaded: ${uploadedPath}`);
            } else {
                alert(data.error || "Upload failed.");
            }
        })
        .catch(() => alert("Upload failed."));
}

function trainModel(options = {}) {
    const skipEnsure = options.skipEnsure || false;
    const isAuto = options.auto || false;

    if (!uploadedPath && !skipEnsure) {
        ensureDatasetPath({ force: true }).then((resolved) => {
            if (!resolved) {
                alert("Upload a dataset or use Kaggle auto-download first.");
                return;
            }
            trainModel({ skipEnsure: true, auto: isAuto });
        });
        return;
    }

    if (isAuto) {
        document.getElementById("trainResult").innerText = "Auto training started...";
    }

    const modelType = document.getElementById("modelType").value;
    const testPath = document.getElementById("testPath").value.trim();
    const testSize = parseFloat(document.getElementById("testSize").value || "0.3");
    const classWeight = document.getElementById("classWeight").value;
    const tune = document.getElementById("tuneModel").checked;

    fetch("/api/train", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            path: uploadedPath,
            model_type: modelType,
            test_path: testPath || null,
            test_size: testSize,
            class_weight: classWeight,
            tune: tune
        })
    })
        .then((res) => res.json())
        .then((data) => {
            if (data.success) {
                document.getElementById("modelStatus").innerText = `Model: ${data.best_model}`;
                document.getElementById("trainResult").innerText = JSON.stringify(data.metrics, null, 2);
                renderDatasetInsights(data.train_summary, data.test_summary);
                loadMetrics();
            } else {
                document.getElementById("trainResult").innerText = data.error || "Training failed.";
            }
        })
        .catch(() => {
            document.getElementById("trainResult").innerText = "Training failed.";
        });
}

function predictFile() {
    const fileInput = document.getElementById("predictFile");
    if (!fileInput.files.length) {
        alert("Select a CSV file for prediction.");
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    fetch("/api/predict", { method: "POST", body: formData })
        .then((res) => res.json())
        .then((data) => {
            if (data.success) {
                renderAttackStats(data.label_summary || {}, data.summary || {});
                renderPredictSummary(data.summary || {}, data.label_summary || {});
                document.getElementById("predictResult").innerText = JSON.stringify(data, null, 2);
            } else {
                document.getElementById("predictResult").innerText = data.error || "Prediction failed.";
            }
        })
        .catch(() => {
            document.getElementById("predictResult").innerText = "Prediction failed.";
        });
}

function loadMetrics() {
    fetch("/api/metrics")
        .then((res) => res.json())
        .then((data) => {
            if (data.error) {
                return;
            }
            renderMetricsChart(data);
            renderConfusionChart(data.confusion_matrix, data.labels || []);
            renderConfusionTable(data.confusion_matrix, data.labels || []);
        });
}

function renderMetricsChart(metrics) {
    const ctx = document.getElementById("metricsChart").getContext("2d");
    const labels = ["accuracy", "precision", "recall", "f1"];
    const values = labels.map((label) => metrics[label] || 0);

    if (metricsChart) {
        metricsChart.destroy();
    }

    metricsChart = new Chart(ctx, {
        type: "bar",
        data: {
            labels,
            datasets: [
                {
                    label: "Score",
                    data: values,
                    backgroundColor: "#2563eb"
                }
            ]
        },
        options: {
            scales: {
                y: { min: 0, max: 1 }
            }
        }
    });
}

function renderConfusionChart(matrix, labels) {
    if (!matrix || !matrix.length) {
        return;
    }

    const classLabels = labels.length ? labels : matrix.map((_row, idx) => `C${idx}`);
    const chartLabels = [];
    const values = [];
    for (let i = 0; i < matrix.length; i += 1) {
        for (let j = 0; j < matrix[i].length; j += 1) {
            chartLabels.push(`${classLabels[i]}->${classLabels[j]}`);
            values.push(matrix[i][j]);
        }
    }

    const ctx = document.getElementById("confusionChart").getContext("2d");

    if (confusionChart) {
        confusionChart.destroy();
    }

    confusionChart = new Chart(ctx, {
        type: "bar",
        data: {
            labels: chartLabels,
            datasets: [
                {
                    label: "Confusion Matrix",
                    data: values,
                    backgroundColor: "#94a3b8"
                }
            ]
        },
        options: {
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: { display: false }
            }
        }
    });
}

function renderConfusionTable(matrix, labels) {
    const table = document.getElementById("confusionTable");
    table.innerHTML = "";

    if (!matrix || !matrix.length) {
        return;
    }

    const classLabels = labels.length ? labels : matrix.map((_row, idx) => `C${idx}`);

    const headerRow = document.createElement("tr");
    headerRow.appendChild(document.createElement("th"));
    classLabels.forEach((label) => {
        const th = document.createElement("th");
        th.innerText = label;
        headerRow.appendChild(th);
    });
    table.appendChild(headerRow);

    matrix.forEach((row, i) => {
        const tr = document.createElement("tr");
        const rowHeader = document.createElement("th");
        rowHeader.innerText = classLabels[i];
        tr.appendChild(rowHeader);
        row.forEach((cell) => {
            const td = document.createElement("td");
            td.innerText = cell;
            tr.appendChild(td);
        });
        table.appendChild(tr);
    });
}

function renderAttackStats(labelSummary, binarySummary) {
    const labels = Object.keys(labelSummary || {});
    const values = labels.map((label) => labelSummary[label]);
    const summaryText = Object.entries(binarySummary || {})
        .map(([key, value]) => `${key}: ${value}`)
        .join(" | ");

    document.getElementById("attackSummary").innerText = summaryText || "No predictions yet.";

    if (!labels.length) {
        if (attackChart) {
            attackChart.destroy();
            attackChart = null;
        }
        return;
    }

    const ctx = document.getElementById("attackChart").getContext("2d");
    if (attackChart) {
        attackChart.destroy();
    }

    attackChart = new Chart(ctx, {
        type: "doughnut",
        data: {
            labels,
            datasets: [
                {
                    data: values,
                    backgroundColor: ["#2563eb", "#f97316", "#ef4444", "#22c55e", "#a855f7"]
                }
            ]
        },
        options: {
            plugins: {
                legend: { position: "bottom" }
            }
        }
    });
}

function renderPredictSummary(summary, labelSummary) {
    const lines = [];
    Object.entries(summary || {}).forEach(([key, value]) => {
        lines.push(`${key}: ${value}`);
    });
    Object.entries(labelSummary || {}).forEach(([key, value]) => {
        lines.push(`${key}: ${value}`);
    });
    document.getElementById("predictSummary").innerText = lines.length ? lines.join("\n") : "No prediction summary.";
}

function renderDatasetInsights(trainSummary, testSummary) {
    const lines = [];

    if (trainSummary) {
        lines.push("Train summary:");
        lines.push(`Rows: ${trainSummary.rows} | Columns: ${trainSummary.columns} | Missing: ${trainSummary.missing_values}`);
        if (trainSummary.class_distribution) {
            Object.entries(trainSummary.class_distribution).forEach(([label, value]) => {
                lines.push(`Train ${label}: ${value}`);
            });
        }
    }

    if (testSummary) {
        lines.push("\nTest summary:");
        lines.push(`Rows: ${testSummary.rows} | Columns: ${testSummary.columns} | Missing: ${testSummary.missing_values}`);
        if (testSummary.class_distribution) {
            Object.entries(testSummary.class_distribution).forEach(([label, value]) => {
                lines.push(`Test ${label}: ${value}`);
            });
        }
    }

    const output = lines.length ? lines.join("\n") : "Train a model to view dataset summary.";
    document.getElementById("datasetInsights").innerText = output;
}

function startLive() {
    fetch("/api/live/start", { method: "POST" })
        .then((res) => res.json())
        .then((data) => {
            if (data.error) {
                alert(data.error);
                return;
            }
            document.getElementById("liveStatus").innerText = "Live capture running...";
            if (!liveInterval) {
                liveInterval = setInterval(fetchLiveAlerts, 3000);
            }
        });
}

function stopLive() {
    fetch("/api/live/stop", { method: "POST" })
        .then((res) => res.json())
        .then(() => {
            document.getElementById("liveStatus").innerText = "Live capture stopped.";
            if (liveInterval) {
                clearInterval(liveInterval);
                liveInterval = null;
            }
        });
}

function clearLive() {
    fetch("/api/live/clear", { method: "POST" })
        .then((res) => res.json())
        .then((data) => {
            if (data.error) {
                document.getElementById("liveStatus").innerText = data.error;
                return;
            }
            document.getElementById("alerts").innerHTML = "";
        });
}

function fetchLiveAlerts() {
    fetch("/api/live/alerts")
        .then((res) => res.json())
        .then((data) => {
            if (data.error) {
                document.getElementById("liveStatus").innerText = data.error;
                return;
            }

            const alertsList = document.getElementById("alerts");
            alertsList.innerHTML = "";
            (data.alerts || []).slice(-10).forEach((alert) => {
                const item = document.createElement("li");
                const time = new Date(alert.timestamp * 1000).toLocaleTimeString();
                item.innerText = `${time} | ${alert.src} -> ${alert.dst} | ${alert.category}`;
                alertsList.appendChild(item);
            });
        });
}

function useKaggleDataset() {
    setUploadStatus("Resolving dataset from Kaggle...");
    return fetch("/api/dataset/auto", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ hint: "train" })
    })
        .then((res) => res.json())
        .then((data) => {
            if (data.error) {
                setUploadStatus("Dataset not found. Please upload a CSV file.");
                return false;
            }
            uploadedPath = data.train_path;
            setUploadStatus(`Using: ${data.train_path}`);
            document.getElementById("testPath").value = data.test_path || "";
            return true;
        })
        .catch(() => {
            setUploadStatus("Auto-download failed. Please upload a CSV file.");
            return false;
        });
}

function ensureDatasetPath(options = {}) {
    const force = options.force || false;
    if (uploadedPath) {
        return Promise.resolve(true);
    }
    if (datasetAutoTried && !force) {
        return Promise.resolve(false);
    }
    datasetAutoTried = true;
    return useKaggleDataset();
}

function autoTrainOnLoad() {
    if (autoTrainTriggered) {
        return;
    }
    ensureDatasetPath().then((resolved) => {
        if (resolved && !autoTrainTriggered) {
            autoTrainTriggered = true;
            trainModel({ skipEnsure: true, auto: true });
        }
    });
}

autoTrainOnLoad();

loadMetrics();
