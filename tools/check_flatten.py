"""Validate the flattened project against Zensical's built-in checker.

Zensical reports every unresolved internal link and anchor during a build.
This tool builds the project, normalises each reported issue to a stable
`<type> @ <file>:<line>:<col>` key, and diffs that set against a committed
baseline of issues already known to exist in the source corpus
(known-issues.txt). The flatten is faithful when the build introduces no
issue outside that baseline.

The gate is deliberately hard to pass by accident. Zensical's diagnostic
format is not a stability contract (the tool is pinned), so a build that
crashes, or a future version that reshapes its output, would otherwise yield
an empty issue set that trivially satisfies any baseline. Two guards prevent
that silent pass: a non-zero build exit fails outright, and the count of
parsed diagnostics must equal the checker's own "N issues found" summary.

Forward-looking by design: the only engine it consults is Zensical. It does
not build or diff against MkDocs, and carries no fallback path.
"""

import argparse
import re
import subprocess
import sys
from collections import namedtuple
from pathlib import Path

# Strips SGR colour sequences from Zensical's diagnostic output.
_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")

# The box header that opens each diagnostic carries the location:
#   ╭─[ <file>:<line>:<col> ]
_LOCATION_RE = re.compile(r"╭─\[\s*(.+?)\s*\]")

# Each diagnostic opens with a severity line naming the issue. Zensical uses
# Warning today; Error is matched too so a severity change cannot hide a
# diagnostic (the count guard is the backstop if the wording changes further).
_SEVERITY_RE = re.compile(r"^\s*(?:Warning|Error):\s+(.*\S)\s*$")

# The build's own tally, e.g. "28 issues found" or "No issues found".
_COUNT_RE = re.compile(r"(?:(\d+)\s+issues?\s+found|(No)\s+issues?\s+found)")

REPO_ROOT = Path(__file__).resolve().parent.parent
PROJECT_DIR = REPO_ROOT / "zensical"
BASELINE_PATH = REPO_ROOT / "known-issues.txt"

# Outcome of assessing one build. ok is the gate verdict; reasons explains a
# failure; new and resolved are the baseline diff.
Assessment = namedtuple("Assessment", "ok new resolved reasons")


def parse_issues(build_output):
    """Return the set of normalised issue keys in Zensical build output.

    Each key is "<type> @ <file>:<line>:<col>", e.g.
    "anchor does not exist @ guide/page.md:3:98". Colour escapes are
    ignored; a clean build yields the empty set.
    """
    raise NotImplementedError


def parse_issue_count(build_output):
    """Return the integer from the checker's summary line.

    "N issues found" yields N, "No issues found" yields 0, and output with
    no summary line at all yields None (an incomplete or crashed build).
    """
    raise NotImplementedError


def load_baseline(path):
    """Read the baseline issue keys, one per line.

    Blank lines and lines beginning with '#' are ignored.
    """
    raise NotImplementedError


def diff_issues(current, baseline):
    """Return (new, resolved): issues present only in current, and baseline
    issues no longer present."""
    raise NotImplementedError


def assess(build_output, returncode, baseline):
    """Judge one build against the baseline, returning an Assessment.

    Fails (ok is False) if the build exited non-zero, if the summary line is
    absent, if the parsed diagnostic count disagrees with that summary, or if
    any parsed issue is absent from the baseline. Baseline issues no longer
    reported are surfaced in resolved but never fail the gate.
    """
    raise NotImplementedError


def run_build(project_dir):
    """Build the project with Zensical; return (combined_output, returncode)."""
    result = subprocess.run(
        ["zensical", "build", "-c"],
        cwd=project_dir,
        capture_output=True,
        text=True,
    )
    return result.stdout + result.stderr, result.returncode


def main(argv=None, runner=run_build):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-dir", type=Path, default=PROJECT_DIR)
    parser.add_argument("--baseline", type=Path, default=BASELINE_PATH)
    args = parser.parse_args(argv)

    output, returncode = runner(args.project_dir)
    result = assess(output, returncode, load_baseline(args.baseline))

    for issue in sorted(result.resolved):
        print(f"resolved (no longer reported): {issue}")
    for issue in sorted(result.new):
        print(f"NEW issue introduced by the flatten: {issue}")

    if not result.ok:
        for reason in result.reasons:
            print(f"FAIL: {reason}")
        return 1
    print("OK: build clean against the baseline.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
