from fastapi import FastAPI
import threading
import os
import uvicorn
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

if __name__ == "__main__":
    uvicorn.run("aegisscale.main:app", host="0.0.0.0", port=8000)
