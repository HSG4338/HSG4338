"""
cli.py — Terminal display utilities for the Agentic AI System.
Uses only ANSI escape codes — zero extra dependencies.
Windows 10+ supports ANSI in cmd/PowerShell via VT processing.
"""

import sys
import re
import time
import threading
import shutil

# ── Enable ANSI on Windows ──────────────────────────────────────────────────────
if sys.platform == "win32":
    try:
        import ctypes
        k32 = ctypes.windll.kernel32
        handle = k32.GetStdHandle(-11)
        mode = ctypes.c_ulong()
        k32.GetConsoleMode(handle, ctypes.byref(mode))
        k32.SetConsoleMode(handle, mode.value | 0x0004)
    except Exception:
        pass


# ── Colour palette ──────────────────────────────────────────────────────────────
class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    ITALIC  = "\033[3m"

    RED     = "\033[91m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    BLUE    = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN    = "\033[96m"
    WHITE   = "\033[97m"
    GREY    = "\033[90m"

    BG_DARK = "\033[48;5;234m"

    # 256-colour extras
    PURPLE  = "\033[38;5;135m"
    ORANGE  = "\033[38;5;208m"
    PINK    = "\033[38;5;213m"
    TEAL    = "\033[38;5;43m"
    INDIGO  = "\033[38;5;99m"

    # Semantic aliases
    OK     = GREEN
    FAIL   = RED
    WARN   = YELLOW
    INFO   = CYAN
    MUTED  = DIM + "\033[37m"
    ACCENT = MAGENTA
    LABEL  = BLUE


def c(color: str, text: str) -> str:
    return f"{color}{text}{C.RESET}"

def _strip_ansi(s: str) -> str:
    return re.sub(r'\033\[[0-9;]*m', '', s)

def term_width() -> int:
    return shutil.get_terminal_size((100, 24)).columns


# ── Banner ──────────────────────────────────────────────────────────────────────
_BANNER = [
    r"   _   ___ ___ _  _ _____ ___ ___     _   ___ ",
    r"  /_\ / __| __| \| |_   _|_ _/ __|   /_\ |_ _|",
    r" / _ \ (_ | _|| .` | | |  | | (__   / _ \ | | ",
    r"/_/ \_\___|___|_|\_| |_| |___\___| /_/ \_\___|",
]
_BANNER_COLORS = [C.MAGENTA, C.PURPLE, C.INDIGO, C.CYAN]

def print_banner():
    w = term_width()
    print()
    for i, line in enumerate(_BANNER):
        col = _BANNER_COLORS[min(i, len(_BANNER_COLORS) - 1)]
        print(c(col + C.BOLD, line.center(w)))
    print()
    tag = "◆  LOCAL-FIRST   ◆   NO CLOUD   ◆   NO PAID APIs  ◆"
    print(c(C.GREY, tag.center(w)))
    print()


# ── Dividers ────────────────────────────────────────────────────────────────────
def divider(char="─", color=C.GREY, width=None):
    w = width or term_width()
    print(c(color, char * w))

def thick_divider(color=C.MAGENTA):
    divider("━", color)

def section(title: str, color=C.CYAN):
    w        = term_width()
    label    = f"  {title}  "
    pad      = max((w - len(label)) // 2, 2)
    line     = c(C.GREY, "─" * pad) + c(color + C.BOLD, label) + c(C.GREY, "─" * pad)
    print()
    print(line)
    print()


# ── Status lines ────────────────────────────────────────────────────────────────
def ok(msg: str):
    print(f"  {c(C.GREEN,  '✓')}  {c(C.WHITE, msg)}")

def fail(msg: str):
    print(f"  {c(C.RED,    '✗')}  {c(C.WHITE, msg)}")

def warn(msg: str):
    print(f"  {c(C.YELLOW, '!')}  {c(C.YELLOW, msg)}")

def info(msg: str):
    print(f"  {c(C.CYAN,   '›')}  {msg}")

def muted(msg: str):
    for line in str(msg).splitlines():
        print(f"    {c(C.MUTED, line)}")

def kv(label: str, value: str, label_color=C.BLUE, value_color=C.WHITE):
    lbl = c(label_color, f"{label}:")
    val = c(value_color, str(value))
    print(f"  {lbl:<28}  {val}")


# ── Box ──────────────────────────────────────────────────────────────────────────
def box(lines: list, title: str = "", color=C.CYAN, width: int = None):
    w     = width or min(term_width() - 4, 76)
    inner = w - 2

    if title:
        title_str = f" {title} "
        gap       = inner - len(title_str) - 2
        top       = "╭─" + title_str + "─" * max(gap, 0) + "╮"
    else:
        top = "╭" + "─" * inner + "╮"

    print(c(color, top))
    for line in lines:
        vlen = len(_strip_ansi(line))
        pad  = max(inner - 2 - vlen, 0)
        print(c(color, "│") + "  " + line + " " * pad + c(color, "│"))
    print(c(color, "╰" + "─" * inner + "╯"))


# ── Spinner ──────────────────────────────────────────────────────────────────────
class Spinner:
    FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    def __init__(self, label: str = "Working", color=C.CYAN):
        self.label   = label
        self.color   = color
        self._stop   = threading.Event()
        self._thread = None

    def _spin(self):
        i = 0
        while not self._stop.is_set():
            frame = self.FRAMES[i % len(self.FRAMES)]
            sys.stdout.write(f"\r  {c(self.color, frame)}  {c(C.WHITE, self.label)}...   ")
            sys.stdout.flush()
            time.sleep(0.08)
            i += 1

    def start(self):
        self._stop.clear()
        self._thread = threading.Thread(target=self._spin, daemon=True)
        self._thread.start()
        return self

    def stop(self, success: bool = True, final_msg: str = None):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=1)
        msg  = final_msg or self.label
        icon = c(C.GREEN, "✓") if success else c(C.RED, "✗")
        col  = C.WHITE if success else C.RED
        sys.stdout.write(f"\r  {icon}  {c(col, msg)}{' ' * 30}\n")
        sys.stdout.flush()

    def __enter__(self):
        return self.start()

    def __exit__(self, exc_type, *_):
        self.stop(success=exc_type is None)


# ── Progress bar ─────────────────────────────────────────────────────────────────
def progress_bar(current: int, total: int, label: str = "", width: int = 32, color=C.CYAN):
    pct    = current / max(total, 1)
    filled = int(width * pct)
    bar    = c(color, "█" * filled) + c(C.GREY, "░" * (width - filled))
    pct_s  = c(C.WHITE + C.BOLD, f"{int(pct * 100):3d}%")
    sys.stdout.write(f"\r  {bar}  {pct_s}  {c(C.MUTED, label)}  ")
    sys.stdout.flush()
    if current >= total:
        print()


# ── Agent event line ─────────────────────────────────────────────────────────────
_AGENT_STYLES = {
    "Planner":     (C.BLUE,    "PLAN"),
    "Developer":   (C.GREEN,   "CODE"),
    "Reviewer":    (C.YELLOW,  "REVIEW"),
    "QA":          (C.MAGENTA, "TEST"),
    "RepoManager": (C.CYAN,    "REPO"),
}

_STATUS_COLORS = {
    "ok":   C.GREEN,
    "fail": C.RED,
    "warn": C.YELLOW,
    "info": C.CYAN,
}

def agent_event(agent: str, event: str, detail: str = "", status: str = "info"):
    color, tag     = _AGENT_STYLES.get(agent, (C.WHITE, agent[:4].upper()))
    status_color   = _STATUS_COLORS.get(status, C.WHITE)

    tag_badge  = c(C.GREY + C.BOLD,      f"[{tag:<6}]")
    agent_str  = c(color + C.BOLD,        f"{agent:<13}")
    event_str  = c(status_color,          f"{event:<20}")
    detail_str = c(C.MUTED,               detail[:52]) if detail else ""

    print(f"  {tag_badge}  {agent_str}  {event_str}  {detail_str}")


# ── Iteration banner ─────────────────────────────────────────────────────────────
def iteration_header(n: int, total: int):
    label = f"  ITERATION {n} / {total}  "
    w     = term_width()
    pad   = max((w - len(label)) // 2, 2)
    line  = (
        c(C.GREY,           "╌" * pad)
        + c(C.YELLOW + C.BOLD, label)
        + c(C.GREY,           "╌" * pad)
    )
    print()
    print(line)
    print()


# ── Goal result ──────────────────────────────────────────────────────────────────
def print_goal_result(result: dict, goal: str):
    success = result.get("status") == "success"
    border  = C.GREEN if success else C.RED
    print()
    thick_divider(border)
    print()
    if success:
        lines = [
            c(C.GREEN + C.BOLD, "  ✓  GOAL COMPLETED SUCCESSFULLY"),
            "",
            c(C.MUTED, "  Goal       : ") + c(C.WHITE, goal[:65]),
            c(C.MUTED, "  Iterations : ") + c(C.WHITE, str(result.get("iterations", "?"))),
            c(C.MUTED, "  Output     : ") + c(C.CYAN,  str(result.get("output_file", "N/A"))),
        ]
        box(lines, title="RESULT", color=C.GREEN)
    else:
        lines = [
            c(C.RED + C.BOLD, "  ✗  GOAL FAILED"),
            "",
            c(C.MUTED,  "  Goal       : ") + c(C.WHITE,  goal[:65]),
            c(C.MUTED,  "  Iterations : ") + c(C.WHITE,  str(result.get("iterations", "?"))),
            "",
            c(C.YELLOW, "  › Check logs\\orchestrator.log for details."),
        ]
        box(lines, title="RESULT", color=C.RED)
    print()
    thick_divider(border)
    print()


# ── Menu ─────────────────────────────────────────────────────────────────────────
def print_menu():
    print_banner()
    thick_divider(C.GREY)
    print()

    entries = [
        ("1", "Submit a goal",   "Build something with AI agents",      C.GREEN),
        ("2", "Launch web UI",   "Dashboard at http://127.0.0.1:5000",  C.CYAN),
        ("3", "Run validation",  "Check all system components",          C.YELLOW),
        ("4", "Exit",            "",                                     C.GREY),
    ]

    for num, title, desc, col in entries:
        badge     = c(C.BG_DARK + col + C.BOLD, f" {num} ")
        title_str = c(C.WHITE + C.BOLD,          f"  {title:<22}")
        desc_str  = c(C.GREY,                    desc)
        print(f"  {badge}{title_str}  {desc_str}")
        print()

    thick_divider(C.GREY)
    print()
    prompt = c(C.MAGENTA + C.BOLD, "  ❯ ") + c(C.WHITE, "Choice: ")
    sys.stdout.write(prompt)
    sys.stdout.flush()


# ── Validation display ────────────────────────────────────────────────────────────
def print_validation_header():
    print_banner()
    section("SELF-VALIDATION", C.CYAN)

def print_validation_result(errors: list):
    print()
    if errors:
        lines = (
            [c(C.RED + C.BOLD, f"  ✗  FAILED — {len(errors)} issue(s)"), ""] +
            [c(C.RED, f"  ✗  {e}") for e in errors]
        )
        box(lines, title="VALIDATION RESULT", color=C.RED)
    else:
        box(
            [
                c(C.GREEN + C.BOLD, "  ✓  ALL CHECKS PASSED"),
                "",
                c(C.MUTED, "  System is ready to run goals."),
            ],
            title="VALIDATION RESULT",
            color=C.GREEN,
        )
    print()


# ── Crash display ─────────────────────────────────────────────────────────────────
def print_crash(tb: str):
    print()
    thick_divider(C.RED)
    print(c(C.RED + C.BOLD, "  ✗  CRASH DETECTED"))
    divider("─", C.RED)
    for line in tb.splitlines():
        print(c(C.GREY, "  │ ") + c(C.WHITE, line))
    thick_divider(C.RED)
    print()
    warn("Check logs\\orchestrator.log for the full trace.")
    print()
