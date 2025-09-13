#!/usr/bin/env python3
"""
Performance test script to measure endpoint response times
Enhanced with better error handling and resource management
"""

import requests
import time
import statistics
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import signal
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Global flag for graceful shutdown
shutdown_flag = False

def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully"""
    global shutdown_flag
    print("\n🛑 Shutdown signal received. Finishing current tests...")
    shutdown_flag = True

# Register signal handler
signal.signal(signal.SIGINT, signal_handler)

def safe_request(method, url, **kwargs):
    """Make a request with proper error handling"""
    try:
        if method == "GET":
            response = requests.get(url, timeout=30, **kwargs)
        elif method == "POST":
            response = requests.post(url, timeout=30, **kwargs)
        elif method == "PUT":
            response = requests.put(url, timeout=30, **kwargs)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        return response
    except requests.exceptions.Timeout:
        print(f"  ⏰ Timeout for {method} {url}")
        return None
    except requests.exceptions.ConnectionError:
        print(f"  🔌 Connection error for {method} {url}")
        return None
    except Exception as e:
        print(f"  ❌ Request error for {method} {url}: {e}")
        return None

def test_endpoint_performance(endpoint, method="GET", data=None, headers=None, iterations=10):
    """Test endpoint performance with multiple iterations"""
    times = []
    errors = 0
    
    print(f"\n🔍 Testing {method} {endpoint} ({iterations} iterations)...")
    
    for i in range(iterations):
        if shutdown_flag:
            print("  ⏹️ Test interrupted by user")
            break
            
        try:
            start_time = time.time()
            
            response = safe_request(method, f"http://127.0.0.1:8000{endpoint}", 
                                 json=data, headers=headers)
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            if response and response.status_code == 200:
                times.append(response_time)
            else:
                errors += 1
                status_code = response.status_code if response else "No response"
                print(f"  ❌ Request {i+1}: {status_code}")
                
        except Exception as e:
            errors += 1
            print(f"  ❌ Request {i+1}: Exception - {e}")
        
        # Small delay to prevent overwhelming the server
        time.sleep(0.1)
    
    if times:
        avg_time = statistics.mean(times)
        median_time = statistics.median(times)
        min_time = min(times)
        max_time = max(times)
        p95_time = statistics.quantiles(times, n=20)[18] if len(times) >= 20 else max_time
        
        print(f"  ✅ Success: {len(times)}/{iterations} requests")
        print(f"  📊 Response times (ms):")
        print(f"     Average: {avg_time:.1f}")
        print(f"     Median:  {median_time:.1f}")
        print(f"     P95:     {p95_time:.1f}")
        print(f"     Min:     {min_time:.1f}")
        print(f"     Max:     {max_time:.1f}")
        
        return {
            "endpoint": endpoint,
            "method": method,
            "success_rate": len(times) / iterations,
            "avg_time": avg_time,
            "median_time": median_time,
            "p95_time": p95_time,
            "min_time": min_time,
            "max_time": max_time,
            "errors": errors
        }
    else:
        print(f"  ❌ All requests failed")
        return None

def get_auth_token():
    """Get authentication token for testing"""
    # Create a test user with timestamp to avoid conflicts
    test_user = {
        "username": f"perfuser{int(time.time())}",
        "password": "perfpass123"
    }
    
    print("🔐 Getting authentication token...")
    
    # Register
    response = safe_request("POST", "http://127.0.0.1:8000/register", json=test_user)
    if not response or response.status_code != 200:
        print(f"⚠️ User registration failed: {response.status_code if response else 'No response'}")
        return None
    
    # Login
    response = safe_request("POST", "http://127.0.0.1:8000/login", data=test_user)
    if not response or response.status_code != 200:
        print(f"⚠️ Login failed: {response.status_code if response else 'No response'}")
        return None
    
    try:
        token_data = response.json()
        return token_data.get("access_token")
    except Exception as e:
        print(f"⚠️ Failed to parse token: {e}")
        return None

def test_concurrent_performance(endpoint, method="GET", data=None, headers=None, concurrent_users=10, requests_per_user=5):
    """Test concurrent performance with better resource management"""
    print(f"\n🚀 Testing concurrent performance: {concurrent_users} users, {requests_per_user} requests each")
    print(f"   Endpoint: {method} {endpoint}")
    
    all_times = []
    errors = 0
    
    def user_requests(user_id):
        """Single user's requests"""
        if shutdown_flag:
            return [], 0
            
        user_times = []
        user_errors = 0
        
        for i in range(requests_per_user):
            if shutdown_flag:
                break
                
            try:
                start_time = time.time()
                
                response = safe_request(method, f"http://127.0.0.1:8000{endpoint}", 
                                     json=data, headers=headers)
                
                end_time = time.time()
                response_time = (end_time - start_time) * 1000
                
                if response and response.status_code == 200:
                    user_times.append(response_time)
                else:
                    user_errors += 1
                    
            except Exception as e:
                user_errors += 1
            
            # Small delay between requests
            time.sleep(0.05)
        
        return user_times, user_errors
    
    # Run concurrent requests with limited workers
    max_workers = min(concurrent_users, 20)  # Limit concurrent threads
    
    try:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(user_requests, i) for i in range(concurrent_users)]
            
            for future in as_completed(futures):
                if shutdown_flag:
                    break
                    
                try:
                    user_times, user_errors = future.result(timeout=60)
                    all_times.extend(user_times)
                    errors += user_errors
                except Exception as e:
                    print(f"  ❌ Thread error: {e}")
                    errors += requests_per_user
                    
    except Exception as e:
        print(f"  ❌ Concurrent test error: {e}")
        return None
    
    if all_times:
        avg_time = statistics.mean(all_times)
        median_time = statistics.median(all_times)
        p95_time = statistics.quantiles(all_times, n=20)[18] if len(all_times) >= 20 else max(all_times)
        
        print(f"  ✅ Concurrent test results:")
        print(f"     Total requests: {len(all_times) + errors}")
        print(f"     Successful: {len(all_times)}")
        print(f"     Failed: {errors}")
        print(f"     Success rate: {len(all_times)/(len(all_times)+errors)*100:.1f}%")
        print(f"     Average response time: {avg_time:.1f}ms")
        print(f"     Median response time: {median_time:.1f}ms")
        print(f"     P95 response time: {p95_time:.1f}ms")
        
        return {
            "concurrent_users": concurrent_users,
            "requests_per_user": requests_per_user,
            "total_requests": len(all_times) + errors,
            "success_rate": len(all_times) / (len(all_times) + errors),
            "avg_time": avg_time,
            "median_time": median_time,
            "p95_time": p95_time
        }
    
    return None

