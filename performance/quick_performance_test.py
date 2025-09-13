#!/usr/bin/env python3
"""
Quick Performance Test to identify response time issues
"""

import requests
import time
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import statistics

def test_endpoint(url, name, iterations=5):
    """Test a single endpoint"""
    print(f"\n🔍 Testing {name} ({url})")
    
    times = []
    for i in range(iterations):
        try:
            start_time = time.time()
            response = requests.get(url, timeout=30)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                times.append(response_time)
                print(f"  Request {i+1}: {response_time:.1f}ms")
            else:
                print(f"  Request {i+1}: {response.status_code} - {response_time:.1f}ms")
                
        except Exception as e:
            print(f"  Request {i+1}: Error - {e}")
        
        time.sleep(0.5)  # Small delay between requests
    
    if times:
        avg_time = statistics.mean(times)
        median_time = statistics.median(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"  📊 Results: Avg={avg_time:.1f}ms, Median={median_time:.1f}ms, Min={min_time:.1f}ms, Max={max_time:.1f}ms")
        
        if avg_time > 1000:
            print(f"  ⚠️ SLOW: {name} is taking {avg_time:.1f}ms average")
        else:
            print(f"  ✅ FAST: {name} is performing well")
            
        return avg_time
    else:
        print(f"  ❌ All requests failed for {name}")
        return None

def main():
    print("🚀 Quick Performance Test")
    print("=" * 50)
    
    # Test endpoints
    endpoints = [
        ("http://127.0.0.1:8000/health", "Health Check"),
        ("http://localhost:8000/health", "Health Check (localhost)"),
    ]
    
    results = {}
    
    for url, name in endpoints:
        avg_time = test_endpoint(url, name)
        results[name] = avg_time
    
    print("\n" + "=" * 50)
    print("ANALYSIS")
    print("=" * 50)
    
    if results.get("Health Check") and results.get("Health Check (localhost)"):
        localhost_time = results["Health Check (localhost)"]
        ip_time = results["Health Check"]
        
        if localhost_time > ip_time * 10:
            print(f"⚠️ DNS Resolution Issue Detected!")
            print(f"   localhost: {localhost_time:.1f}ms")
            print(f"   127.0.0.1: {ip_time:.1f}ms")
            print(f"   Difference: {localhost_time/ip_time:.1f}x slower")
            print("\n💡 SOLUTION: Use 127.0.0.1 instead of localhost in your tests")
        else:
            print("✅ No DNS resolution issue detected")
    
    print("\n🔧 Next Steps:")
    print("1. If localhost is slow, update your test scripts to use 127.0.0.1")
    print("2. Restart your backend server to ensure optimizations are loaded")
    print("3. Check if you're running tests against the correct server")

if __name__ == "__main__":
    main()
