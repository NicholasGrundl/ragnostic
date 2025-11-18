# Issue 04: Add Pre-commit Hooks for Code Quality

**Priority:** High
**Estimated Effort:** 0.5 days
**Labels:** `devops`, `code-quality`, `developer-experience`
**Phase:** 0 - DevOps Setup

## Problem Statement

Code quality checks only run manually or in CI/CD (after pushing). This leads to:
- Quality issues discovered late in development cycle
- Failed CI/CD builds after pushing
- Wasted time fixing issues that could be caught locally
- Inconsistent code formatting between commits

## Current State

- No `.pre-commit-config.yaml` file
- No automated checks before commit
- Developers must remember to run linting/formatting manually
- Quality issues only caught during code review or CI/CD

## Proposed Solution

Implement pre-commit hooks using the `pre-commit` framework to automatically:
- Format code with ruff
- Check linting with ruff
- Validate types with mypy (optional, can be slow)
- Check for common issues (trailing whitespace, merge conflicts, etc.)

### Configuration (.pre-commit-config.yaml)

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: ['--maxkb=5000']
      - id: check-merge-conflict
      - id: check-toml
      - id: debug-statements

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format

  # Optional: mypy (can be slow, consider CI-only)
  # - repo: https://github.com/pre-commit/mirrors-mypy
  #   rev: v1.8.0
  #   hooks:
  #     - id: mypy
  #       additional_dependencies: [types-all]
```

## Acceptance Criteria

- [ ] `.pre-commit-config.yaml` created with appropriate hooks
- [ ] `pre-commit` added to `requirements-dev.txt`
- [ ] Hooks installed locally with `pre-commit install`
- [ ] Documentation added to README
- [ ] All hooks pass on current codebase
- [ ] Makefile target added for running hooks manually
- [ ] Team can bypass hooks with `--no-verify` if needed (documented)

## Implementation Steps

1. **Add pre-commit to dev dependencies:**
   ```toml
   [project.optional-dependencies]
   dev = [
       "pre-commit",
       # ... other dev deps
   ]
   ```

2. **Create `.pre-commit-config.yaml`** with hooks listed above

3. **Install hooks:**
   ```bash
   pip install pre-commit
   pre-commit install
   ```

4. **Run on all files initially:**
   ```bash
   pre-commit run --all-files
   ```

5. **Fix any issues found**

6. **Add Makefile target:**
   ```makefile
   .PHONY: pre-commit-install pre-commit-run

   pre-commit-install:
       pre-commit install

   pre-commit-run:
       pre-commit run --all-files
   ```

7. **Update README:**
   ```markdown
   ## Development Setup

   Install pre-commit hooks:
   ```bash
   make pre-commit-install
   ```

   Run hooks manually:
   ```bash
   make pre-commit-run
   ```

   Bypass hooks (use sparingly):
   ```bash
   git commit --no-verify
   ```
   ```

## Dependencies

**Required before starting:**
- Issue #02 (ruff/mypy configuration must exist)
- Issue #03 (package must be installable)

**Blocks:**
- Better developer experience for all future development

## Testing Strategy

1. **Installation Test:**
   - Install hooks in fresh clone
   - Verify hooks are registered in `.git/hooks/`

2. **Functionality Test:**
   - Make a file with trailing whitespace
   - Attempt to commit
   - Verify hook fixes the issue automatically
   - Verify commit proceeds

3. **Bypass Test:**
   - Intentionally create lint error
   - Commit with `--no-verify`
   - Verify commit succeeds (but document this is for emergencies only)

4. **Performance Test:**
   - Time pre-commit on typical changes
   - If >5 seconds, consider making mypy CI-only

## Parallel Work Opportunities

Can be worked on **in parallel** with:
- Issue #01 (CI/CD pipeline)
- Issue #05 (logging infrastructure)
- Issue #06 (pytest markers)

Must be worked **after**:
- Issue #02 (needs linting configs)
- Issue #03 (needs installable package)

## Configuration Tuning

### Fast vs. Thorough Trade-off

**Fast (recommended for pre-commit):**
- Ruff format and check
- Basic file checks
- Skip mypy (run in CI only)

**Thorough (can be slow):**
- Include mypy
- Run tests (too slow for pre-commit)
- Complex linting rules

### Selective Hook Execution

Developers can run specific hooks:
```bash
pre-commit run ruff --all-files
pre-commit run trailing-whitespace --files src/module.py
```

## Notes

- Hooks run only on staged files by default (fast)
- Use `--all-files` flag to run on entire codebase
- Hooks can be updated with `pre-commit autoupdate`
- Consider adding hook to check for secrets/API keys
- Pre-commit cache is stored in `~/.cache/pre-commit`
- Can set `fail_fast: true` to stop on first failure
- Consider adding `pytest-fast` hook for unit tests only (not integration)
