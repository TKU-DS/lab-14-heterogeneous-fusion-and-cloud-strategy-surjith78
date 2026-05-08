# Lab 14: Heterogeneous Fusion & Cloud Strategy

## 📌 Overview
This is the "Last Mile" of our Edge AI Pipeline. In this lab, you will integrate high-frequency scalar sensor data (Water Level) with low-frequency tensor results (YOLO Detection) within the GitHub Codespaces environment.

## 🎯 Learning Objectives
1. Implement **Nearest-Neighbor Join** to synchronize asynchronous data streams.
2. Package fused data into a structured **JSON Metadata** payload.
3. Simulate **Edge-to-Cloud** transmission using MQTT with a local fallback mechanism.

## 🛠️ Setup
Install the necessary packages for Codespaces:
```bash
pip install paho-mqtt ultralytics numpy opencv-python-headless
```

## 🚀 Lab Tasks
1. **Fusion Logic**: Align sensor timestamps with vision timestamps (Tolerance < 100ms).
2. **Protocol Engineering**: Pack the fused results into the specified JSON format.
3. **Cloud Exfiltration**: Publish the payload to the local broker. If connection fails, save to `local.jsonl`.

## ✅ Expected Deliverable
- A GitHub repository containing the functional pipeline.
- Screenshot of the Terminal showing successful fusion logs.
- The `local.jsonl` file content showing at least 5 cached records.
