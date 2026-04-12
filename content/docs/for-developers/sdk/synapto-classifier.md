# synapto-classifier

Six-pass incident classification pipeline. Classifies an incident into one of Synapto's infrastructure layers (OS & Hardware, Network, Database, Middleware, Application).

## Install

```bash
pip install -e libs/synapto-classifier
```

## Usage

```python
from synapto_classifier import ClassifierPipeline
from synapto_contracts import AnomalySignal

pipeline = ClassifierPipeline()
signal = AnomalySignal(title="Nginx 502 errors on web-01", hostname="web-01", severity="high")
classification = pipeline.classify(signal)
print(classification.layer)      # "Middleware"
print(classification.component)  # "nginx"
print(classification.confidence) # 0.87
```

## How it works

The pipeline runs six classification passes in sequence, each specialised for a different infrastructure layer. The pass with the highest confidence score wins. If no pass exceeds the confidence threshold, the incident is classified as `Unknown` and escalated to the Learning Engine for AI classification.
