from fastapi import FastAPI
import threading
import os
import uvicorn
import argparse
from .agent import BaseAgent
from .forecaster import Forecaster
from .orchestrator import Orchestrator
from .utils import AgentType

app = FastAPI(title="AegisScale")


def create_app():
    forecaster = Forecaster(retrain=False)
    agents = [
        BaseAgent("cpu", AgentType.CPU, forecaster),
        BaseAgent("gpu", AgentType.GPU, forecaster),
        BaseAgent("storage", AgentType.STORAGE, forecaster),
    ]
    orch = Orchestrator(
        agents,
        namespace=os.environ.get("NAMESPACE", "default"),
        dry_run=os.environ.get("DRY_RUN", "1") == "1",
    )
    import aegisscale.api as api_mod

    api_mod.ORCH = orch
    app.include_router(api_mod.router, prefix="/api")
    if os.environ.get("RUN_LOOP", "1") == "1":
        t = threading.Thread(
            target=orch.run_loop,
            kwargs={"interval_sec": int(os.environ.get("LOOP_INTERVAL", "30"))},
            daemon=True,
        )
        t.start()
    return app


app = create_app()

def cli():
    parser = argparse.ArgumentParser(prog="aegisscale")
    parser.add_argument("--host", default="0.0.0.0", help="Server host")
    parser.add_argument("--port", default=8000, type=int, help="Server port")
    parser.add_argument("--namespace", default=os.environ.get("NAMESPACE", "default"), help="K8s namespace")
    parser.add_argument("--dry-run", action="store_true", help="Enable dry-run mode")
    parser.add_argument("--no-loop", action="store_true", help="Disable orchestrator loop")
    parser.add_argument("--loop-interval", default=int(os.environ.get("LOOP_INTERVAL", "30")), type=int, help="Loop interval seconds")
    args = parser.parse_args()
    os.environ["NAMESPACE"] = args.namespace
    os.environ["DRY_RUN"] = "1" if args.dry_run else "0"
    os.environ["RUN_LOOP"] = "0" if args.no_loop else "1"
    os.environ["LOOP_INTERVAL"] = str(args.loop_interval)
    uvicorn.run("aegisscale.main:app", host=args.host, port=args.port)

if __name__ == "__main__":
    cli()
