from dataclasses import dataclass

@dataclass
class Metrics:
    latency_ms: float   # average token latency in milliseconds
    calls_per_min: float
    errors: int

@dataclass
class MCPServer:
    name: str
    endpoint: str
