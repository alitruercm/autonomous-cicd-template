"""
PR Self-Healing Agent.

Automatically fixes CI failures by analyzing diffs and generating patches.
Uses AI to identify and fix common issues like lint errors, formatting,
missing imports, and simple test failures.

Safety mechanisms:
- Max 2 AI commits per PR (prevents loops)
- PR-only commits (no direct main pushes)
- Rules enforced via .ai/CLAUDE_RULES.md
- Patch validation before apply
- Fail-open on AI errors
"""

import subprocess
import sys
from pathlib import Path

# Add scripts directory to path for ai_engine import
sys.path.insert(0, str(Path(__file__).parent))

from ai_engine import ask_ai

MAX_COMMITS_PER_PR = 2
COMMIT_MARKER = "[ai-self-heal]"


def run(cmd: list[str]) -> str:
    """Run a shell command and return output."""
    return subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode()


def already_healed() -> bool:
    """Check if max self-heal attempts reached."""
    log = run(["git", "log", "--oneline", "-5"])
    return log.count(COMMIT_MARKER) >= MAX_COMMITS_PER_PR


def get_failures() -> str:
    """Get git diff as context for AI analysis."""
    try:
        diff = run(["git", "diff", "origin/main...HEAD"])
    except Exception:
        diff = run(["git", "diff", "HEAD~1"])
    return diff


def generate_fix(diff: str) -> str:
    """Use AI to generate a fix patch."""
    # Truncate diff if too large
    max_chars = 8000
    if len(diff) > max_chars:
        diff = diff[:max_chars] + "\n... [truncated]"

    prompt = f"""
You are a Senior Software Engineer acting as a PR self-healing agent.

Rules:
- Follow .ai/CLAUDE_RULES.md strictly
- Do NOT introduce new dependencies
- Do NOT weaken CI/CD, security, or coverage
- Only fix what is necessary to pass CI

Input:
Git diff:
{diff}

Task:
1. Identify why CI or rules likely failed
2. Propose concrete code fixes
3. Output ONLY a unified diff (git apply compatible)

Output format:
```diff
diff --git a/path/to/file b/path/to/file
--- a/path/to/file
+++ b/path/to/file
@@ -line,count +line,count @@
 context
-removed line
+added line
 context
```
"""

    return ask_ai(prompt)


def extract_patch(response: str) -> str:
    """Extract diff content from AI response."""
    # Try to find diff block
    if "```diff" in response:
        start = response.find("```diff") + 7
        end = response.find("```", start)
        if end > start:
            return response[start:end].strip()

    # Try to find raw diff
    if "diff --git" in response:
        start = response.find("diff --git")
        return response[start:].strip()

    return response


def apply_patch(patch: str) -> tuple[bool, str]:
    """Apply a git patch."""
    try:
        p = subprocess.Popen(
            ["git", "apply", "--check"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        _, err = p.communicate(patch.encode())
        if p.returncode != 0:
            return False, err.decode()

        # Actually apply the patch
        p = subprocess.Popen(
            ["git", "apply"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        _, err = p.communicate(patch.encode())
        return p.returncode == 0, err.decode()
    except Exception as e:
        return False, str(e)


def commit_changes() -> None:
    """Commit and attribute the self-healing changes."""
    run(["git", "config", "user.name", "AI Self-Heal Bot"])
    run(["git", "config", "user.email", "ai-bot@noreply.github.com"])
    run(["git", "add", "."])
    run(["git", "commit", "-m", f"{COMMIT_MARKER} Fix CI/rule violations"])


def main() -> None:
    """Run the self-healing agent."""
    print("Self-Healing Agent started")

    if already_healed():
        print("[STOP] Max self-heal attempts reached. Human review required.")
        sys.exit(0)

    diff = get_failures()
    if not diff.strip():
        print("[OK] No diff found. Nothing to heal.")
        sys.exit(0)

    print("Analyzing failures with AI...")
    try:
        response = generate_fix(diff)
        patch = extract_patch(response)
    except Exception as e:
        print(f"[WARNING] AI analysis failed: {e}")
        print("Falling back to human review.")
        sys.exit(0)

    if "diff --git" not in patch:
        print("[WARNING] AI did not return a valid patch.")
        print("Falling back to human review.")
        sys.exit(0)

    print("Applying patch...")
    success, error = apply_patch(patch)
    if not success:
        print("[ERROR] Patch failed to apply:")
        print(error)
        print("Falling back to human review.")
        sys.exit(0)

    print("Committing changes...")
    try:
        commit_changes()
        run(["git", "push"])
        print("[OK] Self-healing commit pushed successfully.")
    except Exception as e:
        print(f"[ERROR] Failed to push: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
