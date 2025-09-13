#!/usr/bin/env python3
"""
Load Testing Script for Recipe App
This script helps you run Locust load tests with proper configuration.
"""

import subprocess
import sys
import os
import time

def run_load_test(users=50, spawn_rate=10, run_time="5m"):
    """Run the load test with recommended settings"""
    
    print("🍳 Recipe App Load Testing")
    print("=" * 50)
    
    # Configuration
    host = "http://127.0.0.1:8000"  # Using IP to avoid DNS resolution delays
    
    print(f"Target Host: {host}")
    print(f"Number of Users: {users}")
    print(f"Spawn Rate: {spawn_rate} users/second")
    print(f"Test Duration: {run_time}")
    print()
    
    # Check if backend is running
    print("Checking if backend is running...")
    try:
        import requests
        response = requests.get(f"{host}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running and healthy!")
        else:
            print("⚠️  Backend responded but health check failed")
    except Exception as e:
        print(f"❌ Backend is not running or not accessible: {e}")
        print("Please start your FastAPI backend first:")
        print("cd backend && uvicorn backend.Apis.main:app --reload --host 0.0.0.0 --port 8000")
        return
    
    print()
    print("Starting load test...")
    print("Press Ctrl+C to stop the test early")
    print()
    
    # Run locust
    try:
        cmd = [
            "locust",
            "--host", host,
            "--users", str(users),
            "--spawn-rate", str(spawn_rate),
            "--run-time", run_time,
            "--headless",  # Run without web UI
            "--html", "load_test_report.html",  # Generate HTML report
            "--csv", "load_test_results"  # Generate CSV data
        ]
        
        subprocess.run(cmd, check=True)
        
        print()
        print("✅ Load test completed successfully!")
        print("📊 Check the generated reports:")
        print("   - HTML Report: load_test_report.html")
        print("   - CSV Data: load_test_results.csv")
        
    except KeyboardInterrupt:
        print("\n⏹️  Load test stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Load test failed: {e}")
    except FileNotFoundError:
        print("❌ Locust is not installed. Please install it first:")
        print("pip install locust")

def run_interactive_test():
    """Run locust in interactive mode with web UI"""
    
    print("🍳 Recipe App Load Testing - Interactive Mode")
    print("=" * 50)
    print("This will start Locust's web interface where you can configure and run tests manually.")
    print()
    
    host = "http://127.0.0.1:8000"  # Using IP to avoid DNS resolution delays
    
    # Check if backend is running
    print("Checking if backend is running...")
    try:
        import requests
        response = requests.get(f"{host}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running and healthy!")
        else:
            print("⚠️  Backend responded but health check failed")
    except Exception as e:
        print(f"❌ Backend is not running or not accessible: {e}")
        print("Please start your FastAPI backend first:")
        print("cd backend && uvicorn backend.Apis.main:app --reload --host 0.0.0.0 --port 8000")
        return
    
    print()
    print("Starting Locust web interface...")
    print("Open your browser to: http://localhost:8089")
    print("Press Ctrl+C to stop")
    print()
    
    try:
        cmd = ["locust", "--host", host]
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n⏹️  Locust stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Locust failed: {e}")
    except FileNotFoundError:
        print("❌ Locust is not installed. Please install it first:")
        print("pip install locust")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Recipe App Load Testing')
    parser.add_argument('--users', type=int, default=50, help='Number of concurrent users (max 1000)')
    parser.add_argument('--spawn-rate', type=int, default=10, help='Users spawned per second')
    parser.add_argument('--run-time', type=str, default='5m', help='Test duration (e.g., 5m, 10m, 1h)')
    parser.add_argument('--interactive', action='store_true', help='Run with web UI')
    parser.add_argument('--help', action='store_true', help='Show detailed help')
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "interactive":
            run_interactive_test()
        elif sys.argv[1] == "help":
            print("Recipe App Load Testing")
            print("=" * 30)
            print("Usage:")
            print("  python run_load_test.py                    # Run automated 5-minute test")
            print("  python run_load_test.py --users 1000       # Test with 1000 users")
            print("  python run_load_test.py --users 500 --run-time 10m  # Custom test")
            print("  python run_load_test.py interactive        # Run with web UI")
            print("  python run_load_test.py help               # Show this help")
            print()
            print("Scaling Recommendations:")
            print("  - 100 users: Basic load test")
            print("  - 500 users: Medium scaling test")
            print("  - 1000 users: High scaling test (requires optimizations)")
            print()
            print("Prerequisites:")
            print("  1. Install Locust: pip install locust")
            print("  2. Start your FastAPI backend")
            print("  3. Ensure your database is running")
            print("  4. For 1000+ users: Install Redis and configure PgBouncer")
        else:
            # Parse arguments
            args = parser.parse_args()
            
            # Validate user count
            if args.users > 1000:
                print("⚠️  Warning: Testing with more than 1000 users requires:")
                print("   - Redis caching layer")
                print("   - PgBouncer connection pooling")
                print("   - PostgreSQL server optimizations")
                print("   - Multiple application instances")
                response = input("Continue anyway? (y/N): ")
                if response.lower() != 'y':
                    return
            
            run_load_test(args.users, args.spawn_rate, args.run_time)
    else:
        run_load_test()

if __name__ == "__main__":
    main()
