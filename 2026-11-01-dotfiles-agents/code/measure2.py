# Year-end snapshots of each bare clone: config files the user keeps (paths) and tools/themes they name (text), with
# vendored code, plugin folders, theme packs and prose excluded. One git grep per snapshot.
import json, os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
CL, OUT = sys.argv[1], sys.argv[2]
YEARS = list(range(2015, 2027))
env = dict(os.environ, GIT_NO_LAZY_FETCH="1")
VENDOR = r"(^|/)(plugins?|bundle|pack|plugged|oh-my-zsh|\.oh-my-zsh|node_modules|themes?|colors|autoload|vendor|third_party|submodules?|ports)/"
PROSE = r"\.(md|markdown|rst|txt|org|adoc|html)$|(^|/)(LICENSE|README)"
EXCL = [":!*.md", ":!*.markdown", ":!*.rst", ":!*.txt", ":!*.org", ":!*.html", ":!**/LICENSE*", ":!**/README*"] + \
       [f":!**/{x}/**" for x in ("plugins", "plugin", "bundle", "pack", "plugged", "oh-my-zsh", ".oh-my-zsh", "node_modules", "themes", "theme",
                                  "colors", "autoload", "vendor", "third_party", "submodules", "ports")]
PATHS = {
  "vim": r"(^|/)(\.?vimrc|_vimrc)$|(^|/)\.vim/", "neovim": r"(^|/)nvim/", "emacs": r"(^|/)(\.emacs|init\.el$|\.emacs\.d/|\.doom\.d/|doom/)",
  "helix": r"(^|/)helix/", "vscode": r"(^|/)(vscode|Code/User)/.*settings\.json$", "zed": r"(^|/)zed/(settings|keymap)\.json$",
  "zsh": r"(^|/)\.?zshrc$|(^|/)zsh/", "fish": r"(^|/)fish/|config\.fish$", "nushell": r"(^|/)nushell/",
  "starship": r"starship\.toml$", "p10k": r"\.p10k\.zsh$", "tmux": r"tmux\.conf$|(^|/)tmux/", "zellij": r"(^|/)zellij/",
  "alacritty": r"(^|/)alacritty/|alacritty\.(yml|yaml|toml)$", "kitty": r"(^|/)kitty/|kitty\.conf$", "wezterm": r"(^|/)wezterm/|wezterm\.lua$",
  "ghostty": r"(^|/)ghostty/", "iterm": r"iterm2?/|com\.googlecode\.iterm2", "i3": r"(^|/)i3/", "sway": r"(^|/)sway/",
  "hyprland": r"(^|/)hypr/", "yabai": r"yabairc$|(^|/)yabai/", "aerospace": r"aerospace\.toml$|(^|/)aerospace/",
  "ai_claude": r"(^|/)\.?claude/|(^|/)CLAUDE\.md$", "ai_cursor": r"(^|/)\.?cursor/|\.cursorrules$|(^|/)Cursor/User/", "ai_codex": r"(^|/)\.?codex/",
  "ai_gemini": r"(^|/)\.?gemini/|(^|/)GEMINI\.md$", "ai_aider": r"\.aider\.conf\.yml$", "ai_opencode": r"(^|/)opencode/|opencode\.jsonc?$",
  "ai_copilot": r"(^|/)github-copilot/|(^|/)copilot(\.lua|-chat\.lua)$", "ai_agentsmd": r"(^|/)AGENTS\.md$",
  "brewfile": r"Brewfile$", "nix": r"\.nix$",
}
TOKENS = {
  "catppuccin": r"catppuccin", "tokyonight": r"tokyo-?night", "gruvbox": r"gruvbox", "dracula": r"\bdracula\b", "nord": r"\bnord(fox)?\b",
  "solarized": r"solarized", "rosepine": r"rose-?pine", "kanagawa": r"kanagawa", "onedark": r"\bone-?dark\b", "everforest": r"everforest",
  "monokai": r"monokai", "fzf": r"\bfzf\b", "ripgrep": r"\brg --|alias \w+=.?rg\b|ripgrep|RIPGREP_CONFIG", "bat": r"alias \w+=.?bat\b|\bbat --|BAT_THEME|\bbatcat\b|(^|/)bat/config",
  "eza": r"\beza\b", "exa": r"alias \w+=.?exa\b|\bexa -", "zoxide": r"zoxide", "atuin": r"\batuin\b", "lazygit": r"lazygit",
  "fd": r"\bfdfind\b|alias \w+=.?fd\b|\bfd --type|\bfd -t ", "delta": r"pager\s*=\s*delta|\[delta\]|git-delta", "direnv": r"direnv",
  "ohmyzsh": r"oh-my-zsh", "lazyvim": r"lazyvim", "jetbrainsmono": r"jetbrains ?mono", "firacode": r"fira ?code",
  "berkeley": r"berkeley ?mono", "mise": r"\bmise\b", "asdf": r"\basdf\b", "uv": r"\buv (pip|tool|run|sync)\b",
}
UNION = "|".join(f"(?:{p})" for p in TOKENS.values())
def run(args):
    return subprocess.run(args, capture_output=True, text=True, env=env, encoding="utf-8", errors="replace").stdout
def one(name):
    d = os.path.join(CL, name); rows = []
    for y in YEARS:
        end = f"{y}-12-31T23:59:59" if y < 2026 else "2026-10-31T00:00:00"
        rev = run(["git", "-C", d, "rev-list", "-1", f"--before={end}", "HEAD"]).strip()
        if not rev: continue
        n = run(["git", "-C", d, "rev-list", "--count", f"--since={y}-01-01", f"--before={end}", "HEAD"]).strip()
        files = [f for f in run(["git", "-C", d, "ls-tree", "-r", "--name-only", rev]).splitlines() if not re.search(VENDOR, f, re.I)]
        hit = {k: any(re.search(p, f, re.I) for f in files) for k, p in PATHS.items()}
        out = run(["git", "-C", d, "grep", "-I", "-i", "-o", "-h", "-P", UNION, rev, "--", "."] + EXCL)
        words = set(out.lower().splitlines())
        for k, p in TOKENS.items():
            hit[k] = any(re.search(p, w, re.I) for w in words)
        rows.append({"repo": name, "year": y, "commits": int(n or 0), "files": len(files), **hit})
    return rows
names = sorted(os.listdir(CL))
with ThreadPoolExecutor(8) as ex:
    allrows = [r for rs in ex.map(one, names) for r in rs]
json.dump(allrows, open(OUT, "w"))
print(len(names), "repos,", len(allrows), "repo-years")
