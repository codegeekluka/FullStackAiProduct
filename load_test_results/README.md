# Load Test Results

This folder contains all load testing results and reports for the Recipe App.

## 📁 **Files Overview**

### 📊 **Test Results**
- **`load_test_report.html`** - Locust HTML report with detailed metrics and charts
- **`run_load_test.py`** - Load test runner script
- **`*.csv`** - Generated automatically during test runs (not committed to git)

### 📚 **Documentation**
- **`LOAD_TESTING_README.md`** - Complete guide for running load tests

## 🚀 **Running Load Tests**

### **Quick Start**
```bash
# From the load_test_results directory
python run_load_test.py

# From the root directory
python load_test_results/run_load_test.py

# Or use Locust directly
locust -f ../locustfile.py --host=http://127.0.0.1:8000
```

### **Configuration**
- **Target Host**: `http://127.0.0.1:8000` (use 127.0.0.1, not localhost for better performance)
- **Concurrent Users**: 50-200 (configurable)
- **Test Duration**: 5 minutes (configurable)
- **Spawn Rate**: 10 users/second (configurable)

## 📈 **Understanding Results**

### **Key Metrics**
- **Response Time**: Average, median, P95, P99
- **Request Rate**: Requests per second
- **Success Rate**: Percentage of successful requests
- **Error Rate**: Failed requests and exceptions

### **Performance Targets**
- **Response Time**: <500ms for 95th percentile
- **Success Rate**: >99%
- **Concurrent Users**: 100+ supported

## 🔧 **Performance Tools**

For detailed performance analysis and optimization, see the `/performance/` folder:
- Database index creation
- PostgreSQL optimization
- Endpoint-specific testing
- Network diagnostics
- System resource monitoring

## 📝 **Notes**

- Results are timestamped and should be archived after analysis
- Compare results across different test runs to track improvements
- Use the performance tools to diagnose any issues found in load tests
