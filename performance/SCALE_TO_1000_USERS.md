# Scaling Recipe App to 1000+ Concurrent Users

## 🎯 **Goal**
Support 1000+ concurrent users with <500ms response times

## 📊 **Current State vs Target**
- **Current**: 100 users, 20-100ms response times
- **Target**: 1000+ users, <500ms response times
- **Challenge**: Response times spike at high concurrency

---

## 🔧 **Database Scaling (Critical)**

### 1. **Connection Pool Optimization**
Current: 150 total connections (50 + 100 overflow)
**Target: 500+ total connections**

```python
# backend/database/database.py
engine = create_engine(
    DATABASE_URL,
    pool_size=200,           # Was: 50
    max_overflow=300,        # Was: 100 (Total: 500 connections)
    pool_pre_ping=True,
    pool_recycle=1800,
    pool_timeout=30,
    echo=False,
    connect_args={
        "connect_timeout": 10,
        "application_name": "recipe_app_api"
    }
)
```

### 2. **PostgreSQL Server Configuration**
**Critical for 1000+ users:**

```sql
-- postgresql.conf optimizations
max_connections = 1000                    # Was: 200
shared_buffers = 1GB                      # Was: 256MB
effective_cache_size = 4GB                # Was: 1GB
work_mem = 8MB                           # Was: 4MB
maintenance_work_mem = 256MB              # Was: 64MB
checkpoint_completion_target = 0.9
wal_buffers = 32MB                       # Was: 16MB
default_statistics_target = 200           # Was: 100
random_page_cost = 1.1
```

### 3. **Database Connection Pooling (PgBouncer)**
**Essential for 1000+ users:**

```bash
# Install PgBouncer
sudo apt-get install pgbouncer

# Configure PgBouncer
# /etc/pgbouncer/pgbouncer.ini
[databases]
recipe_app = host=localhost port=5432 dbname=recipe_app

[pgbouncer]
listen_port = 6432
listen_addr = 127.0.0.1
auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 100
```

---

## 🚀 **Application-Level Optimizations**

### 1. **Async Database Operations**
Convert synchronous database calls to async:

```python
# backend/database/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

async_engine = create_async_engine(
    DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    pool_size=200,
    max_overflow=300,
    echo=False
)

async def get_async_db():
    async with AsyncSession(async_engine) as session:
        yield session
```

### 2. **Caching Layer (Redis)**
**Essential for 1000+ users:**

```python
# backend/services/cache.py
import redis
import json
from functools import wraps

redis_client = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True,
    max_connections=100
)

def cache_result(expire_time=300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, expire_time, json.dumps(result))
            return result
        return wrapper
    return decorator
```

### 3. **Database Query Optimization**
Implement read replicas and query optimization:

```python
# backend/database/database.py
# Separate read/write connections
write_engine = create_engine(WRITE_DATABASE_URL, pool_size=50, max_overflow=100)
read_engine = create_engine(READ_DATABASE_URL, pool_size=150, max_overflow=200)

def get_write_db():
    return SessionLocal(bind=write_engine)

def get_read_db():
    return SessionLocal(bind=read_engine)
```

---

## 🏗️ **Infrastructure Scaling**

### 1. **Load Balancing**
Use multiple application instances:

```yaml
# docker-compose.yml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000-8009:8000"
    deploy:
      replicas: 5
    environment:
      - DATABASE_URL=postgresql://user:pass@pgbouncer:6432/recipe_app
```

### 2. **Database Clustering**
PostgreSQL read replicas:

```sql
-- Primary database
-- Configure streaming replication

-- Read replicas (2-3 instances)
-- Handle read queries only
```

### 3. **Connection Pooling Service**
PgBouncer or similar:

```bash
# Run PgBouncer as service
pgbouncer -d /etc/pgbouncer/pgbouncer.ini
```

---

## 📊 **Performance Monitoring**

### 1. **Database Monitoring**
```sql
-- Monitor connection usage
SELECT 
    datname,
    numbackends,
    xact_commit,
    xact_rollback,
    blks_read,
    blks_hit
FROM pg_stat_database 
WHERE datname = 'recipe_app';

-- Monitor slow queries
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    rows
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;
```

### 2. **Application Monitoring**
```python
# backend/middleware/monitoring.py
import time
from fastapi import Request
import logging

logger = logging.getLogger(__name__)

@app.middleware("http")
async def monitor_performance(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(f"{request.url.path} took {process_time:.3f}s")
    
    return response
```

---

## 🧪 **Testing Strategy**

### 1. **Gradual Scaling Test**
```bash
# Test with increasing load
python load_test_results/run_load_test.py --users 100
python load_test_results/run_load_test.py --users 500
python load_test_results/run_load_test.py --users 1000
```

### 2. **Database Connection Test**
```python
# performance/test_db_connections.py
import asyncio
import psycopg2
from concurrent.futures import ThreadPoolExecutor

async def test_connection_pool():
    """Test database connection pool under load"""
    with ThreadPoolExecutor(max_workers=1000) as executor:
        futures = []
        for i in range(1000):
            future = executor.submit(test_single_connection, i)
            futures.append(future)
        
        results = await asyncio.gather(*futures)
        return results
```

---

## 🚀 **Implementation Steps**

### **Phase 1: Database Optimization (Week 1)**
1. ✅ Increase connection pool to 500 connections
2. ✅ Configure PostgreSQL for high concurrency
3. ✅ Install and configure PgBouncer
4. ✅ Add database monitoring

### **Phase 2: Application Optimization (Week 2)**
1. ✅ Implement Redis caching
2. ✅ Convert to async database operations
3. ✅ Add read/write separation
4. ✅ Implement connection pooling

### **Phase 3: Infrastructure Scaling (Week 3)**
1. ✅ Set up load balancer
2. ✅ Deploy multiple app instances
3. ✅ Configure database clustering
4. ✅ Implement monitoring

### **Phase 4: Testing & Tuning (Week 4)**
1. ✅ Run 1000-user load tests
2. ✅ Monitor and optimize bottlenecks
3. ✅ Fine-tune configurations
4. ✅ Document performance results

---

## 💰 **Cost Considerations**

### **Infrastructure Costs (Monthly)**
- **Database**: $200-500 (managed PostgreSQL with read replicas)
- **Redis**: $50-100 (managed Redis for caching)
- **Load Balancer**: $50-100
- **Monitoring**: $50-100
- **Total**: $350-800/month

### **Development Costs**
- **PgBouncer Setup**: 2-3 days
- **Caching Implementation**: 3-4 days
- **Async Conversion**: 1-2 weeks
- **Testing & Tuning**: 1 week

---

## 🎯 **Expected Results**

### **Performance Targets**
- **1000 concurrent users**: <500ms response time
- **Database connections**: <80% utilization
- **Cache hit rate**: >80%
- **Error rate**: <1%

### **Success Metrics**
- ✅ Load test passes with 1000 users
- ✅ Response times remain under 500ms
- ✅ Database handles load without connection errors
- ✅ Cache reduces database load significantly

---

## 🔧 **Quick Start Commands**

```bash
# 1. Update database configuration
python performance/optimize_postgres_config.py

# 2. Install PgBouncer
sudo apt-get install pgbouncer

# 3. Test current performance
python performance/performance_test.py

# 4. Run scaling load test
python load_test_results/run_load_test.py --users 1000

# 5. Monitor database
python performance/monitor_database.py
```

**1000+ concurrent users is definitely achievable with proper infrastructure and optimization!** 🚀
