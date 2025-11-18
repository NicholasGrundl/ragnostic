# Issue 06: Organize Tests with Pytest Markers

**Priority:** High
**Estimated Effort:** 0.5 days
**Labels:** `testing`, `developer-experience`, `code-quality`
**Phase:** 0 - DevOps Setup

## Problem Statement

From ACTIONITEMS.md:
- "Setup test commands with pytest.mark tags"
- "Fast/unit tests vs slow/integration tests"
- "Make commands for testing"

Current issues:
- All tests run at same speed (no fast/slow distinction)
- Cannot selectively run unit tests vs integration tests
- CI/CD must run all tests (slow feedback loop)
- Developers cannot quickly validate changes

## Current State

- 72 test functions exist across test files
- No pytest markers in use
- All tests run together with `pytest`
- No way to filter by speed or type
- No Makefile targets for different test suites

## Proposed Solution

Implement pytest markers to categorize tests:

### Marker Categories

1. **Speed Markers:**
   - `@pytest.mark.fast` - Unit tests, <1s each
   - `@pytest.mark.slow` - Integration tests, database operations

2. **Type Markers:**
   - `@pytest.mark.unit` - Pure unit tests, no external dependencies
   - `@pytest.mark.integration` - Tests with database, file I/O
   - `@pytest.mark.workflow` - Full workflow/pipeline tests

3. **Component Markers:**
   - `@pytest.mark.database`
   - `@pytest.mark.monitor`
   - `@pytest.mark.validator`
   - `@pytest.mark.processor`
   - `@pytest.mark.indexer`

### Configuration (pytest.ini or pyproject.toml)

```toml
[tool.pytest.ini_options]
minversion = "7.0"
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]

markers = [
    "fast: marks tests as fast unit tests (deselect with '-m \"not fast\"')",
    "slow: marks tests as slow integration tests (deselect with '-m \"not slow\"')",
    "unit: marks tests as pure unit tests",
    "integration: marks tests as integration tests",
    "workflow: marks tests as workflow/pipeline tests",
    "database: marks tests that interact with database",
    "monitor: marks tests for directory monitor component",
    "validator: marks tests for document validator component",
    "processor: marks tests for document processor component",
    "indexer: marks tests for document indexer component",
]

# Coverage configuration
addopts = """
    --strict-markers
    --strict-config
    --cov=ragnostic
    --cov-report=term-missing
    --cov-report=html
    --cov-report=xml
"""
```

## Acceptance Criteria

- [ ] Pytest markers configured in `pyproject.toml`
- [ ] All existing tests marked appropriately
- [ ] Fast tests complete in <10 seconds total
- [ ] Slow tests separated and documented
- [ ] Makefile targets created for different test suites
- [ ] CI/CD uses appropriate marker selection
- [ ] Documentation added to README

## Implementation Steps

1. **Add marker configuration to pyproject.toml** (see above)

2. **Mark existing tests:**
   ```python
   import pytest

   # Fast unit test
   @pytest.mark.fast
   @pytest.mark.unit
   @pytest.mark.validator
   def test_file_exists_check():
       """Test file existence validation logic."""
       # ...

   # Slow integration test
   @pytest.mark.slow
   @pytest.mark.integration
   @pytest.mark.database
   def test_document_indexing_pipeline(db_client, tmp_path):
       """Test full document indexing with database."""
       # ...
   ```

3. **Review and categorize all 72 tests:**
   - Review each test file
   - Add appropriate markers
   - Aim for ~80% fast, ~20% slow

4. **Add Makefile targets:**
   ```makefile
   .PHONY: test test-fast test-slow test-unit test-integration test-cov

   test:
       pytest

   test-fast:
       pytest -m fast -v

   test-slow:
       pytest -m slow -v

   test-unit:
       pytest -m unit -v

   test-integration:
       pytest -m integration -v

   test-cov:
       pytest --cov=ragnostic --cov-report=term-missing --cov-report=html

   test-component-%:
       pytest -m $* -v  # e.g., make test-component-validator
   ```

5. **Update CI/CD workflow:**
   ```yaml
   # Fast tests on every PR
   - name: Run fast tests
     run: make test-fast

   # Full test suite on main branch
   - name: Run all tests
     run: make test
     if: github.ref == 'refs/heads/main'
   ```

6. **Document usage in README:**
   ```markdown
   ## Testing

   Run all tests:
   ```bash
   make test
   ```

   Run only fast tests (recommended during development):
   ```bash
   make test-fast
   ```

   Run only integration tests:
   ```bash
   make test-integration
   ```

   Run tests for specific component:
   ```bash
   pytest -m validator  # or monitor, processor, indexer
   ```

   Generate coverage report:
   ```bash
   make test-cov
   open htmlcov/index.html
   ```
   ```

## Dependencies

**Required before:**
- Issue #03 (package must be installable to run tests)

**Enhanced by:**
- Issue #02 (linting ensures marker syntax is correct)

## Testing Strategy

1. **Verify markers work:**
   ```bash
   # Should run only fast tests
   pytest -m fast

   # Should run only slow tests
   pytest -m slow

   # Should run everything except slow tests
   pytest -m "not slow"

   # Should run database tests
   pytest -m database
   ```

2. **Verify speed categorization:**
   ```bash
   # Fast tests should complete quickly
   time pytest -m fast  # Target: <10 seconds
   ```

3. **Verify marker combinations:**
   ```bash
   # Fast database tests only
   pytest -m "fast and database"

   # Unit tests that aren't database tests
   pytest -m "unit and not database"
   ```

## Parallel Work Opportunities

Can be worked on **in parallel** with:
- Issue #01 (CI/CD)
- Issue #04 (pre-commit hooks)
- Issue #05 (logging)

Must be worked **after**:
- Issue #03 (package installation)

Can work **before**:
- Issue #08 (integration tests benefit from markers)

## Test Categorization Guidelines

### Fast Tests (Unit)
- No file I/O
- No database operations
- No external API calls
- Pure logic testing
- Mock external dependencies
- Target: <100ms per test

### Slow Tests (Integration)
- Database operations
- File system operations
- Real PDF processing
- Workflow orchestration
- External service calls (if any)
- Target: <5s per test

## Example Markings

```python
# tests/test_db.py
@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.database
def test_create_document(db_client):
    """Test database document creation."""
    pass

# tests/ingestion_validation/test_checks.py
@pytest.mark.fast
@pytest.mark.unit
@pytest.mark.validator
def test_file_exists_check_valid_file(tmp_path):
    """Test file existence check with valid file."""
    pass

# tests/ingestion_workflow/test_full_pipeline.py
@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.workflow
def test_complete_ingestion_workflow(tmp_path, db_client):
    """Test full ingestion pipeline end-to-end."""
    pass
```

## Notes

- Use `--strict-markers` to catch typos in marker names
- Can combine markers: `pytest -m "fast and validator"`
- Negative selection: `pytest -m "not slow"`
- List available markers: `pytest --markers`
- Consider adding `@pytest.mark.skip` for known failing tests
- Use `@pytest.mark.xfail` for expected failures
- Can mark entire test classes: `@pytest.mark.integration` on class
