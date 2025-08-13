import requests
import time
import random

BASE = "http://localhost:8000/api"


def push_load(agent_name, load):
    return requests.post(f"{BASE}/simulate/{agent_name}", params={"load": load}).json()


if __name__ == "__main__":
    agents = ["cpu", "gpu", "storage"]
    for _ in range(30):
        name = random.choice(agents)
        load = random.random() * 500
        print("pushing", name, load, push_load(name, load))
        time.sleep(2)
