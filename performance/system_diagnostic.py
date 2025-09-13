#!/usr/bin/env python3
"""
System Diagnostic Script for Recipe App Performance Testing
Helps identify potential causes of system crashes during load testing
"""

import psutil
import os
import platform
import subprocess
import time
import threading
from concurrent.futures import ThreadPoolExecutor
import requests
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def check_system_resources():
    """Check current system resource usage"""
    print("🔍 System Resource Check")
    print("=" * 40)
    
    # CPU
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_count = psutil.cpu_count()
    print(f"CPU: {cpu_percent}% usage ({cpu_count} cores)")
    
    # Memory
    memory = psutil.virtual_memory()
    print(f"Memory: {memory.percent}% used ({memory.used // (1024**3):.1f}GB / {memory.total // (1024**3):.1f}GB)")
    
    # Disk
    disk = psutil.disk_usage('/')
    print(f"Disk: {disk.percent}% used ({disk.used // (1024**3):.1f}GB / {disk.total // (1024**3):.1f}GB)")
    
    # Network connections
    connections = len(psutil.net_connections())
    print(f"Network connections: {connections}")
    
    return {
        'cpu_percent': cpu_percent,
        'memory_percent': memory.percent,
        'disk_percent': disk.percent,
        'connections': connections
    }

def check_python_processes():
    """Check for Python processes that might be consuming resources"""
    print("\n🐍 Python Process Check")
    print("=" * 40)
    
    python_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            if 'python' in proc.info['name'].lower():
                python_processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    if python_processes:
        print(f"Found {len(python_processes)} Python processes:")
        for proc in python_processes[:10]:  # Show first 10
            print(f"  PID {proc['pid']}: {proc['name']} - CPU: {proc['cpu_percent']:.1f}%, Memory: {proc['memory_percent']:.1f}%")
    else:
        print("No Python processes found")

def check_database_connections():
    """Check if database is accessible and responsive"""
    print("\n🗄️ Database Connection Check")
    print("=" * 40)
    
    try:
        import psycopg2
        from dotenv import load_dotenv
        load_dotenv()
        
        DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/recipe_app")
        
        start_time = time.time()
        conn = psycopg2.connect(DATABASE_URL)
        connect_time = (time.time() - start_time) * 1000
        
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        
        cursor.execute("SELECT count(*) FROM recipe;")
        recipe_count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        print(f"✅ Database connection: {connect_time:.1f}ms")
        print(f"   Version: {version[0]}")
        print(f"   Recipe count: {recipe_count}")
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")

def test_backend_health():
    """Test backend health and response time"""
    print("\n🏥 Backend Health Check")
    print("=" * 40)
    
    try:
        start_time = time.time()
        response = requests.get("http://127.0.0.1:8000/health", timeout=10)
        response_time = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            print(f"✅ Backend healthy: {response_time:.1f}ms")
        else:
            print(f"⚠️ Backend responded with {response.status_code}: {response_time:.1f}ms")
            
    except Exception as e:
        print(f"❌ Backend not accessible: {e}")

def simulate_concurrent_load():
    """Simulate a small concurrent load to test system stability"""
    print("\n🚀 Concurrent Load Simulation")
    print("=" * 40)
    
    def make_request():
        try:
            start_time = time.time()
            response = requests.get("http://127.0.0.1:8000/health", timeout=5)
            response_time = (time.time() - start_time) * 1000
            return response_time
        except Exception as e:
            return f"Error: {e}"
    
    print("Testing 20 concurrent requests...")
    
    try:
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(20)]
            results = [future.result() for future in futures]
        
        successful = [r for r in results if isinstance(r, (int, float))]
        errors = [r for r in results if isinstance(r, str)]
        
        if successful:
            avg_time = sum(successful) / len(successful)
            print(f"✅ {len(successful)} successful requests, average: {avg_time:.1f}ms")
        
        if errors:
            print(f"❌ {len(errors)} failed requests")
            for error in errors[:3]:  # Show first 3 errors
                print(f"   {error}")
                
    except Exception as e:
        print(f"❌ Concurrent test failed: {e}")

def check_system_limits():
    """Check system limits that might cause crashes"""
    print("\n⚙️ System Limits Check")
    print("=" * 40)
    
    try:
        # Check file descriptor limits (Unix-like systems)
        if platform.system() != "Windows":
            result = subprocess.run(['ulimit', '-n'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"File descriptor limit: {result.stdout.strip()}")
        
        # Check memory limits
        memory = psutil.virtual_memory()
        if memory.percent > 90:
            print(f"⚠️ High memory usage: {memory.percent}%")
        else:
            print(f"✅ Memory usage OK: {memory.percent}%")
            
        # Check CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent > 80:
            print(f"⚠️ High CPU usage: {cpu_percent}%")
        else:
            print(f"✅ CPU usage OK: {cpu_percent}%")
            
    except Exception as e:
        print(f"❌ Could not check system limits: {e}")

def main():
    print("🔧 Recipe App System Diagnostic")
    print("=" * 50)
    print("This script helps identify potential causes of system crashes")
    print("during performance testing.")
    print()
    
    # Check system resources
    resources = check_system_resources()
    
    # Check Python processes
    check_python_processes()
    
    # Check database
    check_database_connections()
    
    # Check backend
    test_backend_health()
    
    # Check system limits
    check_system_limits()
    
    # Simulate small load
    simulate_concurrent_load()
    
    # Recommendations
    print("\n" + "=" * 50)
    print("💡 RECOMMENDATIONS")
    print("=" * 50)
    
    if resources['memory_percent'] > 85:
        print("⚠️ High memory usage detected!")
        print("   - Close unnecessary applications")
        print("   - Reduce concurrent test load")
        print("   - Consider increasing system RAM")
    
    if resources['cpu_percent'] > 80:
        print("⚠️ High CPU usage detected!")
        print("   - Close CPU-intensive applications")
        print("   - Reduce concurrent test load")
        print("   - Consider using fewer test threads")
    
    if resources['connections'] > 1000:
        print("⚠️ High number of network connections!")
        print("   - This might indicate connection leaks")
        print("   - Check for proper connection cleanup")
        print("   - Consider using connection pooling")
    
    print("\n🔧 Crash Prevention Tips:")
    print("1. Run tests with reduced load initially")
    print("2. Monitor system resources during testing")
    print("3. Use the enhanced performance_test.py script")
    print("4. Ensure proper error handling in test scripts")
    print("5. Consider running tests on a dedicated machine")

if __name__ == "__main__":
    main()
