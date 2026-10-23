"""A claim gate: the last check before an agent's reply reaches a customer.

If the reply says an action happened, a successful tool event for that action
must exist in this run. Otherwise the sentence never leaves the server.
"""
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class ToolEvent:
    tool: str   # what ran, e.g. "cancel_order"
    ok: bool    # set by your code from the system's answer, never by the model
    ref: str    # the record that proves it: a cancellation id, a refund id


# Phrases that assert a completed action, per tool that can make it true.
CLAIMS = {
    "cancel_order": re.compile(r"\b(has been|have|I've|is now|was)\s+cancel+ed\b", re.I),
    "refund_payment": re.compile(r"\b(refund(ed)?\b.*\b(issued|processed|sent|done)|(have|I've|has been)\s+refunded)\b", re.I),
}

# What the customer reads instead: true, and still useful.
FALLBACK = {
    "cancel_order": "I couldn't confirm the cancellation yet. A person from our team will check it and email you.",
    "refund_payment": "I couldn't confirm the refund yet. A person from our team will check it and email you.",
}


@dataclass(frozen=True)
class Verdict:
    passed: bool
    reply: str
    unproven: tuple[str, ...]


def gate(reply: str, events: list[ToolEvent]) -> Verdict:
    proven = {e.tool for e in events if e.ok and e.ref}
    unproven = tuple(t for t, pattern in CLAIMS.items() if pattern.search(reply) and t not in proven)
    if not unproven:
        return Verdict(True, reply, ())
    return Verdict(False, " ".join(FALLBACK[t] for t in unproven), unproven)
