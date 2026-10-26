# Model-ID status as of 26 Oct 2026, from the vendors' own deprecation pages (read 26 Oct 2026):
#   OpenAI    developers.openai.com/api/docs/deprecations   (release dates: developers.openai.com/api/docs/changelog)
#   Anthropic platform.claude.com/docs/en/about-claude/model-deprecations
#   Google    ai.google.dev/gemini-api/docs/deprecations  (Gemini 1.5: 24 Sep 2025, Google notice quoted on discuss.ai.google.dev;
#             Gemini 1.0: 15 Feb 2025, forum report, the weakest date here)
# Each rule: (regex on the whole ID, vendor, family, release date, shutdown date or None = none announced).
# The first matching rule wins, so specific snapshots come before family rules.
import re

R = [
    # ---- OpenAI: retired ----
    (r"gpt-3\.5-turbo-(0301|0613|16k.*)", "openai", "gpt-3.5-turbo", "2023-03-01", "2024-09-13"),
    (r"gpt-3\.5-turbo-(instruct|1106).*", "openai", "gpt-3.5-turbo", "2023-03-01", "2026-09-28"),
    (r"gpt-3\.5-turbo.*", "openai", "gpt-3.5-turbo", "2023-03-01", "2026-10-23"),
    (r"gpt-4-32k.*", "openai", "gpt-4", "2023-03-14", "2025-06-06"),
    (r"gpt-4-(1106-)?vision-preview", "openai", "gpt-4", "2023-11-06", "2024-12-06"),
    (r"gpt-4-(0314|0125-preview|turbo-preview)", "openai", "gpt-4", "2023-03-14", "2026-03-26"),
    (r"gpt-4-1106-preview", "openai", "gpt-4-turbo", "2023-11-06", "2026-10-23"),
    (r"gpt-4-turbo.*", "openai", "gpt-4-turbo", "2024-04-09", "2026-10-23"),
    (r"gpt-4(-0613)?", "openai", "gpt-4", "2023-03-14", "2026-10-23"),
    (r"gpt-4o-2024-05-13", "openai", "gpt-4o", "2024-05-13", "2026-10-23"),
    (r"gpt-4o(-mini)?-search-preview.*", "openai", "gpt-4o", "2025-03-11", "2026-07-23"),
    (r"gpt-4o(-mini)?-(realtime|audio)-preview.*", "openai", "gpt-4o-audio", "2024-10-01", "2026-05-07"),
    (r"gpt-4\.1-nano.*", "openai", "gpt-4.1", "2025-04-14", "2026-10-23"),
    (r"gpt-4\.5-preview.*", "openai", "gpt-4.5", "2025-02-27", "2025-07-14"),
    (r"o1-preview.*", "openai", "o1", "2024-09-12", "2025-07-28"),
    (r"o1-mini.*", "openai", "o1", "2024-09-12", "2025-10-27"),
    (r"o1(-pro)?(-20\d\d-\d\d-\d\d)?", "openai", "o1", "2024-12-17", "2026-10-23"),
    (r"o3-mini.*", "openai", "o3-mini", "2025-01-31", "2026-10-23"),
    (r"(o3|o4-mini)-deep-research.*", "openai", "deep-research", "2025-06-24", "2026-07-23"),
    (r"o4-mini.*", "openai", "o4-mini", "2025-04-16", "2026-10-23"),
    (r"gpt-5(\.1)?-chat-latest|gpt-5-codex|gpt-5\.1-codex.*|gpt-5\.2-codex", "openai", "gpt-5 chat/codex", "2025-08-07", "2026-07-23"),
    (r"gpt-5\.[23]-chat-latest", "openai", "gpt-5 chat", "2025-12-11", "2026-08-10"),
    (r"gpt-5\.4-cyber", "openai", "gpt-5.4", "2026-03-05", "2026-10-01"),
    (r"chatgpt-4o-latest", "openai", "gpt-4o", "2024-08-13", "2026-02-17"),
    (r"text-davinci-00[0-9]", "openai", "gpt-3", "2022-11-28", "2024-01-04"),
    # ---- OpenAI: shutdown announced ----
    (r"gpt-4o-mini-tts.*", "openai", "gpt-4o-tts", "2025-03-20", "2027-01-06"),
    (r"gpt-4o(-mini)?-transcribe.*", "openai", "gpt-4o-transcribe", "2025-03-20", "2027-02-26"),
    (r"gpt-4o(-mini)?-(realtime|audio).*", "openai", "gpt-4o-audio", "2024-10-01", "2027-01-20"),
    (r"gpt-4o-mini.*", "openai", "gpt-4o-mini", "2024-07-18", "2027-01-14"),
    (r"gpt-4o.*", "openai", "gpt-4o", "2024-05-13", "2027-01-14"),
    (r"gpt-4\.1(-mini)?(-2025-04-14)?", "openai", "gpt-4.1", "2025-04-14", "2027-01-14"),
    (r"gpt-5(-mini|-nano|-pro)?(-2025-\d\d-\d\d)?", "openai", "gpt-5", "2025-08-07", "2026-12-11"),
    (r"o3(-pro)?(-2025-\d\d-\d\d)?", "openai", "o3", "2025-04-16", "2026-12-11"),
    (r"gpt-5\.1(-2025-11-13)?", "openai", "gpt-5.1", "2025-11-13", "2027-04-01"),
    (r"gpt-5\.3-codex", "openai", "gpt-5.3-codex", "2026-02-24", "2027-04-01"),
    (r"gpt-5\.4-nano.*", "openai", "gpt-5.4", "2026-03-17", "2027-04-01"),
    # ---- OpenAI: no shutdown announced ----
    (r"gpt-5\.2(-pro)?(-\d{4}-\d\d-\d\d)?", "openai", "gpt-5.2", "2025-12-11", None),
    (r"gpt-5\.4(-mini|-pro)?(-\d{4}-\d\d-\d\d)?", "openai", "gpt-5.4", "2026-03-05", None),
    (r"gpt-5\.5(-pro)?(-\d{4}-\d\d-\d\d)?", "openai", "gpt-5.5", "2026-04-24", None),
    (r"gpt-5\.6(-sol|-terra|-luna)?(-\d{4}-\d\d-\d\d)?", "openai", "gpt-5.6", "2026-07-09", None),
    (r"gpt-6-astra.*", "openai", "gpt-6", "2026-09-03", None),
    (r"gpt-6\.1(-sol)?.*", "openai", "gpt-6.1", "2026-09-29", None),
    (r"gpt-6(-sol|-luna)?(-\d{4}-\d\d-\d\d)?", "openai", "gpt-6", "2026-09-22", None),
    # ---- Anthropic ----
    (r"claude-(1|instant).*", "anthropic", "claude-1", "2023-03-14", "2024-11-06"),
    (r"claude-2.*", "anthropic", "claude-2", "2023-07-11", "2025-07-21"),
    (r"claude-3-sonnet.*", "anthropic", "claude-3", "2024-03-04", "2025-07-21"),
    (r"claude-3-opus.*", "anthropic", "claude-3", "2024-03-04", "2026-01-05"),
    (r"claude-3-haiku.*", "anthropic", "claude-3", "2024-03-13", "2026-04-20"),
    (r"claude-3[-.]5-sonnet.*", "anthropic", "claude-3.5", "2024-06-20", "2025-10-28"),
    (r"claude-3[-.]5-haiku.*", "anthropic", "claude-3.5", "2024-10-22", "2026-02-19"),
    (r"claude-3[-.]7-sonnet.*", "anthropic", "claude-3.7", "2025-02-24", "2026-02-19"),
    (r"claude-(sonnet-4|4-sonnet)(-0|-20250514)?", "anthropic", "claude-4", "2025-05-22", "2026-06-15"),
    (r"claude-(opus-4|4-opus)(-0|-20250514)?", "anthropic", "claude-4", "2025-05-22", "2026-06-15"),
    (r"claude-opus-4-1.*", "anthropic", "claude-4.1", "2025-08-05", "2026-08-05"),
    (r"claude-sonnet-4-5.*", "anthropic", "claude-4.5", "2025-09-29", "2026-11-30"),
    (r"claude-haiku-4-5.*", "anthropic", "claude-4.5", "2025-10-15", None),
    (r"claude-opus-4-5.*", "anthropic", "claude-4.5", "2025-11-24", None),
    (r"claude-(opus|sonnet)-4-6.*", "anthropic", "claude-4.6", "2026-02-05", None),
    (r"claude-opus-4-7.*", "anthropic", "claude-4.7", "2026-04-16", None),
    (r"claude-opus-4-8.*", "anthropic", "claude-4.8", "2026-05-28", None),
    (r"claude-(fable|mythos)-5-1.*", "anthropic", "claude-5.1", "2026-09-01", None),
    (r"claude-(fable|mythos)-5.*", "anthropic", "claude-5", "2026-06-09", None),
    (r"claude-sonnet-5-5.*", "anthropic", "claude-5.5", "2026-09-28", None),
    (r"claude-haiku-5-5.*", "anthropic", "claude-5.5", "2026-10-07", None),
    (r"claude-opus-5-5.*", "anthropic", "claude-5.5", "2026-09-22", None),
    (r"claude-sonnet-5.*", "anthropic", "claude-5", "2026-06-30", None),
    (r"claude-opus-5.*", "anthropic", "claude-5", "2026-07-24", None),
    # ---- Google Gemini ----
    (r"gemini-1\.0.*", "google", "gemini-1.0", "2023-12-13", "2025-02-15"),
    (r"gemini-1\.5.*", "google", "gemini-1.5", "2024-05-24", "2025-09-24"),
    (r"gemini-2\.0-flash-(preview-image-generation|exp.*|thinking.*)", "google", "gemini-2.0", "2024-12-11", "2025-11-14"),
    (r"gemini-2\.0-flash-lite-preview.*", "google", "gemini-2.0", "2025-02-05", "2025-12-09"),
    (r"gemini-2\.0-flash-live.*", "google", "gemini-2.0", "2025-04-09", "2025-12-09"),
    (r"gemini-2\.0.*", "google", "gemini-2.0", "2025-02-05", "2026-06-01"),
    (r"gemini-2\.5-pro-preview-(03-25|05-06|06-05)|gemini-2\.5-pro-exp.*", "google", "gemini-2.5", "2025-03-25", "2025-12-02"),
    (r"gemini-2\.5-flash-preview-05-20", "google", "gemini-2.5", "2025-05-20", "2025-11-18"),
    (r"gemini-2\.5-flash-preview-09-2025", "google", "gemini-2.5", "2025-09-25", "2026-02-17"),
    (r"gemini-2\.5-flash-lite-preview.*", "google", "gemini-2.5", "2025-06-17", "2026-03-31"),
    (r"gemini-2\.5-flash-image-preview", "google", "gemini-2.5-image", "2025-05-07", "2026-01-15"),
    (r"gemini-2\.5-flash-image", "google", "gemini-2.5-image", "2025-10-02", "2027-03-15"),
    (r"gemini-2\.5-(flash|pro)-preview-tts", "google", "gemini-2.5-tts", "2025-05-20", "2026-11-17"),
    (r"gemini-2\.5-computer-use.*", "google", "gemini-2.5", "2025-10-07", "2026-07-28"),
    (r"gemini-2\.5-flash-native-audio.*", "google", "gemini-2.5", "2025-12-12", "2026-11-17"),
    (r"gemini-2\.5-(pro|flash|flash-lite)", "google", "gemini-2.5", "2025-06-17", None),
    (r"gemini-3-pro-preview", "google", "gemini-3", "2025-11-18", "2026-03-09"),
    (r"gemini-3-pro-image-preview.*", "google", "gemini-3-image", "2025-11-20", "2026-06-25"),
    (r"gemini-3\.1-flash-image-preview", "google", "gemini-3.1-image", "2026-02-26", "2026-06-25"),
    (r"gemini-3\.1-flash-lite-preview", "google", "gemini-3.1", "2026-03-03", "2026-05-25"),
    (r"gemini-3\.1-flash-lite", "google", "gemini-3.1", "2026-05-07", "2027-05-07"),
    (r"gemini-3\.1-flash-(tts|live)-preview", "google", "gemini-3.1", "2026-02-26", "2026-11-17"),
    (r"gemini-3-flash-preview", "google", "gemini-3", "2025-12-17", None),
    (r"gemini-3-pro-image", "google", "gemini-3-image", "2026-05-28", None),
    (r"gemini-3\.1-pro-preview", "google", "gemini-3.1", "2026-02-19", None),
    (r"gemini-3\.1-flash-(lite-)?image", "google", "gemini-3.1-image", "2026-05-28", None),
    (r"gemini-3\.5-flash-lite", "google", "gemini-3.5", "2026-07-21", None),
    (r"gemini-3\.5-flash", "google", "gemini-3.5", "2026-05-19", None),
    (r"gemini-3\.6-flash", "google", "gemini-3.6", "2026-07-21", None),
    (r"gemini-3\.7-flash", "google", "gemini-3.7", "2026-08-13", None),
    (r"gemini-3\.8-.*", "google", "gemini-3.8", "2026-09-02", None),
    (r"gemini-embedding-001", "google", "embedding", "2025-07-14", "2028-05-14"),
]
C = [(re.compile(p), v, f, rel, sh) for p, v, f, rel, sh in R]
TODAY = "2026-10-26"


def classify(mid, on=TODAY):
    """Status of a model ID on a given date: retired, scheduled (shutdown announced, later), active, unknown."""
    for rx, v, f, rel, sh in C:
        if rx.fullmatch(mid):
            st = "active" if sh is None else ("retired" if sh <= on else "scheduled")
            return dict(vendor=v, family=f, released=rel, shutdown=sh, status=st)
    v = "openai" if re.match(r"gpt-|o[1-9]|chatgpt|text-", mid) else "anthropic" if mid.startswith("claude") else "google"
    return dict(vendor=v, family=None, released=None, shutdown=None, status="unknown")
