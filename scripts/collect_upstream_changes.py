#!/usr/bin/env python3
"""Collect upstream documentation changes for manual translation tracking."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

UPSTREAM_REPO_DEFAULT = "Universal-Commerce-Protocol/ucp"
DEFAULT_STATE: dict[str, str] = {
  "last_synced_upstream_sha": "",
  "last_report_path": "",
  "generated_at": "",
}


def run_git(args: list[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
  result = subprocess.run(
    ["git", *args],
    cwd=cwd,
    capture_output=True,
    text=True,
    check=False,
  )
  if check and result.returncode != 0:
    cmd = "git " + " ".join(args)
    raise RuntimeError(f"{cmd} failed: {result.stderr.strip()}")
  return result


def git_output(args: list[str], cwd: Path) -> str:
  return run_git(args, cwd).stdout.strip()


def try_git_output(args: list[str], cwd: Path) -> str:
  result = run_git(args, cwd, check=False)
  if result.returncode != 0:
    return ""
  return result.stdout.strip()


def git_commit_exists(sha: str, cwd: Path) -> bool:
  result = run_git(["cat-file", "-e", f"{sha}^{{commit}}"], cwd, check=False)
  return result.returncode == 0


def load_state(path: Path) -> dict[str, str]:
  if not path.exists():
    return DEFAULT_STATE.copy()
  try:
    with path.open(encoding="utf-8") as f:
      data = json.load(f)
    return {
      "last_synced_upstream_sha": str(data.get("last_synced_upstream_sha", "")),
      "last_report_path": str(data.get("last_report_path", "")),
      "generated_at": str(data.get("generated_at", "")),
    }
  except (json.JSONDecodeError, OSError):
    return DEFAULT_STATE.copy()


def save_state(path: Path, state: dict[str, str]) -> None:
  path.parent.mkdir(parents=True, exist_ok=True)
  with path.open("w", encoding="utf-8") as f:
    json.dump(state, f, indent=2, ensure_ascii=False)
    f.write("\n")


def normalize_path(path: str) -> str:
  return path.replace("\\", "/")


def is_docs_markdown(path: str) -> bool:
  path = normalize_path(path)
  return path.startswith("docs/") and path.endswith(".md")


def is_structural_path(path: str) -> bool:
  path = normalize_path(path)
  return path in {"mkdocs.yml", "main.py", "hooks.py"} or path.startswith("source/")


def diffstat_for_paths(base_sha: str, head_sha: str, paths: list[str], cwd: Path) -> str:
  if not paths:
    return "+0/-0"
  result = run_git(
    ["diff", "-M", "--numstat", base_sha, head_sha, "--", *paths],
    cwd,
    check=False,
  )
  if result.returncode != 0:
    return "+0/-0"

  added = 0
  deleted = 0
  for line in result.stdout.splitlines():
    parts = line.split("\t")
    if len(parts) < 3:
      continue
    add_raw, del_raw = parts[0], parts[1]
    if add_raw.isdigit():
      added += int(add_raw)
    if del_raw.isdigit():
      deleted += int(del_raw)
  return f"+{added}/-{deleted}"


def last_commit_info(base_sha: str, head_sha: str, path: str, cwd: Path) -> dict[str, str]:
  fmt = "%H%x1f%cs%x1f%s"
  in_range = try_git_output(
    ["log", "-1", f"--format={fmt}", f"{base_sha}..{head_sha}", "--", path],
    cwd,
  )
  raw = in_range or try_git_output(
    ["log", "-1", f"--format={fmt}", head_sha, "--", path],
    cwd,
  )
  if not raw:
    return {
      "sha": head_sha,
      "date": "unknown",
      "subject": "(commit metadata unavailable)",
    }

  sha, date_raw, subject = raw.split("\x1f", 2)
  return {
    "sha": sha,
    "date": date_raw,
    "subject": subject,
  }


def sanitize(text: str) -> str:
  return text.replace("|", "\\|").strip()


def format_doc_item(
  action_label: str,
  path_label: str,
  meta: dict[str, str],
  diffstat: str,
  upstream_repo: str,
) -> str:
  sha = meta["sha"]
  sha_short = sha[:7]
  commit_url = f"https://github.com/{upstream_repo}/commit/{sha}"
  return (
    f"- [ ] {action_label} `{path_label}` | "
    f"커밋: [{sha_short}]({commit_url}) | "
    f"날짜: {meta['date']} | "
    f"메시지: {sanitize(meta['subject'])} | "
    f"diff: `{diffstat}`"
  )


def format_structural_item(
  status: str,
  path_label: str,
  meta: dict[str, str],
  diffstat: str,
  upstream_repo: str,
) -> str:
  sha = meta["sha"]
  sha_short = sha[:7]
  commit_url = f"https://github.com/{upstream_repo}/commit/{sha}"
  return (
    f"- [ ] 영향 검토 `{status} {path_label}` | "
    f"커밋: [{sha_short}]({commit_url}) | "
    f"날짜: {meta['date']} | "
    f"메시지: {sanitize(meta['subject'])} | "
    f"diff: `{diffstat}`"
  )


def ensure_unique_report_path(path: Path) -> Path:
  if not path.exists():
    return path
  stem = path.stem
  suffix = path.suffix
  parent = path.parent
  index = 1
  while True:
    candidate = parent / f"{stem}-{index}{suffix}"
    if not candidate.exists():
      return candidate
    index += 1


def update_index(index_path: Path, report_filename: str, display_time: str, range_text: str) -> None:
  entry = f"- [{display_time}]({report_filename}) `{range_text}`"

  existing_entries: list[str] = []
  if index_path.exists():
    try:
      with index_path.open(encoding="utf-8") as f:
        for line in f.read().splitlines():
          if line.startswith("- ["):
            existing_entries.append(line)
    except OSError:
      existing_entries = []

  deduped = [entry]
  deduped.extend(line for line in existing_entries if line != entry)

  content_lines = [
    "# Translation Update Reports",
    "",
    "원문(UCP) 문서 변경사항 자동 추적 보고서입니다.",
    "체크박스를 사용해 수동 번역 진행 상태를 관리하세요.",
    "",
    *deduped,
    "",
  ]
  index_path.parent.mkdir(parents=True, exist_ok=True)
  index_path.write_text("\n".join(content_lines), encoding="utf-8")


def parse_changes(base_sha: str, head_sha: str, cwd: Path) -> list[list[str]]:
  raw = git_output(["diff", "--name-status", "-M", base_sha, head_sha], cwd)
  rows: list[list[str]] = []
  for line in raw.splitlines():
    parts = line.split("\t")
    if not parts:
      continue
    rows.append(parts)
  return rows


def write_output(key: str, value: str) -> None:
  output_path = os.environ.get("GITHUB_OUTPUT")
  if output_path:
    with open(output_path, "a", encoding="utf-8") as f:
      f.write(f"{key}={value}\n")
  else:
    print(f"{key}={value}")


def build_report(
  now_utc: datetime,
  base_sha: str,
  head_sha: str,
  upstream_repo: str,
  new_docs: list[str],
  modified_docs: list[str],
  renamed_docs: list[tuple[str, str]],
  deleted_docs: list[str],
  structural: list[tuple[str, str, str | None]],
  cwd: Path,
) -> str:
  compare_url = f"https://github.com/{upstream_repo}/compare/{base_sha}...{head_sha}"
  generated_at = now_utc.strftime("%Y-%m-%d %H:%M:%S UTC")

  lines: list[str] = [
    "# Translation Update Report",
    "",
    f"- 생성 시각: {generated_at}",
    f"- 비교 범위: `{base_sha}..{head_sha}`",
    f"- 비교 링크: [Compare changes]({compare_url})",
    "- 기준 브랜치: `upstream/main`",
    "",
    "## 신규 문서",
  ]

  if new_docs:
    for path in sorted(set(new_docs)):
      meta = last_commit_info(base_sha, head_sha, path, cwd)
      diffstat = diffstat_for_paths(base_sha, head_sha, [path], cwd)
      lines.append(format_doc_item("번역", path, meta, diffstat, upstream_repo))
  else:
    lines.append("- 없음")

  lines.extend(["", "## 수정 문서"])
  if modified_docs:
    for path in sorted(set(modified_docs)):
      meta = last_commit_info(base_sha, head_sha, path, cwd)
      diffstat = diffstat_for_paths(base_sha, head_sha, [path], cwd)
      lines.append(format_doc_item("재번역", path, meta, diffstat, upstream_repo))
  else:
    lines.append("- 없음")

  lines.extend(["", "## 리네임 문서"])
  if renamed_docs:
    for old_path, new_path in sorted(set(renamed_docs)):
      path_label = f"{old_path} -> {new_path}"
      meta = last_commit_info(base_sha, head_sha, new_path, cwd)
      diffstat = diffstat_for_paths(base_sha, head_sha, [old_path, new_path], cwd)
      lines.append(
        format_doc_item("링크/앵커 점검", path_label, meta, diffstat, upstream_repo)
      )
  else:
    lines.append("- 없음")

  lines.extend([
    "",
    "## 원문 삭제 문서",
    "",
    "원문에서 삭제되어도 번역본은 보존 정책을 따릅니다.",
  ])
  if deleted_docs:
    for path in sorted(set(deleted_docs)):
      meta = last_commit_info(base_sha, head_sha, path, cwd)
      diffstat = diffstat_for_paths(base_sha, head_sha, [path], cwd)
      lines.append(format_doc_item("보존 검토", path, meta, diffstat, upstream_repo))
  else:
    lines.append("- 없음")

  lines.extend(["", "## 구조/로직 변경"])
  if structural:
    for status, primary, secondary in sorted(set(structural)):
      if secondary:
        path_label = f"{primary} -> {secondary}"
        path_for_log = secondary
        diffstat = diffstat_for_paths(base_sha, head_sha, [primary, secondary], cwd)
      else:
        path_label = primary
        path_for_log = primary
        diffstat = diffstat_for_paths(base_sha, head_sha, [primary], cwd)
      meta = last_commit_info(base_sha, head_sha, path_for_log, cwd)
      lines.append(
        format_structural_item(status, path_label, meta, diffstat, upstream_repo)
      )
  else:
    lines.append("- 없음")

  lines.append("")
  return "\n".join(lines)


def parse_args() -> argparse.Namespace:
  parser = argparse.ArgumentParser(
    description="Collect upstream docs changes and write a manual translation report.",
  )
  parser.add_argument(
    "--base-sha",
    default="",
    help="Base commit SHA for diff range (optional).",
  )
  parser.add_argument(
    "--head-sha",
    default="",
    help="Head commit SHA for diff range (optional; defaults to upstream/main).",
  )
  parser.add_argument(
    "--output-report",
    default="",
    help="Optional explicit output path for report file.",
  )
  parser.add_argument(
    "--state-file",
    default="translation_state/state.json",
    help="Path to state JSON file.",
  )
  parser.add_argument(
    "--upstream-repo",
    default=UPSTREAM_REPO_DEFAULT,
    help="GitHub owner/repo slug for upstream links.",
  )
  return parser.parse_args()


def main() -> int:
  args = parse_args()
  repo_root = Path.cwd()
  state_path = (repo_root / args.state_file).resolve()
  state = load_state(state_path)

  head_sha = args.head_sha or try_git_output(["rev-parse", "upstream/main"], repo_root)
  if not head_sha:
    print("Unable to resolve head SHA. Did you fetch upstream/main?", file=sys.stderr)
    return 1
  if not git_commit_exists(head_sha, repo_root):
    print(f"Head commit does not exist locally: {head_sha}", file=sys.stderr)
    return 1

  base_sha = args.base_sha or state.get("last_synced_upstream_sha", "")
  if not base_sha:
    base_sha = try_git_output(["rev-parse", f"{head_sha}^"], repo_root) or head_sha

  if not git_commit_exists(base_sha, repo_root):
    print(f"Base commit does not exist locally: {base_sha}", file=sys.stderr)
    return 1

  rows = parse_changes(base_sha, head_sha, repo_root)

  new_docs: list[str] = []
  modified_docs: list[str] = []
  renamed_docs: list[tuple[str, str]] = []
  deleted_docs: list[str] = []
  structural: list[tuple[str, str, str | None]] = []

  for parts in rows:
    status = parts[0]
    status_code = status[0]

    if status_code == "R" and len(parts) >= 3:
      old_path = normalize_path(parts[1])
      new_path = normalize_path(parts[2])

      old_is_doc = is_docs_markdown(old_path)
      new_is_doc = is_docs_markdown(new_path)

      if old_is_doc and new_is_doc:
        renamed_docs.append((old_path, new_path))
      elif old_is_doc and not new_is_doc:
        deleted_docs.append(old_path)
      elif not old_is_doc and new_is_doc:
        new_docs.append(new_path)

      if is_structural_path(old_path) or is_structural_path(new_path):
        structural.append((status, old_path, new_path))

      continue

    if len(parts) < 2:
      continue

    path = normalize_path(parts[1])
    if is_docs_markdown(path):
      if status_code == "A":
        new_docs.append(path)
      elif status_code == "M":
        modified_docs.append(path)
      elif status_code == "D":
        deleted_docs.append(path)

    if is_structural_path(path):
      structural.append((status, path, None))

  has_changes = any([
    new_docs,
    modified_docs,
    renamed_docs,
    deleted_docs,
    structural,
  ])

  now_utc = datetime.now(timezone.utc)
  branch_name = f"track/{now_utc.strftime('%Y%m%d-%H%M')}-{head_sha[:7]}"

  write_output("has_changes", "true" if has_changes else "false")
  write_output("base_sha", base_sha)
  write_output("head_sha", head_sha)
  write_output("base_sha_short", base_sha[:7])
  write_output("head_sha_short", head_sha[:7])
  write_output("branch_name", branch_name)

  if not has_changes:
    write_output("report_path", "")
    print("No documentation-impacting changes found in target paths.")
    return 0

  if args.output_report:
    report_path = Path(args.output_report)
    if not report_path.is_absolute():
      report_path = repo_root / report_path
  else:
    report_path = repo_root / "docs" / "translation-updates" / now_utc.strftime("%Y-%m-%d-%H%M.md")

  report_path = ensure_unique_report_path(report_path)
  report_rel = report_path.relative_to(repo_root).as_posix()

  report_body = build_report(
    now_utc=now_utc,
    base_sha=base_sha,
    head_sha=head_sha,
    upstream_repo=args.upstream_repo,
    new_docs=new_docs,
    modified_docs=modified_docs,
    renamed_docs=renamed_docs,
    deleted_docs=deleted_docs,
    structural=structural,
    cwd=repo_root,
  )

  report_path.parent.mkdir(parents=True, exist_ok=True)
  report_path.write_text(report_body, encoding="utf-8")

  index_path = repo_root / "docs" / "translation-updates" / "index.md"
  display_time = now_utc.strftime("%Y-%m-%d %H:%M UTC")
  update_index(
    index_path=index_path,
    report_filename=report_path.name,
    display_time=display_time,
    range_text=f"{base_sha[:7]}..{head_sha[:7]}",
  )

  state["last_synced_upstream_sha"] = head_sha
  state["last_report_path"] = report_rel
  state["generated_at"] = now_utc.isoformat().replace("+00:00", "Z")
  save_state(state_path, state)

  write_output("report_path", report_rel)
  print(f"Generated report: {report_rel}")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
