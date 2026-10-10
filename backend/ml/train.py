import pandas as pd
import lightgbm as lgb
import joblib
import os

def train_models():
    data_path = "backend/ml/synthetic_delay_data.csv"
    if not os.path.exists(data_path):
        print("Data not found. Run generate_data.py first.")
        return
        
    df = pd.read_csv(data_path)
    
    features = [
        "route_id", "stop_index", "hour_of_day", "day_of_week", 
        "is_peak", "rain_mm", "congestion_index", "event_flag", 
        "previous_stop_delay_min"
    ]
    target = "delay_min"
    
    X = df[features]
    y = df[target]
    
    # Train Quantile LightGBM models
    quantiles = [0.10, 0.50, 0.90]
    
    for alpha in quantiles:
        print(f"Training quantile {alpha}...")
        model = lgb.LGBMRegressor(
            objective='quantile',
            alpha=alpha,
            metric='quantile',
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            verbose=-1
        )
        model.fit(X, y)
        
        model_path = f"backend/ml/delay_model_p{int(alpha*100)}.joblib"
        joblib.dump(model, model_path)
        print(f"Saved model to {model_path}")
        
if __name__ == "__main__":
    train_models()
