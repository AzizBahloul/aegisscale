import enum
from typing import NamedTuple


class ResourceRequest(NamedTuple):
    cpu: float
    memory: float
    gpu: int
    storage: float


class AgentType(str, enum.Enum):
    CPU = "cpu"
    GPU = "gpu"
    STORAGE = "storage"
