# Issue 05: Setup Centralized Logging Infrastructure

**Priority:** High
**Estimated Effort:** 1-2 days
**Labels:** `infrastructure`, `observability`, `feature`
**Phase:** 0 - DevOps Setup

## Problem Statement

From ACTIONITEMS.md: "Add logging across modules with custom log setup"

Current state:
- Only basic logging in `processor.py`
- No centralized logging configuration
- No structured logging
- Difficult to debug issues in production
- No log levels or filtering
- No consistent log format

## Current State

Minimal logging exists:
```python
# src/ragnostic/ingestion/processor/processor.py
import logging
logger = logging.getLogger(__name__)
```

But:
- No logging configuration file
- No log formatting standards
- No output destination management (file vs. console)
- Other modules have no logging at all

## Proposed Solution

Implement comprehensive logging infrastructure:

### 1. Logging Configuration Module

Create `src/ragnostic/utils/logging_config.py`:
```python
import logging
import logging.config
from pathlib import Path
from typing import Optional

def setup_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    json_format: bool = False
) -> None:
    """Configure logging for the application."""

    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": level,
                "formatter": "standard",
                "stream": "ext://sys.stdout"
            },
        },
        "loggers": {
            "ragnostic": {
                "level": level,
                "handlers": ["console"],
                "propagate": False
            },
        },
        "root": {
            "level": "WARNING",
            "handlers": ["console"]
        }
    }

    if log_file:
        config["handlers"]["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": level,
            "formatter": "detailed",
            "filename": str(log_file),
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5
        }
        config["loggers"]["ragnostic"]["handlers"].append("file")

    logging.config.dictConfig(config)
```

### 2. Environment-based Configuration

Support configuration via environment variables:
```python
# .env
LOG_LEVEL=DEBUG
LOG_FILE=logs/ragnostic.log
LOG_FORMAT=json  # or "standard"
```

### 3. Module-level Loggers

Add to each module:
```python
import logging
logger = logging.getLogger(__name__)

# Usage:
logger.debug("Processing document: %s", doc_id)
logger.info("Document validated successfully")
logger.warning("File size exceeds recommended limit: %d MB", size_mb)
logger.error("Failed to process document: %s", error)
logger.exception("Unexpected error occurred")  # Includes traceback
```

## Acceptance Criteria

- [ ] Centralized logging configuration module created
- [ ] All existing modules updated to use logging
- [ ] Log levels configurable via environment variable
- [ ] Console and file output supported
- [ ] Log rotation implemented for file output
- [ ] Structured logging option available (JSON)
- [ ] Documentation added to README
- [ ] Examples added for common logging patterns
- [ ] Tests added for logging configuration

## Implementation Steps

1. **Create logging utilities:**
   - `src/ragnostic/utils/__init__.py`
   - `src/ragnostic/utils/logging_config.py`

2. **Add logging to all modules:**
   - Monitor module
   - Validator module
   - Processor module (enhance existing)
   - Indexer module
   - Database client
   - Workflow orchestration

3. **Add configuration:**
   - Update `.env.template` with LOG_* variables
   - Add logging setup to main entry point
   - Create default log directory in `.gitignore`

4. **Add Makefile target:**
   ```makefile
   .PHONY: logs-clean

   logs-clean:
       rm -rf logs/*.log
   ```

5. **Update .gitignore:**
   ```
   logs/
   *.log
   ```

6. **Documentation:**
   - Add logging section to README
   - Document log levels and when to use them
   - Show examples of structured logging

## Logging Strategy by Component

### Monitor
- DEBUG: File discovery events
- INFO: Directory scan started/completed
- WARNING: Permission issues accessing files

### Validator
- DEBUG: Validation checks being performed
- INFO: Document validated/rejected
- WARNING: File size approaching limits
- ERROR: Validation failures

### Processor
- DEBUG: File operations (copy, move)
- INFO: Document processed successfully
- ERROR: Processing failures

### Indexer
- DEBUG: Metadata extraction steps
- INFO: Document indexed successfully
- WARNING: Missing metadata fields
- ERROR: Indexing failures

### Database
- DEBUG: SQL queries (in development only)
- INFO: Database operations (create, update)
- ERROR: Database errors, constraint violations

### Workflow
- INFO: Stage transitions
- WARNING: Retries, degraded performance
- ERROR: Workflow failures

## Dependencies

None - can be implemented independently

## Testing Strategy

1. **Unit Tests:**
   ```python
   def test_logging_setup(tmp_path):
       log_file = tmp_path / "test.log"
       setup_logging(level="DEBUG", log_file=log_file)

       logger = logging.getLogger("ragnostic.test")
       logger.info("Test message")

       assert log_file.exists()
       assert "Test message" in log_file.read_text()
   ```

2. **Integration Tests:**
   - Run ingestion pipeline with DEBUG level
   - Verify all stages produce logs
   - Check log file rotation works
   - Verify JSON format output is valid

3. **Performance Tests:**
   - Ensure logging doesn't significantly slow processing
   - Test log file rotation under load

## Parallel Work Opportunities

Can be worked on **in parallel** with:
- Issue #01 (CI/CD)
- Issue #02 (linting)
- Issue #03 (package installation)
- Issue #04 (pre-commit)
- Issue #06 (pytest markers)

**Enhances all future issues** - better debugging capability

## Advanced Features (Optional)

### Structured Logging with structlog

For production deployments:
```python
import structlog

logger = structlog.get_logger()
logger.info("document_processed", doc_id=doc_id, size_mb=size, duration_sec=duration)
```

Output:
```json
{"event": "document_processed", "doc_id": "abc123", "size_mb": 5.2, "duration_sec": 1.3, "timestamp": "2025-01-15T10:30:00Z"}
```

### Log Aggregation

Consider integration with:
- CloudWatch Logs (AWS)
- Elasticsearch + Kibana (ELK stack)
- Datadog, Sentry, etc.

### Correlation IDs

For tracing requests through pipeline:
```python
import contextvars

request_id = contextvars.ContextVar('request_id')

# In each log:
logger.info("Processing", extra={"request_id": request_id.get()})
```

## Notes

- Use lazy string formatting: `logger.info("Value: %s", val)` not `f"Value: {val}"`
- Never log sensitive data (API keys, passwords, PII)
- Use appropriate log levels:
  - DEBUG: Detailed diagnostic information
  - INFO: General informational messages
  - WARNING: Warning messages (recoverable issues)
  - ERROR: Error messages (operation failed)
  - CRITICAL: Critical errors (application may crash)
- Consider log sampling for high-volume operations
- Log file paths should be configurable for different environments
