# Structured Logging for Grafana/Monitoring

This application uses structured logging to track key events for monitoring and analysis in systems like Grafana, Datadog, or CloudWatch.

## Log Format

All logs follow this format:
```
[EVENT_TYPE] key=value key2=value2 ... session_id=<id>
```

The logs include an `extra` dict with structured fields for easy parsing:
```python
logger.info("[EVENT_TYPE] key=value", extra={"event": "event_type", "key": "value", ...})
```

## Event Types

### 1. TOOL_CALL
Logged when a tool is invoked.

**Fields:**
- `tool_name`: Name of the tool
- `has_all_fields`: Whether all required fields were provided
- `session_id`: Session identifier
- Additional context: `zip_code`, etc.

**Example:**
```
[TOOL_CALL] tool=get-enhanced-quick-quote session_id=abc123 has_all_fields=True
```

### 2. QUOTE_REQUEST
Logged when a quote request is initiated.

**Fields:**
- `zip_code`: ZIP code for the quote
- `num_vehicles`: Number of vehicles (or None)
- `num_drivers`: Number of drivers (or None)
- `coverage_preference`: Coverage type
- `session_id`: Session identifier

**Example:**
```
[QUOTE_REQUEST] zip=90210 vehicles=1 drivers=1 coverage=full_coverage session_id=abc123
```

### 3. QUOTE_GENERATED
Logged when a quote is successfully generated.

**Fields:**
- `zip_code`: ZIP code
- `state`: State abbreviation
- `num_carriers`: Number of carriers in quote
- `num_vehicles`: Number of vehicles
- `num_drivers`: Number of drivers
- `coverage_type`: Type of coverage
- `session_id`: Session identifier
- Additional: `city`, `lookup_failed`

**Example:**
```
[QUOTE_GENERATED] zip=90210 state=CA carriers=3 vehicles=1 drivers=1 coverage=full_coverage session_id=abc123
```

### 4. CARRIER_ESTIMATION
Logged when carrier estimates are generated.

**Fields:**
- `zip_code`: ZIP code
- `state`: State abbreviation
- `num_carriers`: Number of carriers estimated
- `baseline_annual`: Baseline annual premium
- `confidence`: Confidence level (low, medium, high)
- `session_id`: Session identifier

**Example:**
```
[CARRIER_ESTIMATION] zip=90210 state=CA carriers=3 baseline=$4282 confidence=medium session_id=abc123
```

### 5. PHONE_ONLY_STATE
Logged when a phone-only state (AK, HI, MA) is detected.

**Fields:**
- `zip_code`: ZIP code
- `state`: State detected
- `lookup_failed`: Whether ZIP lookup failed
- `session_id`: Session identifier

**Example:**
```
[PHONE_ONLY_STATE] zip=99501 state=AK lookup_failed=False session_id=abc123
```

### 6. BATCH_INCOMPLETE
Logged when a batch of required fields is incomplete.

**Fields:**
- `batch_name`: Name of the batch (batch_1, batch_2)
- `missing_fields`: List of missing field names
- `missing_count`: Count of missing fields
- `session_id`: Session identifier
- Additional: `zip_code`

**Example:**
```
[BATCH_INCOMPLETE] batch=batch_2 missing=2 fields=Number of drivers,Driver details session_id=abc123
```

### 7. DUPLICATE_CALL (Warning Level)
Logged when a duplicate tool call is detected.

**Fields:**
- `tool_name`: Name of the tool
- `seconds_since_last`: Seconds since the last identical call
- `session_id`: Session identifier

**Example:**
```
[DUPLICATE_CALL] tool=get-enhanced-quick-quote seconds_ago=5 session_id=abc123
```

## Grafana Query Examples

### Count quotes by state (last 24h)
```
{event="quote_generated"} | json | state != "" | count by state
```

### Track duplicate calls
```
{event="duplicate_call"} | json | seconds_since_last < 10
```

### Monitor phone-only state frequency
```
{event="phone_only_state"} | json | count
```

### Average baseline premium by state
```
{event="carrier_estimation"} | json | avg(baseline_annual) by state
```

### Track incomplete batches
```
{event="batch_incomplete"} | json | count by batch_name
```

## Session ID

Currently defaults to `"unknown"`. To add session tracking:

1. Extract session ID from request context
2. Pass it to logging functions:
   ```python
   log_quote_generated(
       zip_code="90210",
       state="CA",
       num_carriers=3,
       session_id="session_abc123",  # Add this
       ...
   )
   ```

## Environment Setup

The logging level is controlled by environment variables:
- `INSURANCE_LOG_LEVEL` (default: INFO)
- `LOG_LEVEL`
- `UVICORN_LOG_LEVEL`

To see all structured logs:
```bash
INSURANCE_LOG_LEVEL=INFO uvicorn insurance_server_python.main:app --port 8000
```

## JSON Format for Log Aggregation

All logs include structured `extra` fields that can be extracted by log aggregators:

```python
{
    "event": "quote_generated",
    "zip_code": "90210",
    "state": "CA",
    "num_carriers": 3,
    "num_vehicles": 1,
    "num_drivers": 1,
    "coverage_type": "full_coverage",
    "session_id": "abc123",
    "city": "Beverly Hills",
    "lookup_failed": false
}
```

Configure your log shipper (Fluentd, Logstash, etc.) to parse these fields for indexing in Grafana/Elasticsearch.
