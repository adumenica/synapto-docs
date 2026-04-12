# Contracts

Synapto uses two mechanisms to enforce interfaces between components: Pydantic schemas (Python services) and Protocol Buffers (gRPC/Agent Service).

## synapto-contracts

`libs/synapto-contracts` defines the shared Pydantic models used by all AIOps libraries and services. Any type that crosses a library boundary lives here.

Key types:

| Type | Used by | Purpose |
|------|---------|---------|
| `AnomalySignal` | synapto-detector, orchestration-layer | Represents a detected anomaly |
| `IncidentClassification` | synapto-classifier | Classification result with layer, component, confidence |
| `RemediationSafety` | synapto-remediator | Safety gate result |
| `Workflow` / `WorkflowResult` | synapto-remediator, orchestration-layer | Remediation workflow input/output |
| `TelemetrySignal` | synapto-telemetry | Metric/log envelope published to Redis |

## Protocol Buffers (Agent Service)

The Agent Service uses gRPC defined in `backend/proto/`. The `.proto` files define the `AgentBridge` service:

```protobuf
service AgentBridge {
  rpc Connect(stream AgentMessage) returns (stream JobPayload);
}
```

After modifying a `.proto` file, regenerate the Python stubs:

```bash
python -m grpc_tools.protoc \
  -I backend/proto \
  --python_out=backend/agent-service \
  --grpc_python_out=backend/agent-service \
  backend/proto/agent.proto
```

## Contract verification

`verify_contracts.py` at the repo root runs a suite of structural checks to catch schema drift:

```bash
python verify_contracts.py
```

This checks that:
- All `synapto-contracts` types can be imported without errors
- All SDK libraries accept the contract types without type errors
- The gRPC proto stubs match the current `.proto` definitions

Run this before any PR that modifies a shared schema.
