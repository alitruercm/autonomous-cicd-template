"""
AI Rules Semantic Auditor.

Uses AI to analyze git diffs for rule violations.
Detects weakening of CI/CD gates, security downgrades,
and AI provider abstraction violations.

Behavior:
- AI detects rule violations -> PR blocked (exit 1)
- AI call fails -> PR allowed (exit 0, fail-open)
"""

import subprocess
import sys
from pathlib import Path

# Add scripts directory to path for ai_engine import
sys.path.insert(0, str(Path(__file__).parent))

from ai_engine import ask_ai


def get_diff() -> str:
    """Get git diff for analysis."""
    try:
        # Try to get diff from main branch
        return subprocess.check_output(
            ["git", "diff", "origin/main...HEAD"],
            stderr=subprocess.DEVNULL,
        ).decode()
    except Exception:
        try:
            # Fallback to last commit diff
            return subprocess.check_output(
                ["git", "diff", "HEAD~1"],
                stderr=subprocess.DEVNULL,
            ).decode()
        except Exception:
            return ""


def main() -> None:
    """Run AI semantic audit on git diff."""
    diff = get_diff()

    if not diff.strip():
        print("[OK] No changes to audit.")
        sys.exit(0)

    # Truncate diff if too large (token limits)
    max_diff_chars = 10000
    if len(diff) > max_diff_chars:
        diff = diff[:max_diff_chars] + "\n... [truncated]"

    prompt = f"""
You are an AI governance auditor.

Repository rules are defined in .ai/CLAUDE_RULES.md.

Analyze the following git diff and answer:
1. Does this change violate ANY rule?
2. Are CI/CD gates weakened?
3. Are security checks removed or downgraded?
4. Is AI provider abstraction violated?
5. Is coverage enforcement reduced?

Respond STRICTLY in JSON with:
{{
  "violation": true|false,
  "severity": "critical|high|medium|low|none",
  "explanation": "...",
  "recommendation": "..."
}}

Git diff:
{diff}
"""

    try:
        response = ask_ai(prompt)
        print(response)

        # Check for violation in response
        response_lower = response.lower()
        if '"violation": true' in response_lower or '"violation":true' in response_lower:
            print("\n[ERROR] AI RULE VIOLATION DETECTED")
            sys.exit(1)

        print("\n[OK] No rule violations detected.")
        sys.exit(0)

    except Exception as e:
        # Fail-open: AI failures don't block PR
        print("[WARNING] AI audit failed, falling back to human review.")
        print(f"Error: {e}")
        sys.exit(0)


if __name__ == "__main__":
    main()
