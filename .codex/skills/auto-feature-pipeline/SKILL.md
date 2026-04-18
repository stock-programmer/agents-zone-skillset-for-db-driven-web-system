---
name: auto-feature-pipeline
description: Orchestrate the repo's end-to-end feature delivery workflow from one requirement input: read AGENTS.md, generate PRD/architecture/story docs, delegate TDD Red to tester and TDD Green to coder subagents, run QC gates, and finish with Playwright UAT plus a final delivery report.
---

# Auto Feature Pipeline

Use this skill when the user wants the project workflow to run from a single requirement instead of manually triggering `prd`, `architect`, `story`, `tester`, `qc`, and `coder` step by step.

This skill is the orchestrator. It does not replace the existing project prompts. It coordinates them.

## What This Skill Controls

For one feature request, run this sequence:

1. Read `AGENTS.md`
2. Read `skills/prd.md`, `skills/architect.md`, `skills/story.md`, `skills/qc.md`
3. Create or load a request file in `docs/requests/`
4. Create or update run state in `docs/workflow-runs/`
5. Generate `docs/prd-{slug}.md`
6. Generate `docs/arch-{slug}.md`
7. Generate `docs/story-{slug}.md`
8. Delegate TDD Red to `agents/tester.md`
9. Run QC for `--phase=tester`
10. Delegate TDD Green to `agents/coder.md`
11. Run QC for `--phase=coder`
12. Run Playwright/browser UAT when the story touches UI flows
13. Produce a final completion or blocked report

## Inputs

Accept any of these:

- Raw requirement text from the user
- A feature title plus requirement text
- A request file in `docs/requests/{slug}.md`
- A run state file in `docs/workflow-runs/{slug}.json` for resume

If the user gives only raw text, derive:

- `title`
- `slug`
- `request_file`
- `run_state_file`

Prefer the slug already present in filenames if provided by the user.

## Required Repo Context

Read these files before orchestration:

- `AGENTS.md`
- `agents/tester.md`
- `agents/coder.md`
- `skills/prd.md`
- `skills/architect.md`
- `skills/story.md`
- `skills/qc.md`

Read existing artifacts when resuming:

- `docs/prd-{slug}.md`
- `docs/arch-{slug}.md`
- `docs/story-{slug}.md`
- `docs/workflow-runs/{slug}.json`

## State Management

Use `docs/workflow-runs/{slug}.json` as the machine-readable source of truth.

Each phase should contain:

- `status`: `pending`, `in_progress`, `passed`, `failed`, `blocked`, or `skipped`
- `started_at`
- `finished_at`
- `artifacts`
- `summary`

Always update state after each phase transition.

## Phase Rules

### Phase 1: Intake

- Ensure a request file exists in `docs/requests/{slug}.md`
- Ensure a run state file exists in `docs/workflow-runs/{slug}.json`
- If files already exist, resume instead of recreating

### Phase 2: PRD

- Follow `skills/prd.md`
- Ground the document in the current repo and `AGENTS.md`
- Save to `docs/prd-{slug}.md`

### Phase 3: Architecture

- Follow `skills/architect.md`
- Use the generated PRD plus current codebase conventions
- Save to `docs/arch-{slug}.md`

### Phase 4: Story

- Follow `skills/story.md`
- The story must be the single source of truth for tester and coder
- Save to `docs/story-{slug}.md`

### Phase 5: Tester (TDD Red)

- Spawn a subagent only because the user explicitly asked for subagent-based automation
- Hand off only the story path and the tester role expectations
- The tester must design tests from the story requirements first, then inspect code only as needed to implement the tests
- Require failing tests and capture the failing output

The tester handoff must include:

- story path
- requirement to cover ACs
- requirement to verify tests are failing
- requirement to report modified test files and failure output

### Phase 6: QC for Tester

- Follow `skills/qc.md` with `--phase=tester`
- Reject weak, fake, or circular tests
- If QC fails, loop back to Tester with the QC findings
- Limit retry loops to 3 unless the user says to keep going

### Phase 7: Coder (TDD Green)

- Spawn a subagent for `agents/coder.md`
- Provide story path plus the failing test files/output
- Require iterative implementation until tests pass or the work becomes blocked
- Require a report of changed files, test results, and definition-of-done status

### Phase 8: QC for Coder

- Follow `skills/qc.md` with `--phase=coder`
- Verify implementation claims against the actual code and actual tests
- If QC fails, loop back to Coder with the findings
- Limit retry loops to 3 unless the user says to keep going

### Phase 9: Browser UAT

Run browser UAT when the story changes user-visible flows.

Minimum expectations:

- start the required app services
- execute Playwright or the repo's browser test path
- capture the result in the run state

If the story is backend-only, mark UAT as `skipped` with a reason.

### Phase 10: Final Report

Report:

- final status
- generated docs
- tester outputs
- coder outputs
- QC outcomes
- UAT outcome
- blockers or follow-up items

## Subagent Guidance

When spawning subagents:

- tester owns test creation and red verification
- coder owns implementation and green verification
- do not ask tester to QC itself
- do not ask coder to QC itself
- keep write scopes clear in the prompt

## Retry and Exit Policy

- Retry Tester after failed tester-QC up to 3 times
- Retry Coder after failed coder-QC up to 3 times
- Stop early if a blocker is external, ambiguous, or destructive
- Mark the run `blocked` instead of pretending success

## Output Contract

At minimum, each completed run must leave behind:

- `docs/requests/{slug}.md`
- `docs/workflow-runs/{slug}.json`
- `docs/prd-{slug}.md`
- `docs/arch-{slug}.md`
- `docs/story-{slug}.md`

Optional artifacts:

- test reports
- Playwright outputs
- final delivery summary

## Invocation Examples

Examples that should trigger this skill:

- `执行 auto-feature-pipeline，需求标题是采购申请批量审批，需求内容是：...`
- `用自动编排跑完整 feature 流水线，request file 是 docs/requests/batch-approval.md`
- `继续 docs/workflow-runs/batch-approval.json 这次 run，从 tester qc 失败处恢复`

