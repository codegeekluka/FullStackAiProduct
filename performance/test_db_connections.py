#!/usr/bin/env python3
"""
Database connection pool test for Recipe App
Tests the database connection pool under high concurrent load
"""

import asyncio
import psycopg2
import time
import threading
from concurrent.futures import ThreadPoolExecutor
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from backend.database.config import DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT, DATABASE_NAME

def test_single_connection(connection_id: int) -> dict:
    """Test a single database connection"""
    start_time = time.time()
    success = False
    error = None
    
    try:
        # Connect to database
        conn = psycopg2.connect(
            host=DATABASE_HOST,
            port=DATABASE_PORT,
            database=DATABASE_NAME,
            user=DATABASE_USER,
            password=DATABASE_PASSWORD,
            connect_timeout=10
        )
        
        # Execute a simple query
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        
        if result and result[0] == 1:
            success = True
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        error = str(e)
    
    end_time = time.time()
    duration = end_time - start_time
    
    return {
        "connection_id": connection_id,
        "success": success,
        "duration": duration,
        "error": error
    }

def test_connection_pool_sync(max_connections: int = 1000, max_workers: int = 100) -> dict:
    """Test database connection pool under load using ThreadPoolExecutor"""
    print(f"🧪 Testing database connection pool with {max_connections} connections...")
    print(f"   Using {max_workers} worker threads")
    
    start_time = time.time()
    successful_connections = 0
    failed_connections = 0
    total_duration = 0
    errors = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all connection tests
        futures = []
        for i in range(max_connections):
            future = executor.submit(test_single_connection, i)
            futures.append(future)
        
        # Collect results
        for future in futures:
            try:
                result = future.result(timeout=30)
                if result["success"]:
                    successful_connections += 1
                    total_duration += result["duration"]
                else:
                    failed_connections += 1
                    if result["error"]:
                        errors.append(result["error"])
            except Exception as e:
                failed_connections += 1
                errors.append(str(e))
    
    end_time = time.time()
    total_test_time = end_time - start_time
    
    # Calculate statistics
    avg_duration = total_duration / successful_connections if successful_connections > 0 else 0
    success_rate = (successful_connections / max_connections) * 100
    
    return {
        "total_connections": max_connections,
        "successful_connections": successful_connections,
        "failed_connections": failed_connections,
        "success_rate": success_rate,
        "average_duration": avg_duration,
        "total_test_time": total_test_time,
        "connections_per_second": max_connections / total_test_time,
        "errors": errors[:10]  # Show first 10 errors
    }

async def test_connection_pool_async(max_connections: int = 1000) -> dict:
    """Test database connection pool under load using asyncio"""
    print(f"🧪 Testing database connection pool with {max_connections} async connections...")
    
    start_time = time.time()
    successful_connections = 0
    failed_connections = 0
    total_duration = 0
    errors = []
    
    # Create tasks for all connections
    tasks = []
    for i in range(max_connections):
        task = asyncio.create_task(test_single_connection_async(i))
        tasks.append(task)
    
    # Wait for all tasks to complete
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process results
    for result in results:
        if isinstance(result, dict):
            if result["success"]:
                successful_connections += 1
                total_duration += result["duration"]
            else:
                failed_connections += 1
                if result["error"]:
                    errors.append(result["error"])
        else:
            failed_connections += 1
            errors.append(str(result))
    
    end_time = time.time()
    total_test_time = end_time - start_time
    
    # Calculate statistics
    avg_duration = total_duration / successful_connections if successful_connections > 0 else 0
    success_rate = (successful_connections / max_connections) * 100
    
    return {
        "total_connections": max_connections,
        "successful_connections": successful_connections,
        "failed_connections": failed_connections,
        "success_rate": success_rate,
        "average_duration": avg_duration,
        "total_test_time": total_test_time,
        "connections_per_second": max_connections / total_test_time,
        "errors": errors[:10]  # Show first 10 errors
    }

async def test_single_connection_async(connection_id: int) -> dict:
    """Test a single database connection asynchronously"""
    start_time = time.time()
    success = False
    error = None
    
    try:
        # Use asyncio to run the blocking database operation
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, test_single_connection, connection_id)
        return result
        
    except Exception as e:
        error = str(e)
        end_time = time.time()
        duration = end_time - start_time
        
        return {
            "connection_id": connection_id,
            "success": success,
            "duration": duration,
            "error": error
        }

def test_postgresql_limits():
    """Test PostgreSQL connection limits"""
    print("🔍 Checking PostgreSQL connection limits...")
    
    try:
        conn = psycopg2.connect(
            host=DATABASE_HOST,
            port=DATABASE_PORT,
            database=DATABASE_NAME,
            user=DATABASE_USER,
            password=DATABASE_PASSWORD
        )
        
        cursor = conn.cursor()
        
        # Check max_connections
        cursor.execute("SHOW max_connections;")
        max_connections = cursor.fetchone()[0]
        print(f"   max_connections: {max_connections}")
        
        # Check current connections
        cursor.execute("SELECT count(*) FROM pg_stat_activity;")
        current_connections = cursor.fetchone()[0]
        print(f"   current connections: {current_connections}")
        
        # Check available connections
        available_connections = int(max_connections) - current_connections
        print(f"   available connections: {available_connections}")
        
        cursor.close()
        conn.close()
        
        return {
            "max_connections": int(max_connections),
            "current_connections": current_connections,
            "available_connections": available_connections
        }
        
    except Exception as e:
        print(f"   Error checking PostgreSQL limits: {e}")
        return None

def print_results(results: dict, test_type: str):
    """Print test results in a formatted way"""
    print(f"\n📊 {test_type} Test Results:")
    print("=" * 50)
    print(f"Total Connections: {results['total_connections']}")
    print(f"Successful: {results['successful_connections']}")
    print(f"Failed: {results['failed_connections']}")
    print(f"Success Rate: {results['success_rate']:.2f}%")
    print(f"Average Duration: {results['average_duration']:.3f}s")
    print(f"Total Test Time: {results['total_test_time']:.2f}s")
    print(f"Connections/Second: {results['connections_per_second']:.2f}")
    
    if results['errors']:
        print(f"\n❌ First 10 Errors:")
        for i, error in enumerate(results['errors'], 1):
            print(f"   {i}. {error}")

def main():
    """Main test function"""
    print("🚀 Database Connection Pool Test for Recipe App")
    print("=" * 60)
    
    # Check PostgreSQL limits first
    limits = test_postgresql_limits()
    if limits:
        print(f"\n💡 Recommendation: Test with {limits['available_connections']} connections or less")
    
    # Test configurations
    test_configs = [
        {"connections": 100, "workers": 20},
        {"connections": 500, "workers": 50},
        {"connections": 1000, "workers": 100}
    ]
    
    for config in test_configs:
        connections = config["connections"]
        workers = config["workers"]
        
        print(f"\n{'='*60}")
        print(f"Testing {connections} connections with {workers} workers")
        print(f"{'='*60}")
        
        # Sync test
        print("\n🔄 Running Synchronous Test...")
        sync_results = test_connection_pool_sync(connections, workers)
        print_results(sync_results, "Synchronous")
        
        # Async test
        print("\n⚡ Running Asynchronous Test...")
        async_results = asyncio.run(test_connection_pool_async(connections))
        print_results(async_results, "Asynchronous")
        
        # Wait between tests
        if config != test_configs[-1]:
            print("\n⏳ Waiting 5 seconds before next test...")
            time.sleep(5)

if __name__ == "__main__":
    main()
