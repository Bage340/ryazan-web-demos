"""Narrow GitHub deployment helper; credentials stay in process memory."""

import argparse
import json
import os
from pathlib import Path
import subprocess
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "qa" / "deploy-state.json"
OWNER = "Bage340"


def credential():
    env = os.environ.copy()
    env.update(GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never")
    result = subprocess.run(
        ["git", "-c", "credential.interactive=never", "credential", "fill"],
        input="protocol=https\nhost=github.com\n\n", capture_output=True,
        text=True, env=env, timeout=20, check=False,
    )
    fields = dict(line.split("=", 1) for line in result.stdout.splitlines() if "=" in line)
    if not fields.get("password"):
        raise RuntimeError("DEPLOY_BLOCKED_AUTH: saved GitHub credential unavailable")
    return fields["password"]


def api(token, endpoint, method="GET", data=None):
    request = urllib.request.Request(
        "https://api.github.com" + endpoint,
        data=json.dumps(data).encode() if data is not None else None,
        method=method,
        headers={"Authorization": "Bearer " + token, "Accept": "application/vnd.github+json",
                 "User-Agent": "ryazan-web-demos", "X-GitHub-Api-Version": "2022-11-28"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        content = response.read()
        return json.loads(content) if content else {}


def load_state():
    state = json.loads(STATE.read_text(encoding="utf-8"))
    if state["owner"] != OWNER or not state["repo"].startswith("ryazan-web-demos"):
        raise RuntimeError("Unexpected deployment target")
    return state


def save_state(state):
    STATE.parent.mkdir(exist_ok=True)
    STATE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["status", "create", "enable-pages", "runs", "pages", "jobs"])
    parser.add_argument("--repo", default="ryazan-web-demos")
    parser.add_argument("--run", type=int)
    args = parser.parse_args()
    token = credential()
    profile = api(token, "/user")
    if profile["login"] != OWNER:
        raise RuntimeError("Authenticated account differs from authorized owner")
    if args.action == "status":
        print(json.dumps({"login": profile["login"], "authenticated": True}))
        return
    if args.action == "create":
        if STATE.exists():
            raise RuntimeError("Deployment state already exists; inspect it rather than create again")
        if args.repo != "ryazan-web-demos" and args.repo != "ryazan-web-demos-2026-11-11":
            raise RuntimeError("Repository name outside authorized demo scope")
        try:
            api(token, f"/repos/{OWNER}/{args.repo}")
        except urllib.error.HTTPError as error:
            if error.code != 404:
                raise
        else:
            raise RuntimeError("Repository already exists; refusing to overwrite or reuse")
        repo = api(token, "/user/repos", "POST", {
            "name": args.repo, "description": "Three original static website demos and portfolio. No real companies, orders or data collection.",
            "private": False, "auto_init": False, "has_issues": False,
            "has_projects": False, "has_wiki": False,
        })
        save_state({"owner": OWNER, "repo": repo["name"], "repository_url": repo["html_url"], "clone_url": repo["clone_url"]})
        print(json.dumps({"repository_url": repo["html_url"], "created": True}))
        return
    state = load_state()
    target = f"/repos/{OWNER}/{state['repo']}"
    if args.action == "enable-pages":
        try:
            pages = api(token, target + "/pages")
        except urllib.error.HTTPError as error:
            if error.code != 404:
                raise
            pages = api(token, target + "/pages", "POST", {"build_type": "workflow"})
        if pages.get("build_type") != "workflow":
            api(token, target + "/pages", "PUT", {"build_type": "workflow"})
            pages = api(token, target + "/pages")
        state["pages_url"] = pages.get("html_url")
        save_state(state)
        print(json.dumps({"build_type": pages.get("build_type"), "pages_url": pages.get("html_url"), "status": pages.get("status")}))
    elif args.action == "pages":
        pages = api(token, target + "/pages")
        state["pages_url"] = pages.get("html_url")
        save_state(state)
        print(json.dumps({k: pages.get(k) for k in ("html_url", "status", "build_type", "https_enforced")}))
    elif args.action == "runs":
        runs = api(token, target + "/actions/workflows/deploy-pages.yml/runs?per_page=5")
        print(json.dumps([{k: run.get(k) for k in ("id", "status", "conclusion", "html_url", "head_sha")} for run in runs["workflow_runs"]]))
    elif args.action == "jobs":
        if not args.run:
            raise RuntimeError("--run is required")
        jobs = api(token, target + f"/actions/runs/{args.run}/jobs")
        print(json.dumps([{k: job.get(k) for k in ("id", "name", "status", "conclusion", "steps")} for job in jobs["jobs"]]))


if __name__ == "__main__":
    try:
        main()
    except urllib.error.HTTPError as error:
        print(f"GitHub API returned HTTP {error.code}")
        raise SystemExit(1) from None
    except (RuntimeError, subprocess.TimeoutExpired, urllib.error.URLError) as error:
        print(str(error))
        raise SystemExit(1) from None
