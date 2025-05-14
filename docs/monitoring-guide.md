# Monitoring & Logging Guide

This guide covers monitoring, logging, and observability best practices for GastroAssist in production environments.

## Overview

Proper monitoring and logging are essential for maintaining the reliability and performance of GastroAssist in production. This guide outlines recommended practices for setting up comprehensive monitoring and logging solutions.

## Logging Configuration

### Log Levels

GastroAssist uses Python's standard logging library with the following log levels:

- **DEBUG**: Detailed debug information
- **INFO**: Confirmation that things are working as expected
- **WARNING**: Indication that something unexpected happened, but the application is still working
- **ERROR**: Due to a more serious problem, the application couldn't perform some function
- **CRITICAL**: A serious error indicating that the program itself may be unable to continue running

### Log Format

The recommended log format includes timestamp, log level, module, and message:

```python
import logging
from logging.handlers import RotatingFileHandler
import os

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(
            'logs/gastroassist.log',
            maxBytes=10485760,  # 10MB
            backupCount=5
        ),
        logging.StreamHandler()
    ]
)

# Get logger for module
logger = logging.getLogger(__name__)
```

### What to Log

Include the following information in logs:

1. **System Events**:
   - Application startup and shutdown
   - Configuration changes
   - Service connections and disconnections

2. **User Interactions**:
   - Queries processed (without PII)
   - Search operations
   - Error responses

3. **External Service Interactions**:
   - API calls (without sensitive parameters)
   - Response times
   - Error responses

4. **Performance Metrics**:
   - Query processing time
   - Component timing (search, extraction, summarization)
   - Resource usage

### Sensitive Information

Never log the following sensitive information:

- API keys or credentials
- Full user queries (may contain PHI)
- Personal identifying information
- Complete error stack traces in production

## Monitoring Setup

### Health Check Endpoint

Implement a health check endpoint that monitoring systems can poll:

```python
@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring
    """
    # Check database connection
    db_status = await check_db_connection()
    
    # Check API connections
    openai_status = await check_openai_connection()
    tavily_status = await check_tavily_connection()
    
    # Return overall health status
    return {
        "status": "healthy" if all([db_status, openai_status, tavily_status]) else "unhealthy",
        "components": {
            "database": "connected" if db_status else "disconnected",
            "openai_api": "connected" if openai_status else "disconnected",
            "tavily_api": "connected" if tavily_status else "disconnected",
        },
        "version": "0.1.0",
        "timestamp": datetime.now().isoformat()
    }
```

### Key Metrics to Monitor

1. **System Metrics**:
   - CPU usage
   - Memory usage
   - Disk I/O
   - Network traffic

2. **Application Metrics**:
   - Request rate
   - Response time
   - Error rate
   - Active connections

3. **Database Metrics**:
   - Connection pool usage
   - Query performance
   - Database size
   - Transaction rate

4. **API Metrics**:
   - OpenAI API latency
   - Tavily API latency
   - API rate limits
   - API errors

### Monitoring Tools

#### Prometheus + Grafana Setup

1. **Install Prometheus Client**:
   ```bash
   pip install prometheus-client
   ```

2. **Implement Metrics in FastAPI**:
   ```python
   from prometheus_client import Counter, Histogram, Gauge, Summary
   from prometheus_fastapi_instrumentator import Instrumentator
   
   # Initialize metrics
   REQUESTS_TOTAL = Counter(
       "gastroassist_requests_total",
       "Total number of requests processed",
       ["method", "endpoint", "status_code"]
   )
   
   RESPONSE_TIME = Histogram(
       "gastroassist_response_time_seconds",
       "Response time in seconds",
       ["method", "endpoint"]
   )
   
   ACTIVE_REQUESTS = Gauge(
       "gastroassist_active_requests",
       "Number of active requests"
   )
   
   QUERY_PROCESSING_TIME = Summary(
       "gastroassist_query_processing_time_seconds",
       "Time spent processing queries",
       ["query_type"]
   )
   
   # Instrument FastAPI app
   Instrumentator().instrument(app).expose(app)
   ```

3. **Sample Prometheus Configuration**:
   ```yaml
   # prometheus.yml
   global:
     scrape_interval: 15s
   
   scrape_configs:
     - job_name: 'gastroassist'
       scrape_interval: 5s
       static_configs:
         - targets: ['localhost:8000']
   ```

4. **Basic Grafana Dashboard**:
   Create a dashboard with the following panels:
   - Request rate by endpoint
   - Average response time
   - Error rate
   - API latency
   - System resource usage

#### CloudWatch (AWS)

If deploying on AWS:

1. **Install CloudWatch Agent**:
   ```bash
   pip install watchtower
   ```

