import math
import logging
import time
from typing import List, Dict
from .agent import BaseAgent
from .k8s_scaler import K8sScaler
from .metrics_exporter import MetricsExporter
from .utils import ResourceRequest

logger = logging.getLogger("aegisscale.orch")
logging.basicConfig(level=logging.INFO)


class Orchestrator:
    def __init__(self, agents: List[BaseAgent], namespace="default", dry_run=False):
        self.agents = {a.name: a for a in agents}
        if dry_run:
            from .k8s_scaler import MockK8sScaler
            self.k8s = MockK8sScaler(namespace=namespace)
        else:
            self.k8s = K8sScaler(namespace=namespace)
        self.metrics = MetricsExporter(port=9001)
        self.dry_run = dry_run
        self.budget = {"cpu": 32.0, "memory": 32 * 1024, "gpu": 4, "storage": 2000.0}

    def collect_proposals(self) -> Dict[str, ResourceRequest]:
        proposals = {}
        for name, agent in self.agents.items():
            req = agent.propose()
            proposals[name] = req
            self.metrics.export_agent_request(name, req._asdict())
        return proposals

    def negotiate(
        self, proposals: Dict[str, ResourceRequest]
    ) -> Dict[str, ResourceRequest]:
        scores = {
            n: max(
                r.cpu * 100 + (r.memory / 1024) * 10 + r.gpu * 500 + r.storage * 1, 1.0
            )
            for n, r in proposals.items()
        }
        total = sum(scores.values()) or 1.0
        return {
            n: ResourceRequest(
                cpu=round(self.budget["cpu"] * scores[n] / total, 3),
                memory=int(self.budget["memory"] * scores[n] / total),
                gpu=int(round(self.budget["gpu"] * scores[n] / total)),
                storage=round(self.budget["storage"] * scores[n] / total, 2),
            )
            for n in proposals
        }

    def enact(self, allocations: Dict[str, ResourceRequest]):
        cpu_per_replica = 0.5
        for name, alloc in allocations.items():
            dep = f"{name}-deployment"
            cont = name
            replicas = int(math.ceil(alloc.cpu / cpu_per_replica))
            try:
                if self.dry_run:
                    logger.info(
                        f"[dry_run] would scale {dep} -> {replicas}, cpu={alloc.cpu}"
                    )
                else:
                    logger.info(f"Scaling {dep} -> replicas={replicas}")
                    self.k8s.set_replicas(dep, replicas)
                    self.k8s.patch_resources(
                        dep, cont, f"{int(alloc.cpu * 1000)}m", f"{alloc.memory}Mi"
                    )
            except Exception as e:
                logger.exception(f"Failed to enact {name}: {e}")

    def loop_once(self):
        p = self.collect_proposals()
        a = self.negotiate(p)
        self.enact(a)
        return p, a

    def run_loop(self, interval_sec=30):
        while True:
            try:
                self.loop_once()
            except Exception as e:
                logger.exception("Error in loop: %s", e)
            time.sleep(interval_sec)
