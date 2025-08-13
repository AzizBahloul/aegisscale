from fastapi import APIRouter
from .orchestrator import Orchestrator

router = APIRouter()
ORCH: Orchestrator = None


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get("/agents")
async def list_agents():
    return {"agents": list(ORCH.agents.keys())}


@router.post("/simulate/{agent_name}")
async def simulate_load(agent_name: str, load: float):
    agent = ORCH.agents.get(agent_name)
    if not agent:
        return {"error": "agent not found"}
    agent.observe(load)
    return {"msg": "observed"}


@router.post("/step")
async def step():
    proposals, allocations = ORCH.loop_once()
    return {
        "proposals": {k: v._asdict() for k, v in proposals.items()},
        "allocations": {k: v._asdict() for k, v in allocations.items()},
    }


@router.get("/status")
async def status():
    return {
        "agents_last_requests": {
            k: v.last_request._asdict() for k, v in ORCH.agents.items()
        }
    }
