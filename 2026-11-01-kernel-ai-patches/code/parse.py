"""Parse mainline non-merge commits into JSON: sha, author email/name, author/commit time, subject,
Assisted-by values, Fixes: targets, revert targets, Reported-by Sashiko (the AI review bot), Cc stable.
  python parse.py <bare linux clone> <out.json>"""
import subprocess, re, json, sys
REPO = sys.argv[1]; OUT = sys.argv[2]
SEP = "\x1e"; FS = "\x1f"
fmt = FS.join(["%H", "%ae", "%an", "%at", "%ct", "%s", "%B"]) + SEP
raw = subprocess.run(["git", "-C", REPO, "log", "--no-merges", "--format=" + fmt],
                     capture_output=True, check=True).stdout.decode("utf-8", "replace")
re_ab = re.compile(r"^\s*assisted-by:\s*(.+?)\s*$", re.I | re.M)
re_fix = re.compile(r"^\s*fixes:\s*([0-9a-f]{8,40})\b", re.I | re.M)
re_rev = re.compile(r"This reverts commit ([0-9a-f]{8,40})", re.I)
re_sash = re.compile(r"^\s*reported-by:.*sashiko", re.I | re.M)
rows = []
for rec in raw.split(SEP):
    rec = rec.strip("\n")
    if not rec: continue
    h, ae, an, at, ct, s, b = rec.split(FS, 6)
    rows.append(dict(h=h, ae=ae.lower(), an=an, at=int(at), ct=int(ct), s=s,
                     ab=re_ab.findall(b), fixes=[x.lower() for x in re_fix.findall(b)],
                     rev=[x.lower() for x in re_rev.findall(b)],
                     sashiko=bool(re_sash.search(b)),
                     stable=bool(re.search(r"^\s*cc:.*stable@", b, re.I | re.M))))
json.dump(rows, open(OUT, "w"))
print(len(rows), "commits;", sum(1 for r in rows if r["ab"]), "assisted")
