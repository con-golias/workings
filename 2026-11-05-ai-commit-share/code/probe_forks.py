import os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gh import search
for repo in ["torvalds/linux", "facebook/react"]:
    sha = subprocess.run(["gh", "api", f"repos/{repo}/commits?per_page=1", "--jq", ".[0].sha"], capture_output=True, text=True).stdout.strip()
    r = search(f"hash:{sha}", per_page=10)
    print(repo, sha[:10], r["total_count"], r["incomplete_results"], [i["repository"]["full_name"] for i in r["items"]])
