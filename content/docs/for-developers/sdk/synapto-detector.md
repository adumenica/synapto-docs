# synapto-detector

Statistical anomaly detection engine. Analyses time-series metrics to detect anomalies before they become incidents.

## Install

```bash
pip install -e libs/synapto-detector
```

## Usage

```python
from synapto_detector import DetectionEngine
from synapto_contracts import AnomalySignal

engine = DetectionEngine()
# Pass a list of recent metric values (e.g. CPU %)
anomalies = engine.detect(metric_name="cpu_usage", values=[45, 47, 50, 52, 91, 93])
for signal in anomalies:
    print(signal.title)     # "CPU usage anomaly detected"
    print(signal.severity)  # "high"
```

The detector uses Z-score analysis by default. Values more than 3 standard deviations from the rolling mean trigger an `AnomalySignal`.
