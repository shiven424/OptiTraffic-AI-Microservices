#!/bin/bash

echo "Starting simulator.py..."
python3 simulator.py &  # Run in background

sleep 5

echo "Running cityflow_runner.py once..."
python3 cityflow_runner.py

wait