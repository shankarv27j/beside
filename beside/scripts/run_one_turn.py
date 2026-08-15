"""Quick local test without the API server.

Usage (from beside/):
  .venv\\Scripts\\activate
  python scripts/run_one_turn.py "I don't know"
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.crew import run_mentor_turn  # noqa: E402


def main() -> None:
    message = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "hi"
    result = run_mentor_turn(
        child_name="Asha",
        age=10,
        skill="arithmetic",
        interest="cricket",
        profile="New learner. Likes cricket stories. Build trust first.",
        history="(no prior turns)",
        child_message=message,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()