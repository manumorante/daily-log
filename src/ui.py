"""Terminal UI helpers. Rich-based colors, symbols, and output."""

from contextlib import contextmanager
from rich.console import Console

console = Console(highlight=False)

# ─── Colors ──────────────────────────────────────────────────────────────────


def _style(style: str, text: str) -> str:
    """Return styled text as a string (for inline use with print)."""
    with console.capture() as cap:
        console.print(text, style=style, end="", highlight=False)
    return cap.get()


def green(text: str) -> str:
    return _style("green", text)


def yellow(text: str) -> str:
    return _style("yellow", text)


def red(text: str) -> str:
    return _style("red", text)


def blue(text: str) -> str:
    return _style("blue", text)


def cyan(text: str) -> str:
    return _style("cyan", text)


def dim(text: str) -> str:
    return _style("dim", text)


# ─── Symbols ─────────────────────────────────────────────────────────────────

OK = green("●")
SKIP = dim("○")
WARN = yellow("▲")
ERR = red("✕")
ITEM = dim("▸")
RUN = blue("●")

# ─── Helpers ─────────────────────────────────────────────────────────────────

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


# ─── Spinner ─────────────────────────────────────────────────────────────────


@contextmanager
def spinner(message: str):
    """Show a spinner while a block executes."""
    if console.is_terminal:
        with console.status(f"  {message}", spinner="dots"):
            yield
    else:
        print(f"  {message}")
        yield
