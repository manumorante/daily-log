"""
Helpers de interfaz para daily-log.
Colores pastel ANSI y símbolos elegantes.
"""

import sys

# ─── Colores (ANSI 256) ──────────────────────────────────────────────────────

_NO_COLOR = not sys.stdout.isatty()


def _c(code: str, text: str) -> str:
    if _NO_COLOR:
        return text
    return f"\033[38;5;{code}m{text}\033[0m"


def _dim(text: str) -> str:
    return _c("245", text)


def green(text: str) -> str:
    return _c("114", text)


def yellow(text: str) -> str:
    return _c("222", text)


def red(text: str) -> str:
    return _c("174", text)


def blue(text: str) -> str:
    return _c("111", text)


def cyan(text: str) -> str:
    return _c("116", text)


def dim(text: str) -> str:
    return _dim(text)


# ─── Símbolos ─────────────────────────────────────────────────────────────────

OK = green("●")
SKIP = dim("○")
WARN = yellow("▲")
ERR = red("✕")
ITEM = dim("▸")
RUN = blue("●")

# ─── Helpers ──────────────────────────────────────────────────────────────────

LINE = dim("─" * 40)


def header(title: str):
    print(f"\n  {blue(title)}")
    print(f"  {LINE}")


def ok(text: str):
    print(f"  {OK} {text}")


def skip(text: str):
    print(f"  {SKIP} {dim(text)}")


def warn(text: str):
    print(f"  {WARN} {yellow(text)}")


def err(text: str):
    print(f"  {ERR} {red(text)}")


def item(text: str):
    print(f"    {ITEM} {text}")


def info(text: str):
    print(f"  {dim(text)}")


def run(text: str):
    print(f"  {RUN} {text}")


def done(text: str):
    print(f"\n  {OK} {text}")


def separator():
    print(f"  {LINE}")
