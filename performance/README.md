# Performance Testing & Optimization Tools

This folder contains all performance-related tools and documentation for the Recipe App.

Run locust from root directory to run performance

## 📁 Files Overview

### 🔧 **Setup & Optimization**
- **`create_performance_indexes.py`** - Creates database indexes for fast queries
- **`optimize_postgres_config.py`** - Checks and suggests PostgreSQL optimizations
- **`PERFORMANCE_OPTIMIZATIONS.md`** - Complete summary of all optimizations made

### 🧪 **Testing Tools**
- **`performance_test.py`** - Comprehensive performance testing (individual + concurrent)
- **`test_put_endpoints.py`** - Tests PUT endpoint performance specifically
- **`quick_performance_test.py`** - Quick health check and localhost vs 127.0.0.1 comparison
- **`network_test.py`** - Diagnoses network latency issues
- **`system_diagnostic.py`** - Checks system resources and potential crash causes

## 🚀 **Quick Start**

### 1. **Setup Database Indexes** (One-time)
```bash
python performance/create_performance_indexes.py
```

### 2. **Check PostgreSQL Settings**
```bash
python performance/optimize_postgres_config.py
```

### 3. **Run Performance Tests**
```bash
# Quick health check
python performance/quick_performance_test.py

# Comprehensive testing
python performance/performance_test.py

# Test specific endpoints
python performance/test_put_endpoints.py
```

### 4. **Diagnose Issues**
```bash
# Network problems
python performance/network_test.py

# System resources
python performance/system_diagnostic.py
```

## 📊 **Performance Targets**

- **Response Times**: <500ms for 95th percentile
- **Concurrent Users**: 100+ supported
- **Success Rate**: >99%
- **Connection Errors**: <1%

## 🎯 **Key Optimizations Applied**

1. **Database Connection Pool**: 150 total connections
2. **Database Indexes**: 7 critical indexes created
3. **Query Optimization**: N+1 queries eliminated
4. **Error Handling**: Retry logic for connection resets
5. **Lightweight Endpoints**: Reduced data transfer

See `PERFORMANCE_OPTIMIZATIONS.md` for complete details.
