import pandas as pd
import numpy as np
import os

def generate_data(num_rows=50000):
    np.random.seed(42)
    
    # Features
    route_ids = np.random.choice([1, 2, 3], size=num_rows) # Red, Blue, Branch
    stop_indices = np.random.randint(1, 20, size=num_rows)
    hours = np.random.randint(6, 23, size=num_rows)
    day_of_week = np.random.randint(0, 7, size=num_rows)
    
    is_peak = ((hours >= 8) & (hours <= 11)) | ((hours >= 17) & (hours <= 20))
    is_peak = is_peak.astype(int)
    
    rain_mm = np.random.exponential(scale=2.0, size=num_rows)
    rain_mm[np.random.rand(num_rows) > 0.1] = 0 # 90% of time no rain
    
    congestion_index = np.random.uniform(0, 1, size=num_rows)
    event_flag = np.random.choice([0, 1], p=[0.95, 0.05], size=num_rows)
    
    previous_stop_delay_min = np.random.exponential(scale=2.0, size=num_rows)
    
    # Target: Delay (min)
    # base delay + propagation + rain impact + peak impact + noise
    delay = (
        0.5 + 
        0.7 * previous_stop_delay_min + # Decay from previous
        (rain_mm * np.random.uniform(0.5, 1.5, size=num_rows)) + # Rain adds 2-5 min roughly based on mm
        (is_peak * np.random.uniform(1.0, 3.0, size=num_rows)) + 
        (congestion_index * 2.0) +
        (event_flag * 5.0) + 
        np.random.normal(0, 1.0, size=num_rows)
    )
    delay = np.maximum(0, delay) # No negative delay
    
    df = pd.DataFrame({
        "route_id": route_ids,
        "stop_index": stop_indices,
        "hour_of_day": hours,
        "day_of_week": day_of_week,
        "is_peak": is_peak,
        "rain_mm": rain_mm,
        "congestion_index": congestion_index,
        "event_flag": event_flag,
        "previous_stop_delay_min": previous_stop_delay_min,
        "delay_min": delay
    })
    
    os.makedirs("backend/ml", exist_ok=True)
    df.to_csv("backend/ml/synthetic_delay_data.csv", index=False)
    print(f"Generated {num_rows} rows of synthetic data in backend/ml/synthetic_delay_data.csv")

if __name__ == "__main__":
    generate_data()
