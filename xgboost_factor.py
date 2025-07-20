import xgboost as xgb

def train_model(X, y):
    model = xgb.XGBClassifier()
    return model.fit(X, y)
