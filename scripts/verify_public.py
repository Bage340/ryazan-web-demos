"""Verify actual Pages URLs and byte-for-byte public assets from API state."""

import hashlib
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def main():
    state = json.loads((ROOT / "qa" / "deploy-state.json").read_text(encoding="utf-8"))
    base = state.get("pages_url")
    if not base or not base.startswith("https://"):
        raise RuntimeError("No actual HTTPS URL returned by Pages API")
    result = []
    for file in sorted((ROOT / "portfolio-dist").rglob("*")):
        if not file.is_file() or file.name == ".nojekyll":
            continue
        relative = file.relative_to(ROOT / "portfolio-dist").as_posix()
        url = base.rstrip("/") + "/" + relative
        request = urllib.request.Request(url, headers={"User-Agent": "ryazan-demo-qa"})
        with urllib.request.urlopen(request, timeout=30) as response:
            actual = response.read()
            if response.status != 200 or actual != file.read_bytes():
                raise RuntimeError(f"Public artifact mismatch: {relative}")
            result.append({"file": relative, "url": response.url, "status": response.status,
                           "sha256": hashlib.sha256(actual).hexdigest()})
    for suffix in ("", "ventilation/", "furniture/", "autoservice/"):
        url = base.rstrip("/") + "/" + suffix
        with urllib.request.urlopen(url, timeout=30) as response:
            if response.status != 200:
                raise RuntimeError(f"Public landing page unavailable: {suffix}")
    (ROOT / "qa" / "public-assets.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"PUBLIC_ARTIFACT_VERIFIED: {len(result)} files match; four landing URLs return HTTP 200")


if __name__ == "__main__":
    main()
