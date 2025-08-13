from typing import List
import numpy as np
import pickle
import os
from sklearn.ensemble import RandomForestRegressor

MODEL_PATH = "/tmp/aegisscale_forecaster.pkl"


class Forecaster:
    def __init__(self, retrain=False):
        self.model = None
        if os.path.exists(MODEL_PATH) and not retrain:
            try:
                with open(MODEL_PATH, "rb") as f:
                    self.model = pickle.load(f)
            except Exception:
                self.model = None
        if self.model is None:
            self.model = RandomForestRegressor(n_estimators=20, random_state=42)

    def train(self, series: List[float], window=12):
        X, y = [], []
        for i in range(window, len(series)):
            X.append(series[i - window : i])
            y.append(series[i])
        if len(X) < 5:
            return False
        X, y = np.array(X), np.array(y)
        self.model.fit(X, y)
        with open(MODEL_PATH, "wb") as f:
            pickle.dump(self.model, f)
        return True

    def predict(self, recent_window: List[float], horizon=1):
        x = np.array(recent_window).reshape(1, -1)
        preds = []
        cur = x
        for _ in range(horizon):
            p = float(self.model.predict(cur)[0])
            preds.append(max(p, 0.0))
            cur = np.roll(cur, -1)
            cur[0, -1] = p
        return preds
