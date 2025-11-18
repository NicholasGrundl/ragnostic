# Issue 01: Setup CI/CD Pipeline with GitHub Actions

**Priority:** Critical
**Estimated Effort:** 1-2 days
**Labels:** `devops`, `infrastructure`, `ci/cd`
**Phase:** 0 - DevOps Setup

## Problem Statement

The project currently has no automated testing, linting, or build validation. This creates risks:
- Code quality issues may be merged undetected
- Breaking changes can reach main branch
- No automated test execution on PRs
- Manual testing is error-prone and time-consuming

## Current State

- No `.github/workflows/` directory exists
- Tests exist but run manually only
- No automated quality checks
- No build verification

## Proposed Solution

Create GitHub Actions workflows to automate:

1. **Pull Request Workflow** (`.github/workflows/pr.yml`):
   - Run tests with pytest
   - Execute linting with ruff
   - Run type checking with mypy
   - Generate coverage reports
   - Validate package builds

2. **Main Branch Workflow** (`.github/workflows/main.yml`):
   - Run full test suite
   - Build and publish package (if applicable)
   - Generate documentation

## Acceptance Criteria

- [ ] GitHub Actions workflow file created
- [ ] Automated tests run on every PR
- [ ] Linting checks pass before merge
- [ ] Type checking validates code
- [ ] Coverage reports generated and uploaded
- [ ] Build process validates successfully
- [ ] Badge added to README showing build status

## Implementation Steps

1. Create `.github/workflows/` directory
2. Add `pr.yml` workflow with jobs for:
   - Setup Python 3.11
   - Install dependencies
   - Run pytest with coverage
   - Run ruff check
   - Run mypy
3. Add `main.yml` for main branch automation
4. Configure workflow permissions
5. Test workflow with a PR
6. Add status badges to README

## Dependencies

- Issue #02 (linting config must exist first)
- Python 3.11 available in GitHub Actions runners
- Package must be installable (Issue #03)

## Testing Strategy

- Create a test PR to verify workflow runs
- Intentionally introduce lint error to verify failure
- Verify coverage reporting works
- Check badge displays correctly

## Parallel Work Opportunities

Can be worked on **in parallel** with:
- Issue #04 (pre-commit hooks)
- Issue #05 (logging infrastructure)
- Issue #06 (pytest markers)

Must be worked **after**:
- Issue #02 (linting configuration)
- Issue #03 (package installation)

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Python testing with GitHub Actions](https://docs.github.com/en/actions/automating-builds-and-tests/building-and-testing-python)
- [pytest-cov for coverage](https://pytest-cov.readthedocs.io/)

## Notes

- Consider caching pip dependencies for faster runs
- Set up branch protection rules after workflow is working
- May want separate workflows for fast/slow tests
