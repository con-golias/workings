# Shared rules for cutting an item's section out of an 8-K's plain text.
import re

HEAD_205 = re.compile(r"item\s*2\s*\.\s*05", re.I)
# A candidate item heading: "Item 7.01 Regulation FD", "ITEM 9.01. Financial ...", or the signature block.
CAND = re.compile(r"(?:Item|ITEM)\s*[1-9]\s*\.\s*\d\d\.?\s*[:\-–—]?\s*[A-Z][A-Za-z]|SIGNATURES?\b|Signatures?\s+Pursuant")
# Words that make "Item N.NN" an in-text reference rather than a heading ("as described under Item 8.01").
REF = re.compile(r"(?:under|in|see|to|of|and|or|with|by|per|this|that|such|pursuant|Items?|the|our|its)[\s,(]*$", re.I)


def next_heading(t, start):
    for m in CAND.finditer(t, start):
        if not REF.search(t[max(0, m.start() - 25): m.start()]):
            return m.start()
    return None


def item_section(t, head=HEAD_205, limit=8000):
    """Longest span from an item heading to the next real heading (or `limit` characters)."""
    best = ""
    for m in head.finditer(t):
        n = next_heading(t, m.end())
        s = t[m.start(): n if n is not None else min(len(t), m.end() + limit)]
        if len(s) > len(best):
            best = s
    return best
