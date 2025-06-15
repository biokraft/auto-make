#!/usr/bin/env python3
"""Test script to verify streaming behavior."""

import sys
import time

print("Starting streaming test...")
sys.stdout.flush()

for i in range(5):
    print(f"Line {i + 1}: Processing...")
    sys.stdout.flush()
    time.sleep(1)

print("Streaming test completed!")
sys.stdout.flush()
