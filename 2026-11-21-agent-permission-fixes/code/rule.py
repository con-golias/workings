# The inclusion rule, as shown in the article. Applied by hand to every candidate line (METHOD.md).
COUNTS_IF = {
    "something":  ["a command", "a tool call", "a file read or write", "a network request",
                   "a setting", "a plugin", "a hook", "a subagent"],
    "got past":   ["the permission prompt", "an allow / ask / deny rule", "the sandbox",
                   "workspace trust or a consent dialog", "organisation policy",
                   "a blocking hook", "plan mode", "a path boundary"],
}
NOT_COUNTED = ["checks that were too strict", "display-only fixes",
               "'Changed...' or 'Added...' design changes"]
