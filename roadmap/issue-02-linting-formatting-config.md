# Issue 02: Configure Linting and Formatting Tools

**Priority:** Critical
**Estimated Effort:** 1 day
**Labels:** `code-quality`, `devops`, `configuration`
**Phase:** 0 - DevOps Setup

## Problem Statement

The project has `ruff` and `mypy` in `requirements-dev.txt` but:
- No `ruff` configuration exists
- No `mypy` configuration exists
- No consistent code style enforcement
- Type hints exist but aren't validated
- No automated formatting

## Current State

- `ruff` specified in requirements-dev.txt but not configured
- `mypy` specified in requirements-dev.txt but not configured
- No `.editorconfig` for editor consistency
- Type hints used throughout codebase but not checked
- Inconsistent code style possible

## Proposed Solution

Add comprehensive linting and formatting configuration to `pyproject.toml`:

### Ruff Configuration
```toml
[tool.ruff]
line-length = 100
target-version = "py311"
exclude = ["data/", "*.ipynb"]

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "N",   # pep8-naming
    "UP",  # pyupgrade
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
]
ignore = []

[tool.ruff.lint.isort]
known-first-party = ["ragnostic"]
```

### Mypy Configuration
```toml
[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false  # Start lenient, gradually stricten
exclude = ["data/", "notebooks/"]

[[tool.mypy.overrides]]
module = ["docling.*", "marker.*", "burr.*"]
ignore_missing_imports = true
```

## Acceptance Criteria

- [ ] Ruff configuration added to `pyproject.toml`
- [ ] Mypy configuration added to `pyproject.toml`
- [ ] `.editorconfig` created for editor consistency
- [ ] Makefile targets added for `make lint`, `make format`, `make typecheck`
- [ ] All existing code passes ruff checks (or issues filed for violations)
- [ ] Mypy runs successfully on codebase
- [ ] Documentation updated with linting instructions

## Implementation Steps

1. Add `[tool.ruff]` section to `pyproject.toml`
2. Add `[tool.mypy]` section to `pyproject.toml`
3. Create `.editorconfig` with basic settings
4. Add Makefile targets:
   ```makefile
   .PHONY: lint format typecheck

   lint:
       ruff check src/ tests/

   format:
       ruff format src/ tests/

   typecheck:
       mypy src/
   ```
5. Run `make lint` and fix any critical issues
6. Run `make typecheck` and add ignores for external libraries
7. Update README with usage instructions

## Dependencies

None - this is a foundational task

## Testing Strategy

- Run `ruff check` on entire codebase
- Run `ruff format --check` to verify formatting
- Run `mypy` on src directory
- Verify all tools complete without critical errors
- Test in clean virtual environment

## Parallel Work Opportunities

Can be worked on **in parallel** with:
- Issue #03 (package installation)
- Issue #04 (pre-commit hooks) - though hooks depend on this config
- Issue #05 (logging infrastructure)

This is **required before**:
- Issue #01 (CI/CD uses these tools)
- Issue #04 (pre-commit hooks use these configs)

## Auto-fix Recommendations

When implementing, consider:
- Use `ruff check --fix` for auto-fixable issues
- Use `ruff format` to auto-format code
- Address import sorting automatically with ruff

## Notes

- Start with lenient rules, gradually increase strictness
- Consider adding `pylint` or `bandit` for security checks in future
- Ruff replaces need for: isort, black, flake8, pyupgrade
- May need to add `# type: ignore` comments for some mypy issues
- Consider adding `ruff` format check to pre-commit hooks
