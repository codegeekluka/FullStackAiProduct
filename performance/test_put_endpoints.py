#!/usr/bin/env python3
"""
Test script for PUT endpoints that were previously slow
"""

import requests
import time
import json
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

BASE_URL = "http://127.0.0.1:8000"

def test_put_endpoints():
    print("🚀 Testing PUT Endpoints Performance")
    print("=" * 50)
    
    # Register and login
    print("🔐 Authenticating...")
    register_data = {
        "username": "puttestuser",
        "password": "testpass123"
    }
    
    try:
        register_response = requests.post(f"{BASE_URL}/register", json=register_data)
        if register_response.status_code == 200:
            print("✅ User registered successfully")
        elif register_response.status_code == 400:
            print("ℹ️ User already exists, continuing with login...")
        else:
            print(f"Registration failed: {register_response.status_code}")
            return
    except Exception as e:
        print(f"Registration error: {e}")
        return
    
    # Login
    login_data = {
        "username": "puttestuser",
        "password": "testpass123"
    }
    
    login_response = requests.post(f"{BASE_URL}/login", data=login_data)
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.status_code}")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a test recipe
    print("📝 Creating test recipe...")
    recipe_data = {
        "title": "PUT Test Recipe",
        "description": "Test recipe for PUT endpoint testing",
        "prep_time": "30",
        "cook_time": "45",
        "ingredients": ["Test ingredient 1", "Test ingredient 2"],
        "instructions": ["Step 1", "Step 2"],
        "is_active": False,
        "favorite": False
    }
    
    recipe_response = requests.post(f"{BASE_URL}/recipe/manualRecipe", json=recipe_data, headers=headers)
    if recipe_response.status_code != 200:
        print(f"Recipe creation failed: {recipe_response.status_code}")
        return
    
    recipe_slug = recipe_response.json()["slug"]
    print(f"✅ Created recipe: {recipe_slug}")
    
    # Test PUT endpoints
    endpoints_to_test = [
        ("/recipe/{slug}/favorite", "PUT", "Toggle favorite"),
        ("/recipe/{slug}/active", "PUT", "Toggle active"),
        ("/recipe/{slug}/tags", "PUT", "Add tags", {"tags": ["test-tag", "performance-tag"]})
    ]
    
    for endpoint_template, method, description, *extra_data in endpoints_to_test:
        endpoint = endpoint_template.format(slug=recipe_slug)
        print(f"\n🔍 Testing {method} {endpoint} ({description})")
        
        times = []
        for i in range(10):
            start_time = time.time()
            
            try:
                if method == "PUT":
                    if extra_data:
                        response = requests.put(f"{BASE_URL}{endpoint}", json=extra_data[0], headers=headers)
                    else:
                        response = requests.put(f"{BASE_URL}{endpoint}", headers=headers)
                    
                    if response.status_code == 200:
                        elapsed = (time.time() - start_time) * 1000
                        times.append(elapsed)
                        print(f"  Request {i+1}: {elapsed:.1f}ms")
                    else:
                        print(f"  Request {i+1}: Failed ({response.status_code})")
                else:
                    response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
                    if response.status_code == 200:
                        elapsed = (time.time() - start_time) * 1000
                        times.append(elapsed)
                        print(f"  Request {i+1}: {elapsed:.1f}ms")
                    else:
                        print(f"  Request {i+1}: Failed ({response.status_code})")
                        
            except Exception as e:
                print(f"  Request {i+1}: Error - {e}")
        
        if times:
            avg_time = sum(times) / len(times)
            median_time = sorted(times)[len(times)//2]
            p95_time = sorted(times)[int(len(times)*0.95)]
            min_time = min(times)
            max_time = max(times)
            
            print(f"  📊 Results: Avg={avg_time:.1f}ms, Median={median_time:.1f}ms, P95={p95_time:.1f}ms")
            print(f"     Min={min_time:.1f}ms, Max={max_time:.1f}ms")
            
            if p95_time < 100:
                print(f"  ✅ FAST: {description} is performing well")
            elif p95_time < 500:
                print(f"  ⚠️ MODERATE: {description} could be optimized")
            else:
                print(f"  ❌ SLOW: {description} needs optimization")

if __name__ == "__main__":
    test_put_endpoints()
