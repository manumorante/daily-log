from .git_local import collect_git_local
from .github import collect_github
from .wakatime import collect_wakatime
from .shortcut import collect_shortcut
# from .claude_code import collect_claude_code  # Disabled: ambiguous context classification

ALL = [
    ("Git Local", collect_git_local),    # Fast: local git log
    ("GitHub", collect_github),          # Git remote: API
    ("WakaTime", collect_wakatime),      # Time tracking: API
    ("Shortcut", collect_shortcut),      # Project mgmt: API (slowest, multiple calls)
    # ("Claude Code", collect_claude_code),  # Disabled: ambiguous context classification
]
