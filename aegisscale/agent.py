from .utils import ResourceRequest, AgentType
import numpy as np


class BaseAgent:
    def __init__(self, name: str, agent_type: AgentType, forecaster=None):
        self.name = name
        self.type = agent_type
        self.forecaster = forecaster
        self.history = []
        self.last_request = ResourceRequest(cpu=0.1, memory=128, gpu=0, storage=1.0)

    def observe(self, load_metric: float):
        self.history.append(float(load_metric))
        if len(self.history) > 200:
            self.history = self.history[-200:]

    def propose(self) -> ResourceRequest:
        recent = self.history[-12:] if len(self.history) >= 12 else self.history
        forecast_val = 0.0
        try:
            if self.forecaster and len(recent) >= 3:
                forecast_val = self.forecaster.predict(recent, horizon=1)[0]
        except Exception:
            forecast_val = recent[-1] if recent else 0.0

        current = recent[-1] if recent else 0.0
        expected = 0.7 * current + 0.3 * forecast_val

        if self.type == AgentType.CPU:
            cpu = max(0.1, 0.1 + expected * 0.01)
            mem = max(128, 128 + expected * 2)
            gpu = 0
            storage = 1.0
        elif self.type == AgentType.GPU:
            cpu = max(0.2, 0.2 + expected * 0.005)
            mem = max(512, 512 + expected * 4)
            gpu = 1 if expected > 200 else 0
            storage = 5.0
        else:
            cpu = max(0.1, 0.1 + expected * 0.002)
            mem = max(128, 128 + expected * 1.0)
            gpu = 0
            storage = max(10.0, 10.0 + expected * 0.1)

        req = ResourceRequest(
            cpu=round(cpu, 3), memory=int(mem), gpu=int(gpu), storage=round(storage, 2)
        )
        self.last_request = req
        return req


class RLAgent(BaseAgent):
    def __init__(self, name, agent_type, model=None, forecaster=None):
        super().__init__(name, agent_type, forecaster)
        self.model = model

    def propose(self):
        if self.model:
            obs = self._build_obs()
            _ = self.model.predict(obs)  # removed unused variable
            return self.last_request
        return super().propose()

    def _build_obs(self):
        arr = self.history[-20:] if len(self.history) >= 1 else [0]
        return np.array(arr)
