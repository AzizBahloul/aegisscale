# AegisScale — Multi-Agent Cloud Auto-Scaler (MVP)

AegisScale is an advanced MVP for proactive resource negotiation and scaling in Kubernetes clusters. Agents forecast loads and negotiate allocations; the orchestrator applies changes to k8s.

## Features (MVP)
- Rule-based multi-agent negotiation (CPU/GPU/Storage agents)
- Lightweight forecaster (RandomForest window model)
- Kubernetes scaler integration (patch replicas & resources)
- Prometheus metrics exporter
- FastAPI control endpoints & background orchestrator loop
- Ray RLlib multi-agent training stub (extendable)

## Getting started (local with docker-compose)
1. Build + run:
   ```bash
   docker-compose build
   docker-compose up
   ```
2. Open API: [http://localhost:8000/api/health](http://localhost:8000/api/health)

## Running against minikube
* Start minikube and set `KUBECONFIG` env or mount it into container.
* Deploy `deploy/k8s-deployment.yaml` and `deploy/k8s-service.yaml`.
* Use `DRY_RUN=0` to allow orchestrator to call k8s.

## Extending
* Replace forecaster with LSTM/Prophet for stronger forecasts.
* Replace rule-based negotiation with RL model (`rl_train.py`).
* Add security (RBAC) and auth for APIs.
* Add Grafana dashboards.

## Files to inspect
* `aegisscale/orchestrator.py` — core negotiation + enactment  
* `aegisscale/agent.py` — agent logic  
* `aegisscale/k8s_scaler.py` — k8s API wrapper  
* `aegisscale/forecaster.py` — forecasting model  

## Notes
* Default `DRY_RUN=1` so it won't scale your cluster unless you set `DRY_RUN=0`.
* RL code is a stub; training requires a realistic simulator.