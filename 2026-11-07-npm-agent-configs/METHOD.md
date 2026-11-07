# Conventions

- **Agent-config paths:** `~/.claude.json`, `~/.claude/` (settings, skills, commands, agents, hooks, plugins, CLAUDE.md),
  Claude Desktop's `claude_desktop_config.json`, `~/.codex/`, `~/.cursor/`, `~/.gemini/`, `~/.config/opencode` and
  `.opencode`, `.mcp.json`, Windsurf / Codeium, Kiro, Continue, Amp.
- **Global:** a write into one of those under the user's home. **Project:** a write into the project folder
  (`INIT_CWD`). **None:** prints, checks or reads only.
- **global_only:** the write is behind `npm_config_global === "true"`. Otherwise it also runs as a dependency.
- **optout:** an environment variable or flag stops the write. **grant:** the write includes trust hashes, permission
  allow-rules or approval settings.
- **Downloads:** api.npmjs.org last-week point, 6 Nov 2026.
