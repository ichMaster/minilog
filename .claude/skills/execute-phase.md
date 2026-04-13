---
name: execute-phase
description: Execute a project phase — implement all issues one by one with validation, testing, committing, pushing, and closing
user_invocable: true
arguments:
  - name: phase
    description: "Phase number (1-8) to execute"
    required: true
allowed_tools:
  # Filesystem
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  # Shell
  - Bash
  # Task tracking
  - TodoWrite
  # GitHub MCP
  - mcp__github-mcp__list_issues
  - mcp__github-mcp__get_issue
  - mcp__github-mcp__update_issue
  - mcp__github-mcp__add_issue_comment
  - mcp__github-mcp__search_issues
  - mcp__github-mcp__create_branch
  - mcp__github-mcp__create_or_update_file
  - mcp__github-mcp__get_file_contents
  - mcp__github-mcp__push_files
  - mcp__github-mcp__list_commits
  - mcp__github-mcp__search_code
---

# Execute Phase Skill

Execute all GitHub issues in the specified phase sequentially. Each issue is implemented, validated, tested, fixed, committed, pushed, and closed before moving to the next.

## Phase-to-label mapping

| Phase | Label | Issues |
|-------|-------|--------|
| 1 | phase-1-foundation | #1, #2, #3 |
| 2 | phase-2-lexer-parser | #4, #5 |
| 3 | phase-3-core-logic | #6, #7, #8 |
| 4 | phase-4-engine | #9 |
| 5 | phase-5-advanced-engines | #10, #11, #12 |
| 6 | phase-6-frontend | #13 |
| 7 | phase-7-examples | #14, #15, #16 |
| 8 | phase-8-documentation | #17 |

## Procedure

### 1. Discover issues

Fetch all open issues for the phase using the GitHub MCP tool `list_issues` with label filter `phase-{N}-*` from `ichMaster/minilog`. Sort by issue number ascending. If all issues in the phase are already closed, report that and stop.

### 2. Set up task tracking

Create a TodoWrite task list with all phase issues. Mark the first open one as `in_progress`, the rest as `pending`.

### 3. For each issue (in order):

#### 3a. Read the spec

Read the issue body from GitHub to get the description and acceptance criteria. Also read the corresponding task section from `specification/minilog-stage1-spec.md` (section 10) for the full specification including file list, dependencies, and detailed requirements.

#### 3b. Implement

- Read any existing source files that the new code depends on
- Create or modify the files listed in the task specification
- Follow the data models and algorithms from the spec exactly
- Follow all conventions from CLAUDE.md (type hints, English code, Ukrainian `.ml` syntax)

#### 3c. Validate acceptance criteria

For each acceptance criterion in the issue:
- Run the specific check (e.g., run a Python snippet, invoke CLI command)
- Use `.venv/bin/python` and `.venv/bin/pytest` directly (not `source .venv/bin/activate`)
- If a criterion fails, fix the code and re-validate

#### 3d. Run tests

```bash
.venv/bin/pytest tests/unit/<test_file>.py -v    # run the new tests
.venv/bin/pytest -v                               # run full suite for regressions
```

If any test fails:
1. Read the error message carefully
2. Fix the code (not the test, unless the test itself has a bug)
3. Re-run until all tests pass

#### 3e. Commit

```bash
git add <specific files>
git commit -m "$(cat <<'EOF'
MINILOG-NNN: <title> — <short description>

<1-2 sentence summary of what was implemented>

Closes #<issue_number>

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

#### 3f. Push and close

```bash
git push origin main
```

The `Closes #N` in the commit message auto-closes the issue on push. Verify the issue is closed via GitHub MCP.

#### 3g. Update tracking

Mark the completed issue as `completed` in TodoWrite. Mark the next issue as `in_progress`.

### 4. Generate phase report

After all issues are complete, output a summary report:

```
## Phase N Complete

| Issue | Title | Tests | Status |
|-------|-------|-------|--------|
| #N | MINILOG-NNN: Title | X tests | Closed |
| ... | ... | ... | ... |

**Total tests:** X (all passing)
**Commits:** list of commit hashes
```

Also run the full test suite one final time with coverage:

```bash
.venv/bin/pytest --cov=minilog --cov-report=term-missing
```

Include the coverage summary in the report.
