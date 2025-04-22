# Example results for ESP32-S3 with 8MB SPIRAM:
# Test Summary:
# Busy loop: 153018.20 iterations/second
# Busy loop with yield: 40303.37 iterations/second
# SHA-256 (1KB): 7357.60 iterations/second

import time
import hashlib
import os

# Configuration
TEST_DURATION = 5  # Duration of each test in seconds
DATA_SIZE = 1024   # 1KB of data for SHA-256 test
DATA = os.urandom(DATA_SIZE)  # Generate 1KB of random data for SHA-256

def stress_test_busy_loop():
    print("\nStarting busy loop stress test...")
    iterations = 0
    start_time = time.ticks_ms()
    end_time = start_time + (TEST_DURATION * 1000)
    
    while time.ticks_ms() < end_time:
        iterations += 1
    
    duration_ms = time.ticks_diff(time.ticks_ms(), start_time)
    iterations_per_second = (iterations / duration_ms) * 1000
    print(f"Busy loop test completed: {iterations_per_second:.2f} iterations/second")
    return iterations_per_second

def stress_test_busy_loop_with_yield():
    print("\nStarting busy loop with yield (sleep_ms(0)) stress test...")
    iterations = 0
    start_time = time.ticks_ms()
    end_time = start_time + (TEST_DURATION * 1000)
    
    while time.ticks_ms() < end_time:
        iterations += 1
        time.sleep_ms(0)  # Yield to other tasks
    
    duration_ms = time.ticks_diff(time.ticks_ms(), start_time)
    iterations_per_second = (iterations / duration_ms) * 1000
    print(f"Busy loop with yield test completed: {iterations_per_second:.2f} iterations/second")
    return iterations_per_second

def stress_test_sha256():
    print("\nStarting SHA-256 stress test (1KB data)...")
    iterations = 0
    start_time = time.ticks_ms()
    end_time = start_time + (TEST_DURATION * 1000)
    
    while time.ticks_ms() < end_time:
        hashlib.sha256(DATA).digest()  # Compute SHA-256 on 1KB data
        iterations += 1
    
    duration_ms = time.ticks_diff(time.ticks_ms(), start_time)
    iterations_per_second = (iterations / duration_ms) * 1000
    print(f"SHA-256 test completed: {iterations_per_second:.2f} iterations/second")
    return iterations_per_second

def main():
    print("Starting CPU stress tests...")
    
    # Run busy loop test
    busy_loop_ips = stress_test_busy_loop()
    
    # Small delay to stabilize system
    time.sleep_ms(500)
    
    # Run busy loop with yield test
    yield_loop_ips = stress_test_busy_loop_with_yield()
    
    # Small delay to stabilize system
    time.sleep_ms(500)
    
    # Run SHA-256 test
    sha256_ips = stress_test_sha256()
    
    # Summary
    print("\nTest Summary:")
    print(f"Busy loop: {busy_loop_ips:.2f} iterations/second")
    print(f"Busy loop with yield: {yield_loop_ips:.2f} iterations/second")
    print(f"SHA-256 (1KB): {sha256_ips:.2f} iterations/second")
    print("All tests completed.")

try:
    main()
except Exception as e:
    print(f"Error during tests: {e}")

