#!/usr/bin/env python3
"""
Network vs Server Performance Test
"""

import requests
import time
import statistics
import socket
import subprocess
import platform
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def test_local_connection():
    """Test if we can connect to localhost directly"""
    print("🔍 Testing localhost connection...")
    
    try:
        # Test socket connection
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('localhost', 8000))
        sock.close()
        
        if result == 0:
            print("✅ Socket connection to localhost:8000 successful")
            return True
        else:
            print(f"❌ Socket connection failed with error code: {result}")
            return False
    except Exception as e:
        print(f"❌ Socket connection error: {e}")
        return False

def test_ping():
    """Test ping to localhost"""
    print("\n🏓 Testing ping to localhost...")
    
    try:
        if platform.system().lower() == "windows":
            result = subprocess.run(['ping', '-n', '4', 'localhost'], 
                                  capture_output=True, text=True, timeout=10)
        else:
            result = subprocess.run(['ping', '-c', '4', 'localhost'], 
                                  capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Ping to localhost successful")
            print(f"Output: {result.stdout}")
        else:
            print(f"❌ Ping failed: {result.stderr}")
    except Exception as e:
        print(f"❌ Ping error: {e}")

def test_requests_session():
    """Test with requests session (connection pooling)"""
    print("\n🔗 Testing with requests session (connection pooling)...")
    
    session = requests.Session()
    
    # First request (establish connection)
    start_time = time.time()
    response = session.get("http://localhost:8000/health")
    first_request_time = (time.time() - start_time) * 1000
    
    print(f"First request (connection setup): {first_request_time:.1f}ms")
    
    # Subsequent requests (reuse connection)
    times = []
    for i in range(10):
        start_time = time.time()
        response = session.get("http://localhost:8000/health")
        request_time = (time.time() - start_time) * 1000
        times.append(request_time)
        
        if response.status_code == 200:
            print(f"Request {i+1}: {request_time:.1f}ms")
        else:
            print(f"Request {i+1}: {response.status_code} - {request_time:.1f}ms")
    
    if times:
        avg_time = statistics.mean(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"\n📊 Session performance:")
        print(f"   Average: {avg_time:.1f}ms")
        print(f"   Min: {min_time:.1f}ms")
        print(f"   Max: {max_time:.1f}ms")
        print(f"   Improvement over first request: {((first_request_time - avg_time) / first_request_time * 100):.1f}%")

def test_different_hosts():
    """Test different ways to connect to localhost"""
    print("\n🌐 Testing different localhost connections...")
    
    hosts = [
        "localhost",
        "127.0.0.1", 
        "::1",  # IPv6 localhost
        "0.0.0.0"
    ]
    
    for host in hosts:
        try:
            start_time = time.time()
            response = requests.get(f"http://{host}:8000/health", timeout=10)
            request_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                print(f"✅ {host}: {request_time:.1f}ms")
            else:
                print(f"❌ {host}: {response.status_code} - {request_time:.1f}ms")
        except Exception as e:
            print(f"❌ {host}: Error - {e}")

def test_connection_pooling():
    """Test connection pooling vs individual connections"""
    print("\n🔄 Testing connection pooling...")
    
    # Individual connections (like Locust)
    print("Testing individual connections (like Locust):")
    individual_times = []
    for i in range(5):
        start_time = time.time()
        response = requests.get("http://localhost:8000/health")
        request_time = (time.time() - start_time) * 1000
        individual_times.append(request_time)
        print(f"  Individual {i+1}: {request_time:.1f}ms")
    
    # Connection pooling
    print("\nTesting connection pooling:")
    session = requests.Session()
    pooled_times = []
    for i in range(5):
        start_time = time.time()
        response = session.get("http://localhost:8000/health")
        request_time = (time.time() - start_time) * 1000
        pooled_times.append(request_time)
        print(f"  Pooled {i+1}: {request_time:.1f}ms")
    
    if individual_times and pooled_times:
        individual_avg = statistics.mean(individual_times)
        pooled_avg = statistics.mean(pooled_times)
        
        print(f"\n📊 Connection pooling comparison:")
        print(f"   Individual connections: {individual_avg:.1f}ms average")
        print(f"   Connection pooling: {pooled_avg:.1f}ms average")
        print(f"   Improvement: {((individual_avg - pooled_avg) / individual_avg * 100):.1f}%")

def main():
    print("🌐 Network Performance Analysis")
    print("=" * 50)
    
    # Test basic connectivity
    if not test_local_connection():
        print("❌ Cannot connect to localhost:8000")
        return
    
    # Test ping
    test_ping()
    
    # Test different hosts
    test_different_hosts()
    
    # Test connection pooling
    test_connection_pooling()
    
    # Test session performance
    test_requests_session()
    
    print("\n" + "=" * 50)
    print("💡 RECOMMENDATIONS")
    print("=" * 50)
    
    print("""
🔧 To fix the 2000ms response times:

1. **Run Locust on the same machine as the server**
   - Eliminates network latency
   - Use: locust --host=http://localhost:8000

2. **Use connection pooling in Locust**
   - Modify locustfile to use requests.Session()
   - Reuse connections between requests

3. **Check network configuration**
   - Disable firewall temporarily
   - Check for proxy settings
   - Verify DNS resolution

4. **Test with different hosts**
   - Try 127.0.0.1 instead of localhost
   - Check if IPv6 (::1) is faster

5. **Monitor actual server performance**
   - Check backend logs for actual processing time
   - Use server-side timing middleware
    """)

if __name__ == "__main__":
    main()

