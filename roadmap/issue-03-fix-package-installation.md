# Issue 03: Fix Package Installation Issues

**Priority:** Critical
**Estimated Effort:** 0.5 days
**Labels:** `bug`, `packaging`, `critical`
**Phase:** 0 - DevOps Setup

## Problem Statement

Tests cannot run because the package is not properly installable:
```
ModuleNotFoundError: No module named 'ragnostic'
```

The `pyproject.toml` has an empty dependencies list, while actual dependencies are in `requirements.txt`. This causes:
- Tests fail with import errors
- Package cannot be installed via pip
- Development workflow is broken
- CI/CD cannot run tests

## Current State

**pyproject.toml:**
```toml
[project]
name = "ragnostic"
version = "0.1.0"
dependencies = []  # ← EMPTY!
```

**requirements.txt:**
- Contains 44 actual dependencies
- Not referenced by pyproject.toml
- Must be installed separately

## Proposed Solution

### Option 1: Move Dependencies to pyproject.toml (Recommended)

Move all dependencies from `requirements.txt` to `pyproject.toml`:

```toml
[project]
name = "ragnostic"
version = "0.1.0"
dependencies = [
    "python-magic",
    "docling",
    "marker-pdf",
    # ... all other dependencies
]

[project.optional-dependencies]
dev = [
    "jupyterlab",
    "pytest",
    "pytest-cov",
    "mypy",
    "ruff",
]
```

### Option 2: Keep requirements.txt (Alternative)

If keeping requirements.txt for compatibility:
```toml
[project]
name = "ragnostic"
dynamic = ["dependencies"]

[tool.setuptools.dynamic]
dependencies = {file = ["requirements.txt"]}
```

## Acceptance Criteria

- [ ] `pyproject.toml` properly declares all dependencies
- [ ] `pip install -e .` succeeds without errors
- [ ] `pip install .` works in clean virtual environment
- [ ] Tests can import `ragnostic` module
- [ ] `pytest` runs successfully
- [ ] Development dependencies separated from production
- [ ] Installation instructions in README are updated

## Implementation Steps

1. **Choose approach** (Option 1 recommended for modern Python projects)
2. **Update pyproject.toml:**
   - Add all dependencies from requirements.txt
   - Separate dev dependencies to `[project.optional-dependencies]`
   - Add optional dependencies for different platforms (PyTorch variants)
3. **Test installation:**
   ```bash
   # Create fresh venv
   python -m venv test_env
   source test_env/bin/activate

   # Test installation
   pip install -e .

   # Verify imports work
   python -c "import ragnostic"

   # Test dev install
   pip install -e ".[dev]"
   pytest
   ```
4. **Update documentation:**
   - Update README installation section
   - Update requirements files or remove if consolidated
   - Update Makefile if needed

## Dependencies

None - this is foundational

## Testing Strategy

1. **Clean Environment Test:**
   - Create new virtualenv
   - Run `pip install -e .`
   - Verify all imports work
   - Run test suite

2. **Editable Install Test:**
   - Install with `-e` flag
   - Make code change
   - Verify change is immediately available

3. **Dev Dependencies Test:**
   - Install with `.[dev]`
   - Verify pytest, mypy, ruff available

4. **Import Test:**
   ```python
   from ragnostic.db import DatabaseClient
   from ragnostic.ingestion.monitor import DirectoryMonitor
   # etc.
   ```

## Parallel Work Opportunities

Can be worked on **in parallel** with:
- Issue #02 (linting configuration)
- Issue #05 (logging infrastructure)

This is **required before**:
- Issue #01 (CI/CD needs installable package)
- Issue #06 (test organization needs working tests)
- Issue #08 (integration tests need working package)

## Platform-Specific Considerations

PyTorch installation varies by platform. Consider:

```toml
[project.optional-dependencies]
cuda = ["torch", "torchvision", "torchaudio"]  # CUDA version
cpu = ["torch", "torchvision", "torchaudio"]   # CPU-only
mps = ["torch", "torchvision", "torchaudio"]   # Apple Silicon
```

Document platform-specific installation in README.

## Migration Path

1. Keep `requirements.txt` initially for backwards compatibility
2. Add note that pyproject.toml is canonical source
3. Eventually remove requirements.txt or generate from pyproject.toml

## Notes

- Modern Python packaging uses `pyproject.toml` exclusively
- Consider using `pip-tools` to generate locked requirements
- May want to add version constraints (e.g., `"numpy>=1.24,<2.0"`)
- Check if any dependencies have minimum/maximum version requirements
- Ensure all dependencies are available on PyPI
