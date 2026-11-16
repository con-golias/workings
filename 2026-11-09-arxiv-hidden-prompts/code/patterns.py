"""Reviewer-directed instruction phrases, from Lin's four types (CACM 2026, Table 1) plus generic forms.

A hit is a phrase match in the PDF's extracted text (whitespace and case normalised). A hit is a candidate only:
papers that study prompt injection quote the same phrases, so every new hit gets a verdict by reading.
"""
import re

PHRASES = [
    r"ignore (?:all )?(?:the )?previous instructions",
    r"give a positive review",
    r"do not highlight any negatives",
    r"recommend accepting this paper",
    r"for llm reviewers?",
    r"llm reviewer note",
    r"important review requirements",
    r"as a language model,? you should",
    r"if you are an? (?:ai|llm|large language model|language model)\b[^.]{0,80}review",
    r"(?:ai|llm) reviewers?:",
]
RX = re.compile("|".join(f"(?:{p})" for p in PHRASES), re.I)


def norm(text):
    text = text.replace("­", "").replace("-\n", "")
    return re.sub(r"\s+", " ", text)


def find_hits(text, width=160):
    t = norm(text)
    out = []
    for m in RX.finditer(t):
        out.append(t[max(0, m.start() - width): m.end() + width])
    return out
