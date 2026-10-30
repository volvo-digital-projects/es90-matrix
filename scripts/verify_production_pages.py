"""Wait until the public GitHub Pages site serves the canonical static files."""

import argparse
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_BASE = "https://volvo-es90-matrix.github.io/es90-matrix/"
PUBLIC_SUFFIXES = {".html", ".json", ".js", ".css", ".svg", ".png", ".jpg", ".jpeg", ".webp", ".ico"}


def changed_public_files(base_sha: str) -> list[str]:
    changed = subprocess.check_output(
        ["git", "diff", "--name-only", base_sha, "HEAD", "--"],
        cwd=ROOT,
        text=True,
    ).splitlines()
    paths = {"app.html", "version.json"}
    for path in changed:
        if Path(path).suffix.lower() in PUBLIC_SUFFIXES and not path.startswith(
            (".github/", "scripts/", "automation/")
        ):
            paths.add(path)
    return sorted(path for path in paths if (ROOT / path).is_file())


def public_file_matches(path: str, commit: str, attempt: int) -> bool:
    url = PUBLIC_BASE + urllib.parse.quote(path) + f"?deploy={commit}&attempt={attempt}"
    request = urllib.request.Request(url, headers={"Cache-Control": "no-cache"})
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            served = response.read()
    except (urllib.error.URLError, TimeoutError) as error:
        print(f"{path}: public read failed: {error}", flush=True)
        return False
    expected = (ROOT / path).read_bytes()
    if Path(path).suffix.lower() in {".html", ".json", ".js", ".css", ".svg"}:
        expected = expected.replace(b"\r\n", b"\n")
    if served != expected:
        print(f"{path}: public content has not reached commit {commit[:12]}", flush=True)
        return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-sha", required=True)
    parser.add_argument("--commit", required=True)
    args = parser.parse_args()
    paths = changed_public_files(args.base_sha)
    for attempt in range(1, 31):
        pending = [
            path for path in paths
            if not public_file_matches(path, args.commit, attempt)
        ]
        if not pending:
            print(f"Production Pages verified at {args.commit}: {', '.join(paths)}")
            return 0
        print(f"Pages verification attempt {attempt}/30: pending {', '.join(pending)}", flush=True)
        if attempt < 30:
            time.sleep(10)
    print("Production Pages did not serve the expected canonical files within 5 minutes.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
