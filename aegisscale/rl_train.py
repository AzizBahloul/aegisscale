import ray
from ray import tune
from ray.rllib.env.multi_agent_env import MultiAgentEnv
import numpy as np
import gym           # type: ignore
from gym import spaces  # type: ignore


class SimpleNegotiationEnv(MultiAgentEnv):
    def __init__(self, num_agents=3):
        self.num_agents = num_agents
        self.agents = [f"agent_{i}" for i in range(num_agents)]
        self.observation_space = spaces.Box(
            low=0.0, high=1e6, shape=(12,), dtype=np.float32
        )
        self.action_space = spaces.Box(low=0.0, high=8.0, shape=(1,), dtype=np.float32)

    def reset(self):
        return {a: np.zeros(12, dtype=np.float32) for a in self.agents}

    def step(self, action_dict):
        obs, rew, done, info = {}, {}, {}, {}
        for a, action in action_dict.items():
            req = float(action[0])
            desired = 1.5
            r = -abs(desired - req)
            obs[a] = np.zeros(12, dtype=np.float32)
            rew[a] = r
            done[a] = False
            info[a] = {}
        done["__all__"] = False
        return obs, rew, done, info


def train_local():
    ray.init(ignore_reinit_error=True, include_dashboard=False)
    tune.run(
        "PPO",
        stop={"training_iteration": 5},
        config={
            "env": SimpleNegotiationEnv,
            "env_config": {"num_agents": 3},
            "multiagent": {
                "policies": {
                    f"policy_{i}": (
                        None,
                        gym.spaces.Box(0.0, 1.0, (12,)),
                        gym.spaces.Box(0.0, 8.0, (1,)),
                        {},
                    )
                    for i in range(3)
                },
                "policy_mapping_fn": lambda aid: f"policy_{int(aid.split('_')[-1])}",
            },
            "framework": "torch",
            "num_workers": 0,
        },
    )


if __name__ == "__main__":
    train_local()