2. **Configure Logging to CloudWatch**:
   ```python
   import watchtower
   import logging
   
   # CloudWatch handler
   cloudwatch_handler = watchtower.CloudWatchLogHandler(
       log_group='GastroAssist',
       stream_name='api-{instance_id}'
   )
   
   # Add to root logger
   logging.getLogger().addHandler(cloudwatch_handler)
   ```

3. **Set Up CloudWatch Alarms**:
   - High error rate
   - High latency
   - Low health check success rate
   - Resource constraints

### Custom Instrumentation

Implement custom instrumentation for critical components:

```python
import time
from contextlib import contextmanager

@contextmanager
def timing_context(name, logger=None):
    """Context manager for timing code blocks"""
    start_time = time.time()
    try:
        yield
    finally:
        elapsed_time = time.time() - start_time
        if logger:
            logger.info(f"{name} took {elapsed_time:.3f} seconds")
        
        # Update Prometheus metric if available
        if name.startswith("query_"):
            QUERY_PROCESSING_TIME.labels(query_type=name).observe(elapsed_time)

# Usage example
async def process_query(query: Query):
    with timing_context("query_processing", logger):
        # Process query
        processed_query = query_processor.process(query.text)
    
    with timing_context("information_needs_analysis", logger):
        # Analyze information needs
        information_needs = reasoning_agent.analyze(processed_query)
    
    # More steps...
```

## Alerting

### Alert Thresholds

Set up alerts for the following conditions:

1. **Availability Issues**:
   - Health check failures
   - High HTTP 5xx error rate (>1%)
   - API service unavailability

2. **Performance Issues**:
   - High response time (>5s for 95th percentile)
   - High CPU usage (>80% for 5 minutes)
   - High memory usage (>85% for 5 minutes)

3. **Functional Issues**:
   - High error rate in summary generation
   - External API failures
   - Database connection issues

### Alert Notification Channels

Configure multiple notification channels:

- Email for non-urgent issues
- SMS or phone calls for critical issues
- Integration with incident management systems
- Team chat (Slack, Microsoft Teams, etc.)

## Log Analysis

### Centralized Logging

For distributed deployments, implement centralized logging with:

- **ELK Stack** (Elasticsearch, Logstash, Kibana)
- **Graylog**
- **AWS CloudWatch Logs**
- **Google Cloud Logging**

### Log Retention

Implement a log retention policy:

- Production logs: 30-90 days
- Error logs: 90-180 days
- Audit logs: 1 year (or as required by regulations)

### Common Log Queries

Prepare common log queries for troubleshooting:

- Errors within a specific time range
- Slow queries (>2s processing time)
- API failures
- Authentication failures

## Dashboard Examples

### Operations Dashboard

Key metrics for operations team:

- System health status
- Request volume and trends
- Error rates
- API usage and limits
- Resource utilization

### Development Dashboard

Key metrics for developers:

- Component performance
- Error distribution by component
- Test coverage
- API response times
- Specific error types and frequencies

### Executive Dashboard

Key metrics for leadership:

- Overall system availability
- User engagement metrics
- Query volume trends
- Success rate
- Cost metrics (API usage, infrastructure)

## Incident Response

### Monitoring During Incidents

During incidents, focus monitoring on:

1. Impact metrics:
   - Error rate
   - Affected users/requests
   - Performance degradation

2. Root cause indicators:
   - Resource bottlenecks
   - External service degradation
   - Network issues

### Post-Incident Analysis

After resolution, analyze:

1. Incident timeline from logs
2. Performance metrics during the incident
3. Warning signs that preceded the incident
4. Effectiveness of alerts and response

## Performance Optimization

Use monitoring data to identify optimization opportunities:

1. **Query Processing Performance**:
   - Identify slow queries
   - Optimize reasoning agent logic
   - Cache common queries

2. **External API Optimization**:
   - Adjust timeouts
   - Implement retries with backoff
   - Consider caching where appropriate

3. **Resource Allocation**:
   - Right-size instances based on utilization
   - Scale components independently
   - Optimize database performance

## Compliance Considerations

For healthcare deployments, consider:

1. **Audit Logging**:
   - Track all access to the system
   - Log authentication events
   - Maintain immutable logs

2. **Data Access Monitoring**:
   - Monitor for unusual access patterns
   - Log all data retrieval operations
   - Implement alerts for suspicious activity

## Conclusion

Effective monitoring and logging are critical for maintaining a reliable, performant GastroAssist deployment. Start with basic logging and health checks, then gradually implement more sophisticated monitoring as your deployment scales. Regularly review and refine your monitoring strategy based on operational experience and changing requirements.
