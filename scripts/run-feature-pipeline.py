from __future__ import annotations

import argparse
import json
import re
from collections import OrderedDict
from datetime import datetime
from pathlib import Path
from typing import Any


def make_slug(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not normalized:
        return f"feature-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    return normalized


def read_request_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def ensure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def build_request_body(
    title: str,
    slug: str,
    requested_at: str,
    requested_by: str,
    requirement: str,
) -> str:
    return f"""# Feature Request

## Metadata

- Title: {title}
- Slug: {slug}
- Requested At: {requested_at}
- Requested By: {requested_by}
- Source: bootstrap-script

## Business Context

- Target role:
- Target stage in end-to-end flow:
- Upstream dependency:
- Downstream handoff:

## Requirement

{requirement}

## Constraints

- In scope:
- Out of scope:
- Database change allowed:
- Frontend impact:
- Backend impact:
- UAT required:

## Completion Expectation

- Expected outputs: PRD, architecture, story, TDD Red, tester QC, TDD Green, coder QC, browser UAT, final report
- Done when: all required phases pass or the run is explicitly marked blocked with concrete reasons
"""


def build_run_state(title: str, slug: str, requested_at: str, requested_by: str) -> OrderedDict[str, Any]:
    return OrderedDict(
        [
            ("title", title),
            ("slug", slug),
            ("requested_at", requested_at),
            ("requested_by", requested_by),
            ("request_file", f"docs/requests/{slug}.md"),
            (
                "artifacts",
                OrderedDict(
                    [
                        ("prd", f"docs/prd-{slug}.md"),
                        ("architecture", f"docs/arch-{slug}.md"),
                        ("story", f"docs/story-{slug}.md"),
                        ("tester_report", f"docs/workflow-runs/{slug}.tester.md"),
                        ("tester_qc_report", f"docs/workflow-runs/{slug}.tester-qc.md"),
                        ("coder_report", f"docs/workflow-runs/{slug}.coder.md"),
                        ("coder_qc_report", f"docs/workflow-runs/{slug}.coder-qc.md"),
                        ("uat_report", f"docs/workflow-runs/{slug}.uat.md"),
                        ("final_report", f"docs/workflow-runs/{slug}.final.md"),
                    ]
                ),
            ),
            (
                "phases",
                OrderedDict(
                    [
                        (
                            "intake",
                            OrderedDict(
                                [
                                    ("status", "passed"),
                                    ("started_at", requested_at),
                                    ("finished_at", requested_at),
                                    ("artifacts", [f"docs/requests/{slug}.md"]),
                                    ("summary", "Request bootstrap completed."),
                                ]
                            ),
                        ),
                        ("prd", phase_stub()),
                        ("architecture", phase_stub()),
                        ("story", phase_stub()),
                        ("tester", phase_stub()),
                        ("tester_qc", phase_stub()),
                        ("coder", phase_stub()),
                        ("coder_qc", phase_stub()),
                        ("uat", phase_stub()),
                        ("final_report", phase_stub()),
                    ]
                ),
            ),
        ]
    )


def phase_stub() -> OrderedDict[str, Any]:
    return OrderedDict(
        [
            ("status", "pending"),
            ("started_at", None),
            ("finished_at", None),
            ("artifacts", []),
            ("summary", ""),
        ]
    )


def build_prompt(repo_root: Path, slug: str) -> str:
    return f"""Execute the auto-feature-pipeline skill for this repository.

Repository root: {repo_root}
Request file: docs/requests/{slug}.md
Run state file: docs/workflow-runs/{slug}.json

Requirements:

1. Read AGENTS.md, agents/tester.md, agents/coder.md, and all project workflow skills under skills/.
2. Generate:
   - docs/prd-{slug}.md
   - docs/arch-{slug}.md
   - docs/story-{slug}.md
3. Use the tester subagent for TDD Red based on docs/story-{slug}.md.
4. Run QC for tester using the project QC workflow.
5. Use the coder subagent for TDD Green based on docs/story-{slug}.md and the failing tests.
6. Run QC for coder using the project QC workflow.
7. Run Playwright/browser UAT if the story affects UI flows; otherwise mark UAT skipped with a reason.
8. Update docs/workflow-runs/{slug}.json after every phase.
9. Leave a final report in docs/workflow-runs/{slug}.final.md.

Stop only when the run is passed, blocked, or failed with a concrete blocker report.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare a feature pipeline run.")
    parser.add_argument("--title")
    parser.add_argument("--requirement")
    parser.add_argument("--request-file")
    parser.add_argument("--slug")
    parser.add_argument("--requested-by", default="codex-user")
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    docs_root = repo_root / "docs"
    requests_dir = docs_root / "requests"
    runs_dir = docs_root / "workflow-runs"

    ensure_directory(requests_dir)
    ensure_directory(runs_dir)

    title = args.title
    requirement = args.requirement
    slug = args.slug

    if args.request_file:
        request_file = Path(args.request_file).resolve()
        request_content = read_request_file(request_file)
        if not slug:
            slug = request_file.stem
        if not title:
            title = slug
        if not requirement:
            requirement = request_content

    if not requirement:
        raise SystemExit("Provide --requirement or --request-file.")
    if not title:
        raise SystemExit("Provide --title or --request-file.")
    if not slug:
        slug = make_slug(title)

    request_path = requests_dir / f"{slug}.md"
    run_state_path = runs_dir / f"{slug}.json"
    prompt_path = runs_dir / f"{slug}.prompt.md"
    requested_at = datetime.now().astimezone().isoformat(timespec="seconds")

    if request_path.exists() and not args.force:
        raise SystemExit(f"Request file already exists: {request_path}. Use --force to overwrite.")
    if run_state_path.exists() and not args.force:
        raise SystemExit(f"Run state already exists: {run_state_path}. Use --force to overwrite.")

    request_body = build_request_body(title, slug, requested_at, args.requested_by, requirement)
    run_state = build_run_state(title, slug, requested_at, args.requested_by)
    prompt_body = build_prompt(repo_root, slug)

    request_path.write_text(request_body, encoding="utf-8")
    run_state_path.write_text(json.dumps(run_state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    prompt_path.write_text(prompt_body, encoding="utf-8")

    print("Prepared feature pipeline run.")
    print(f"Request: {request_path}")
    print(f"Run state: {run_state_path}")
    print(f"Prompt: {prompt_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