def main():
    print("🚀 Recipe App Performance Test (Enhanced)")
    print("=" * 50)
    print("💡 This version includes better error handling and resource management")
    print("   Press Ctrl+C to stop tests gracefully")
    print()
    
    # Get auth token
    token = get_auth_token()
    if not token:
        print("❌ Failed to get authentication token")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test endpoints (reduced iterations to prevent overload)
    endpoints_to_test = [
        ("/users/me", "GET"),
        ("/users/me/preferences/options", "GET"),
        ("/user/tags", "GET"),
        ("/user/active-recipe", "GET"),
        ("/user/recipes", "GET"),
        ("/health", "GET"),
    ]
    
    results = []
    
    # Individual performance tests
    print("📊 INDIVIDUAL PERFORMANCE TESTS")
    print("=" * 50)
    
    for endpoint, method in endpoints_to_test:
        if shutdown_flag:
            break
            
        result = test_endpoint_performance(endpoint, method, headers=headers, iterations=10)
        if result:
            results.append(result)
    
    if shutdown_flag:
        print("\n⏹️ Tests stopped by user")
        return
    
    # Concurrent performance tests (reduced load)
    print("\n" + "=" * 50)
    print("CONCURRENT PERFORMANCE TESTS")
    print("=" * 50)
    
    concurrent_endpoints = [
        ("/users/me", "GET"),
        ("/user/recipes", "GET"),
        ("/health", "GET"),
    ]
    
    concurrent_results = []
    
    for endpoint, method in concurrent_endpoints:
        if shutdown_flag:
            break
            
        result = test_concurrent_performance(endpoint, method, headers=headers, 
                                           concurrent_users=10, requests_per_user=5)
        if result:
            concurrent_results.append(result)
    
    # Summary
    print("\n" + "=" * 50)
    print("PERFORMANCE SUMMARY")
    print("=" * 50)
    
    print("\n📊 Individual Endpoint Performance:")
    for result in results:
        status = "✅" if result["p95_time"] < 500 else "⚠️"
        print(f"{status} {result['method']} {result['endpoint']}:")
        print(f"   P95: {result['p95_time']:.1f}ms, Median: {result['median_time']:.1f}ms, Success: {result['success_rate']*100:.1f}%")
    
    print("\n📊 Concurrent Performance:")
    for result in concurrent_results:
        status = "✅" if result["p95_time"] < 500 else "⚠️"
        print(f"{status} {result['concurrent_users']} users, {result['requests_per_user']} requests each:")
        print(f"   P95: {result['p95_time']:.1f}ms, Median: {result['median_time']:.1f}ms, Success: {result['success_rate']*100:.1f}%")
    
    # Recommendations
    print("\n💡 Performance Recommendations:")
    slow_endpoints = [r for r in results if r["p95_time"] > 500]
    if slow_endpoints:
        print("   ⚠️ Endpoints needing optimization:")
        for endpoint in slow_endpoints:
            print(f"      - {endpoint['method']} {endpoint['endpoint']} (P95: {endpoint['p95_time']:.1f}ms)")
    else:
        print("   ✅ All endpoints are performing well (< 500ms P95)")
    
    print("\n🔧 Crash Prevention Features:")
    print("   - Limited concurrent threads (max 20)")
    print("   - Request timeouts (30s)")
    print("   - Graceful shutdown handling")
    print("   - Reduced test iterations")
    print("   - Small delays between requests")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️ Test stopped by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
