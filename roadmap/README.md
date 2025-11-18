# RAGnostic Project Roadmap

This roadmap provides a comprehensive development plan for the RAGnostic project, organized into 15 distinct issues across 5 development phases.

## Table of Contents

- [Overview](#overview)
- [Project Phases](#project-phases)
- [Issue Catalog](#issue-catalog)
- [Labels and Organization](#labels-and-organization)
- [Parallel Work Opportunities](#parallel-work-opportunities)
- [Creating GitHub Issues](#creating-github-issues)
- [Development Workflow](#development-workflow)
- [Estimated Timeline](#estimated-timeline)

---

## Overview

**Current State:** RAGnostic has a functional document ingestion pipeline (Phase 1 - partial) with excellent documentation and test coverage. The codebase is well-architected but lacks DevOps infrastructure and several key features.

**Goal:** Build a complete hierarchical RAG system for technical document processing with production-ready DevOps practices.

**Total Issues:** 15 (6 critical, 4 high, 3 medium, 2 low priority)

---

## Project Phases

### Phase 0: DevOps Setup (Issues #1-6)
**Duration:** 2-3 weeks
**Goal:** Establish development infrastructure and code quality standards

**Issues:**
- #01: CI/CD Pipeline with GitHub Actions
- #02: Linting and Formatting Configuration
- #03: Fix Package Installation
- #04: Pre-commit Hooks
- #05: Logging Infrastructure
- #06: Pytest Markers and Test Organization

**Why First:** These foundational issues enable efficient development for all subsequent phases.

### Phase 1: Complete Ingestion (Issues #7-11)
**Duration:** 3-4 weeks
**Goal:** Finish and polish the document ingestion pipeline

**Issues:**
- #07: Database Client Refactor
- #08: Integration Tests for Ingestion Flow
- #09: Cleanup on Success
- #10: Document Search Functionality
- #11: Add Original Filename Field

**Current Status:** Partially complete - basic ingestion works, needs refinement.

### Phase 2: Semantic Extraction (Issue #12)
**Duration:** 4-6 weeks
**Goal:** Extract semantic structure from documents

**Issues:**
- #12: Semantic Extraction (EPIC - break into sub-issues)
  - Section hierarchy detection
  - Image/table captioning with LLMs
  - Document summarization
  - Chunking strategies
  - Entity extraction

**Status:** Fully documented in `docs/2b_Semantic_Extraction.md`, not implemented.

### Phase 3: Vector Storage (Issue #13)
**Duration:** 3-4 weeks
**Goal:** Implement vector database for semantic search

**Issues:**
- #13: ChromaDB Integration and Embedding Pipeline

**Status:** Dependencies specified, architecture designed.

### Phase 4: Query Pipeline (Issue #14)
**Duration:** 3-4 weeks
**Goal:** Build two-tier retrieval and RAG query system

**Issues:**
- #14: Query Pipeline and Retrieval

**Status:** Fully documented in `docs/2_Ragnostic_Project_Plan.md`.

### Phase 5: Evaluation (Issue #15)
**Duration:** 2-3 weeks
**Goal:** Measure and optimize RAG quality

**Issues:**
- #15: Evaluation and Metrics Framework

**Status:** Planned but not detailed.

---

## Issue Catalog

| # | Title | Priority | Effort | Phase | Blocking Issues | Blocked By |
|---|-------|----------|--------|-------|----------------|------------|
| 01 | CI/CD Pipeline | Critical | 1-2d | 0 | #02, #03 | None |
| 02 | Linting Config | Critical | 1d | 0 | None | None |
| 03 | Fix Package Install | Critical | 0.5d | 0 | None | None |
| 04 | Pre-commit Hooks | High | 0.5d | 0 | #02, #03 | None |
| 05 | Logging Infrastructure | High | 1-2d | 0 | None | None |
| 06 | Pytest Markers | High | 0.5d | 0 | #03 | None |
| 07 | Database Refactor | Medium | 2-3d | 1 | #03, #06 | None |
| 08 | Integration Tests | High | 2-3d | 1 | #03, #06 | None |
| 09 | Cleanup on Success | Medium | 0.5-1d | 1 | #03, #05 | None |
| 10 | Document Search | Medium | 2-3d | 1 | #03 | None |
| 11 | Original Filename | Low | 0.5d | 1 | None | None |
| 12 | Semantic Extraction | Medium | 4-6w | 2 | #03, Phase 1 | None |
| 13 | Vector Storage | Low | 3-4w | 3 | #12 | None |
| 14 | Query Pipeline | Low | 3-4w | 4 | #13 | None |
| 15 | Evaluation Framework | Low | 2-3w | 5 | #14 | None |

### Issue Descriptions

#### Phase 0: DevOps Setup

**Issue #01: CI/CD Pipeline with GitHub Actions** [`critical`, `devops`, `ci/cd`]
- Setup automated testing, linting, and build validation
- Add GitHub Actions workflows for PR and main branch
- Blocked by: #02 (needs linting config), #03 (needs installable package)
- File: `issue-01-cicd-pipeline.md`

**Issue #02: Linting and Formatting Configuration** [`critical`, `code-quality`, `devops`]
- Configure ruff and mypy in pyproject.toml
- Add Makefile targets for lint, format, typecheck
- No dependencies - foundational task
- File: `issue-02-linting-formatting-config.md`

**Issue #03: Fix Package Installation** [`critical`, `bug`, `packaging`]
- Populate pyproject.toml dependencies
- Fix `ModuleNotFoundError` preventing tests from running
- No dependencies - foundational task
- File: `issue-03-fix-package-installation.md`

**Issue #04: Add Pre-commit Hooks** [`high`, `devops`, `code-quality`]
- Setup pre-commit framework with ruff, trailing whitespace checks
- Blocked by: #02 (needs linting config)
- File: `issue-04-pre-commit-hooks.md`

**Issue #05: Setup Logging Infrastructure** [`high`, `infrastructure`, `observability`]
- Create centralized logging configuration
- Add logging to all modules
- No dependencies - can work in parallel
- File: `issue-05-logging-infrastructure.md`

**Issue #06: Organize Tests with Pytest Markers** [`high`, `testing`, `developer-experience`]
- Add markers for fast/slow, unit/integration tests
- Create Makefile targets for different test suites
- Blocked by: #03 (tests must be runnable)
- File: `issue-06-pytest-markers.md`

#### Phase 1: Complete Ingestion

**Issue #07: Refactor Database Client Architecture** [`medium`, `refactoring`, `architecture`]
- Separate infrastructure, CRUD, and business logic layers
- Implement repository pattern
- Blocked by: #03, #06
- File: `issue-07-database-client-refactor.md`

**Issue #08: Add Integration Tests for Ingestion Flow** [`high`, `testing`, `integration`]
- Test complete workflow end-to-end
- Test error handling and edge cases
- Blocked by: #03, #06
- File: `issue-08-integration-tests.md`

**Issue #09: Add Cleanup on Success** [`medium`, `feature`, `ingestion`]
- Implement configurable cleanup strategies (keep/delete/archive)
- Clean up source files after successful ingestion
- Blocked by: #03, #05
- File: `issue-09-cleanup-on-success.md`

**Issue #10: Implement Document Search** [`medium`, `feature`, `search`]
- Create search service with keyword and metadata filtering
- Add CLI and programmatic API
- Blocked by: #03
- File: `issue-10-document-search.md`

**Issue #11: Add Original Filename Field** [`low`, `enhancement`, `database`]
- Add original_filename to database schema
- Track original names through ingestion
- No dependencies - independent change
- File: `issue-11-original-filename.md`

#### Phase 2: Semantic Extraction

**Issue #12: Implement Semantic Extraction (EPIC)** [`medium`, `feature`, `ml`, `epic`]
- Section hierarchy detection
- Image/table captioning with LLMs
- Document summarization
- Chunking strategies
- Entity extraction
- Break into 5 sub-issues
- Blocked by: #03, Phase 1 complete
- File: `issue-12-semantic-extraction.md`

#### Phase 3: Vector Storage

**Issue #13: Implement Vector Storage with ChromaDB** [`low`, `feature`, `vector-db`, `ml`]
- ChromaDB client and two-tier collections
- Embedding generation pipeline
- Vector search functionality
- Blocked by: #12 (needs summaries and chunks)
- File: `issue-13-vector-storage.md`

#### Phase 4: Query Pipeline

**Issue #14: Implement Query Pipeline** [`low`, `feature`, `rag`, `ml`]
- Two-tier retrieval (summary → chunks)
- Reranking by section coverage
- LLM integration for answers
- Blocked by: #13
- File: `issue-14-query-pipeline.md`

#### Phase 5: Evaluation

**Issue #15: Build Evaluation Framework** [`low`, `evaluation`, `metrics`]
- Retrieval metrics (Precision, Recall, MRR, NDCG)
- Answer quality metrics (faithfulness, relevance)
- Benchmarking and regression testing
- Blocked by: #14
- File: `issue-15-evaluation-framework.md`

---

## Labels and Organization

### Recommended GitHub Labels

#### Priority Labels
- `priority: critical` - Must be done first (Issues #1-3)
- `priority: high` - Important for Phase 0-1 (Issues #4-6, #8)
- `priority: medium` - Nice to have (Issues #7, #9-10, #12)
- `priority: low` - Future enhancements (Issues #11, #13-15)

#### Type Labels
- `type: bug` - Fixes (#3)
- `type: feature` - New functionality (#5, #9-10, #12-14)
- `type: enhancement` - Improvements (#11)
- `type: refactoring` - Code restructuring (#7)
- `type: testing` - Test infrastructure (#6, #8, #15)

#### Component Labels
- `component: devops` - Infrastructure (#1-4)
- `component: database` - Database changes (#7, #11)
- `component: ingestion` - Ingestion pipeline (#8-9)
- `component: search` - Search functionality (#10)
- `component: ml` - ML/AI features (#12-14)
- `component: evaluation` - Quality metrics (#15)

#### Specialty Labels
- `epic` - Large multi-issue work (#12)
- `infrastructure` - Foundation work (#1-2, #5)
- `code-quality` - Quality improvements (#2, #4, #6)
- `packaging` - Package management (#3)
- `architecture` - Design changes (#7)
- `documentation` - Needs docs (all issues)

#### Phase Labels
- `phase-0: devops` - Issues #1-6
- `phase-1: ingestion` - Issues #7-11
- `phase-2: semantic` - Issue #12
- `phase-3: vector` - Issue #13
- `phase-4: query` - Issue #14
- `phase-5: evaluation` - Issue #15

---

## Parallel Work Opportunities

### Maximum Parallelization Strategy

To minimize total development time, work on issues in parallel where possible:

#### Wave 1: Foundation (Week 1)
**Can work in parallel:**
- #02: Linting Config (1 day) → Developer A
- #03: Fix Package Install (0.5 day) → Developer B
- #05: Logging Infrastructure (1-2 days) → Developer C

**Why parallel:** No dependencies on each other

**Completion:** All 3 must complete before Wave 2

#### Wave 2: DevOps Completion (Week 1-2)
**Can work in parallel:**
- #01: CI/CD Pipeline (1-2 days) → Developer A
- #04: Pre-commit Hooks (0.5 day) → Developer B
- #06: Pytest Markers (0.5 day) → Developer C

**Dependencies:** All require Wave 1 complete

#### Wave 3: Phase 1 Features (Week 3-4)
**Can work in parallel:**
- #07: Database Refactor (2-3 days) → Developer A
- #08: Integration Tests (2-3 days) → Developer B
- #09: Cleanup on Success (0.5-1 day) → Developer C
- #10: Document Search (2-3 days) → Developer D
- #11: Original Filename (0.5 day) → Developer E

**Dependencies:** All require #03 complete, #07-#08 benefit from #06

**Note:** 5 developers can work simultaneously here!

#### Wave 4: Semantic Extraction (Week 5-10)
**Break #12 into sub-issues, work in parallel:**
- Sub-issue 12.1: Section Detection → Developer A
- Sub-issue 12.2: Image/Table Captioning → Developer B
- Sub-issue 12.3: Summarization → Developer C
- Sub-issue 12.4: Chunking → Developer A (after 12.1)
- Sub-issue 12.5: Entity Extraction → Developer D

**Dependencies:** Requires Phase 1 complete

#### Wave 5: Vector & Query (Week 11-16)
**Can work in parallel (partially):**
- #13: Vector Storage (weeks 11-14) → Developer A
- #14: Query Pipeline (weeks 14-16) → Developer A (after #13)
- #15: Evaluation Framework (weeks 14-16) → Developer B (in parallel with #14)

**Dependencies:** Sequential: #12 → #13 → #14, but #15 can overlap with #14

### Dependency Graph

```
Phase 0:
  Wave 1: [#02] [#03] [#05]  ← All parallel
            ↓     ↓     ↓
  Wave 2: [#01] [#04] [#06]  ← All parallel
            ↓     ↓     ↓
          Phase 0 Complete

Phase 1:
  Wave 3: [#07] [#08] [#09] [#10] [#11]  ← All parallel
                 ↓
          Phase 1 Complete

Phase 2:
  Wave 4: [#12.1] [#12.2] [#12.3]  ← Parallel
            ↓       ↓        ↓
          [#12.4] [#12.5]  ← Parallel
                 ↓
          Phase 2 Complete

Phase 3:
          [#13]  ← Sequential
            ↓
Phase 4:
          [#14]  ← Sequential
            ↓
Phase 5:
          [#15]  ← Can overlap with #14
```

### Critical Path Analysis

**Critical Path** (longest sequential dependency chain):
```
#03 → #06 → #08 → #12 → #13 → #14 → #15
```

**Estimated Critical Path Duration:**
- #03: 0.5 days
- #06: 0.5 days
- #08: 2.5 days
- #12: 6 weeks (30 days)
- #13: 4 weeks (20 days)
- #14: 4 weeks (20 days)
- #15: 3 weeks (15 days)

**Total Critical Path:** ~18.5 weeks (4.5 months)

**With Parallelization:** Can be reduced to ~15-17 weeks (4 months) with 3-5 developers

---

## Creating GitHub Issues

### Automated Approach (Recommended)

Use GitHub CLI to create issues from markdown files:

```bash
# Install GitHub CLI if needed
# brew install gh  # macOS
# apt install gh   # Ubuntu

# Authenticate
gh auth login

# Create all issues
for file in roadmap/issue-*.md; do
  # Extract issue number and title
  issue_num=$(basename "$file" .md | cut -d'-' -f2)
  title=$(grep "^# " "$file" | head -1 | sed 's/^# //')

  # Extract labels from markdown
  labels=$(grep "Labels:" "$file" | sed 's/\*\*Labels:\*\* //' | sed 's/`//g')

  # Create issue
  gh issue create \
    --title "$title" \
    --body-file "$file" \
    --label "$labels"

  echo "Created issue #$issue_num: $title"
done
```

### Manual Approach

For each issue file in `roadmap/`:

1. **Go to GitHub Issues:** Navigate to repository → Issues → New Issue

2. **Set Title:** Copy the title from markdown (without the `# Issue XX:` prefix)
   - Example: "Setup CI/CD Pipeline with GitHub Actions"

3. **Set Body:** Copy the entire markdown file content

4. **Add Labels:** Apply labels as specified in each issue's "Labels" field
   - Example: `devops`, `infrastructure`, `ci/cd`

5. **Set Priority:** Add priority label based on "Priority" field

6. **Set Phase:** Add phase label (e.g., `phase-0: devops`)

7. **Assign (Optional):** Assign to team members if known

8. **Set Milestone (Optional):** Group by phase
   - Milestone 1: "Phase 0 - DevOps Setup"
   - Milestone 2: "Phase 1 - Complete Ingestion"
   - etc.

### Issue Template

```markdown
**Priority:** [Critical|High|Medium|Low]
**Estimated Effort:** [X days/weeks]
**Labels:** [comma-separated]
**Phase:** [0-5]

## Problem Statement
[Description of what needs to be fixed/built]

## Current State
[What exists today]

## Proposed Solution
[Detailed solution with code examples]

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
...

## Dependencies
**Required before:**
- Issue #X

**Blocks:**
- Issue #Y

## Parallel Work Opportunities
[What can be done simultaneously]

## Notes
[Additional context]
```

### GitHub Projects Board (Optional)

Create a project board to track progress:

**Columns:**
1. **Backlog** - Not started
2. **Ready** - Dependencies met, can start
3. **In Progress** - Currently being worked on
4. **In Review** - PR open
5. **Done** - Merged

**Views:**
- By Phase (group by phase label)
- By Priority (sort by priority)
- By Assignee (group by developer)
- Critical Path (filter critical path issues)

---

## Development Workflow

### Recommended Process

1. **Start with Phase 0** - Complete all DevOps issues (#1-6) first
   - This establishes quality gates and efficient workflow
   - Makes all subsequent development faster and safer

2. **Use Feature Branches** - One branch per issue
   ```bash
   git checkout -b issue-03-fix-package-install
   # Make changes
   git commit -m "Fix package installation (#3)"
   git push origin issue-03-fix-package-install
   # Create PR linking to issue
   ```

3. **Link PRs to Issues**
   ```markdown
   Closes #3

   ## Changes
   - Populated pyproject.toml dependencies
   - Moved requirements to pyproject.toml
   - Updated installation docs

   ## Testing
   - Verified `pip install -e .` works
   - All tests pass
   ```

4. **Use Draft PRs** - Create draft PRs early for visibility

5. **Code Review** - All PRs reviewed before merge

6. **Merge Strategy** - Squash and merge (clean history)

### Branch Protection

Configure branch protection for `main`:
- Require PR reviews (1+ approvals)
- Require status checks (CI/CD must pass)
- Require branches to be up to date
- No direct pushes to main

### Milestones

Create milestones for each phase:
- **Phase 0 Complete:** Issues #1-6 closed
- **Phase 1 Complete:** Issues #7-11 closed
- **Phase 2 Complete:** Issue #12 closed
- **Phase 3 Complete:** Issue #13 closed
- **Phase 4 Complete:** Issue #14 closed
- **Phase 5 Complete:** Issue #15 closed

---

## Estimated Timeline

### With 1 Developer (Sequential)

| Phase | Duration | Cumulative |
|-------|----------|------------|
| Phase 0 | 2-3 weeks | 3 weeks |
| Phase 1 | 3-4 weeks | 7 weeks |
| Phase 2 | 4-6 weeks | 13 weeks |
| Phase 3 | 3-4 weeks | 17 weeks |
| Phase 4 | 3-4 weeks | 21 weeks |
| Phase 5 | 2-3 weeks | 24 weeks |

**Total:** ~24 weeks (6 months)

### With 3-5 Developers (Parallel)

| Phase | Duration | Cumulative | Notes |
|-------|----------|------------|-------|
| Phase 0 | 1-2 weeks | 2 weeks | 3 parallel workstreams |
| Phase 1 | 2-3 weeks | 5 weeks | 5 parallel workstreams |
| Phase 2 | 4-6 weeks | 11 weeks | 3-4 parallel workstreams |
| Phase 3 | 3-4 weeks | 15 weeks | Sequential |
| Phase 4 | 3-4 weeks | 19 weeks | Sequential, partial overlap with Phase 5 |
| Phase 5 | 2-3 weeks | 20 weeks | Overlaps with Phase 4 |

**Total:** ~20 weeks (5 months) with efficient parallelization

### Quick Start (MVP)

To get a working system quickly:

**Minimum Viable Product (4-6 weeks):**
1. Issues #2-3 (linting + package) - 1.5 days
2. Issue #6 (pytest markers) - 0.5 day
3. Issues #8-10 (integration tests + search) - 1 week
4. Issue #12 (simplified semantic extraction) - 3 weeks
5. Issue #13 (basic vector storage) - 2 weeks
6. Issue #14 (simple query pipeline) - 2 weeks

**Result:** Basic RAG system working, without full DevOps infrastructure

---

## Success Metrics

### Phase 0 Success Criteria
- [ ] CI/CD pipeline runs on every PR
- [ ] All tests pass automatically
- [ ] Code coverage >80%
- [ ] Linting passes with zero errors
- [ ] Pre-commit hooks prevent bad commits
- [ ] Fast tests run in <10 seconds

### Phase 1 Success Criteria
- [ ] Documents ingested end-to-end
- [ ] Integration tests cover full pipeline
- [ ] Search by title/keywords works
- [ ] Source files cleaned up after ingestion
- [ ] Database architecture clean and testable

### Phase 2 Success Criteria
- [ ] Document sections extracted
- [ ] Images and tables captioned
- [ ] Document summaries generated
- [ ] Documents chunked for retrieval
- [ ] Processing <5 min per document

### Phase 3 Success Criteria
- [ ] Embeddings generated for all documents
- [ ] Vector search returns relevant results
- [ ] Two-tier collections populated
- [ ] Search latency <1 second

### Phase 4 Success Criteria
- [ ] Questions answered with context
- [ ] Two-tier retrieval working
- [ ] CLI and API functional
- [ ] Multiple LLM providers supported
- [ ] End-to-end latency <5 seconds

### Phase 5 Success Criteria
- [ ] Retrieval metrics >0.7 across board
- [ ] Answer quality validated
- [ ] Regression tests prevent quality loss
- [ ] Performance benchmarked

---

## Additional Resources

### Documentation
- `docs/1_System_Requirements.md` - System overview
- `docs/2_Ragnostic_Project_Plan.md` - Complete project plan
- `docs/2a_Document_Ingestion.md` - Phase 1 details
- `docs/2b_Semantic_Extraction.md` - Phase 2 details

### Code
- `src/ragnostic/` - Main source code
- `tests/` - Test suite
- `notebooks/` - Exploration notebooks

### Community
- GitHub Issues - Questions and discussion
- PRs - Code review and collaboration

---

## Questions?

For questions about this roadmap:
1. Open a GitHub Discussion
2. Reference specific issue numbers
3. Tag with `roadmap` label

Happy building! 🚀
