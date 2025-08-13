from prometheus_client import start_http_server, Gauge
import logging

logger = logging.getLogger("aegisscale.metrics_exporter")

AGENT_CPU_REQ = Gauge(
    "aegisscale_agent_cpu_request_cores", "Requested CPU cores by agent", ["agent"]
)
AGENT_MEM_REQ = Gauge(
    "aegisscale_agent_memory_request_mib", "Requested Memory MiB by agent", ["agent"]
)
AGENT_GPU_REQ = Gauge(
    "aegisscale_agent_gpu_request", "Requested GPUs by agent", ["agent"]
)
AGENT_STORAGE_REQ = Gauge(
    "aegisscale_agent_storage_request_gib", "Requested Storage GiB by agent", ["agent"]
)


class MetricsExporter:
    def __init__(self, port=8001):
        try:
            start_http_server(port)
        except OSError as e:
            logger.warning(f"Could not start metrics HTTP server on port {port}: {e}")

    def export_agent_request(self, agent_name: str, req: dict):
        AGENT_CPU_REQ.labels(agent=agent_name).set(req.get("cpu", 0.0))
        AGENT_MEM_REQ.labels(agent=agent_name).set(req.get("memory", 0))
        AGENT_GPU_REQ.labels(agent=agent_name).set(req.get("gpu", 0))
        AGENT_STORAGE_REQ.labels(agent=agent_name).set(req.get("storage", 0.0))
