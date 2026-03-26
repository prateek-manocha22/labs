import json
import time

def monitor_stream(file_path):
    print("🚀 Starting Healthcare Agent Stream...")
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    for entry in data:
        print(f"📊 Monitoring Patient {entry['patient_id']} - Vital Check: HR {entry['heart_rate']}, O2 {entry['oxygen']}")
        # TO DO: Add anomaly detection and agentic alerts here
        time.sleep(1)

if __name__ == "__main__":
    monitor_stream("data/sample_vitals.json")
