import time
import threading
import queue
import json
import random
import os

# MQTT Client Simulation (With fallback for missing package)
try:
    import paho.mqtt.client as mqtt
    HAS_MQTT = True
except ImportError:
    HAS_MQTT = False

# =================================================================
# Course: Data Engineering (CSIE, Tamkang University)
# Lab 14: Heterogeneous Fusion & MQTT Strategy (Final Version)
# =================================================================

# Thread-safe queues for data buffering
sensor_queue = queue.Queue(maxsize=50)
vision_queue = queue.Queue(maxsize=1)
stop_event = threading.Event()

def sensor_producer():
    """Producer A: Simulates an Ultrasonic Water Level Sensor (20Hz)."""
    print("[Sensor Thread] Started (20Hz).")
    while not stop_event.is_set():
        data = {
            "ts": time.time(), 
            "val": round(random.uniform(2.0, 4.0), 2)
        }
        
        # If queue is full, drop the oldest and put the newest
        try:
            sensor_queue.put_nowait(data)
        except queue.Full:
            try: sensor_queue.get_nowait()
            except queue.Empty: pass
            try: sensor_queue.put_nowait(data)
            except queue.Full: pass
            
        time.sleep(0.05)

def vision_producer():
    """Producer B: Simulates YOLOv10 Inference results (4Hz)."""
    print("[Vision Thread] Started (4Hz).")
    while not stop_event.is_set():
        data = {
            "ts": time.time(), 
            "count": random.randint(0, 10)
        }
        
        try:
            vision_queue.put_nowait(data)
        except queue.Full:
            try: vision_queue.get_nowait()
            except queue.Empty: pass
            try: vision_queue.put_nowait(data)
            except queue.Full: pass
            
        time.sleep(0.25)

def publish_data(payload):
    """Simulates MQTT Publishing with Local Fallback (Graceful Degradation)."""
    # Simulate a connection success rate of 80%
    success = False
    
    if success and HAS_MQTT:
        print(f"[CLOUD] Successfully published via MQTT QoS 1.")
    else:
        # Implementation of local cache mechanism
        print(f"[CACHE] Connection failed or missing package. Saving to local.jsonl...")
        with open("local.jsonl", "a") as f:
            f.write(json.dumps(payload) + "\n")

if __name__ == "__main__":
    # Start simulators as daemon threads
    threading.Thread(target=sensor_producer, daemon=True).start()
    threading.Thread(target=vision_producer, daemon=True).start()
    
    print("[*] Starting Fusion Pipeline...")
    try:
        while True:
            # Step 1: Latching - Use low-frequency Vision timestamp as the baseline
            vis = vision_queue.get()
            
            best_match = None
            min_diff = 1.0 # Initial threshold (1 second)
            
            # Step 2: Nearest-Neighbor Join Logic
            # Retrieve available sensor data from the buffer to find the closest match
            while not sensor_queue.empty():
                s = sensor_queue.get()
                diff = abs(vis["ts"] - s["ts"])
                if diff < min_diff:
                    min_diff = diff
                    best_match = s
            
            # Step 3: Threshold Validation (Tolerance: 100ms)
            if best_match and min_diff < 0.1:
                # Step 4: JSON Protocol Packaging
                payload = {
                    "timestamp": vis["ts"],
                    "data": {
                        "water_level_m": best_match["val"], 
                        "debris_count": vis["count"]
                    },
                    "sync_error_ms": round(min_diff * 1000, 2)
                }
                print(f"\n[FUSION] Aligned! Time Error: {payload['sync_error_ms']}ms")
                publish_data(payload)
            else:
                print(f"[!] Sync failed: Time error too large ({min_diff*1000:.2f}ms).")
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        stop_event.set()
        print("\n[*] System Shutdown initiated.")
