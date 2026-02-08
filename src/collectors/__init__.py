from .github import collect_github
from .shortcut import collect_shortcut
from .git_local import collect_git_local
from .wakatime import collect_wakatime
from .claude_code import collect_claude_code

ALL = [
    ("GitHub", collect_github),
    ("Shortcut", collect_shortcut),
    ("Git Local", collect_git_local),
    ("WakaTime", collect_wakatime),
    ("Claude Code", collect_claude_code),
]
