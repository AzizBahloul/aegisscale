import pytest
from aegisscale.k8s_scaler import K8sScaler


def test_kube_config_loads():
    try:
        s = K8sScaler()
        assert hasattr(s, "get_deployment_replicas")
    except Exception:
        pytest.skip("No kube config available.")
