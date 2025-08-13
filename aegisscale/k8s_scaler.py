from kubernetes import client, config
import os


def load_kube_config():
    try:
        config.load_incluster_config()
    except Exception:
        kube_path = os.environ.get("KUBECONFIG")
        if kube_path and os.path.exists(kube_path):
            config.load_kube_config(kube_config=kube_path)
        else:
            config.load_kube_config()



class K8sScaler:
    def __init__(self, namespace="default"):
        load_kube_config()
        self.apps = client.AppsV1Api()
        self.namespace = namespace

    def set_replicas(self, deployment_name: str, replicas: int):
        replicas = max(int(replicas), 0)
        body = {"spec": {"replicas": replicas}}
        return self.apps.patch_namespaced_deployment_scale(
            deployment_name, self.namespace, body
        )

    def patch_resources(
        self, deployment_name: str, container_name: str, cpu: str, memory: str
    ):
        patch = {
            "spec": {
                "template": {
                    "spec": {
                        "containers": [
                            {
                                "name": container_name,
                                "resources": {
                                    "requests": {"cpu": cpu, "memory": memory},
                                    "limits": {"cpu": cpu, "memory": memory},
                                },
                            }
                        ]
                    }
                }
            }
        }
        return self.apps.patch_namespaced_deployment(
            deployment_name, self.namespace, patch
        )

    def get_deployment_replicas(self, deployment_name):
        dep = self.apps.read_namespaced_deployment(deployment_name, self.namespace)
        return dep.spec.replicas


# Mock scaler for dry run mode
class MockK8sScaler:
    def __init__(self, namespace="default"):
        self.namespace = namespace

    def set_replicas(self, deployment_name: str, replicas: int):
        pass

    def patch_resources(self, deployment_name: str, container_name: str, cpu: str, memory: str):
        pass

    def get_deployment_replicas(self, deployment_name):
        return 1
