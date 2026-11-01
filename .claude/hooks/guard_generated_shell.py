#!/usr/bin/env python3
"""PreToolUse hook (Bash): refuse shell writes to data/ and figures/.

The editor-tool guard (guard_generated.py) cannot see `printf > data/x`,
`sed -i ... data/x` or `cp y figures/`. This hook tokenises the command with
shlex, splits it into simple commands, and blocks:

- a redirection (`>`, `>>`) whose target is under data/ or figures/;
- `tee`, `rm`, `truncate`, `touch`, `shred` with such an argument;
- `sed`/`perl` with an in-place flag and such an argument;
- `cp`, `mv`, `install`, `ln`, `rsync` whose destination (last argument) is
  under data/ or figures/;
- `dd` with `of=` such a path.

Matching works on tokens, so a quoted string that merely mentions data/ -- a
commit message, an echo -- is one argument of an unrelated command and is
ignored. Running a phase script (scripts/run_*.py) is how those files are
meant to change and is never blocked.

This is not a sandbox: a write inside an interpreter one-liner
(`python -c "open('data/x','w')"`) is not caught. It closes the casual route;
review closes the rest.
"""
import json
import os
import re
import shlex
import sys

GENERATED = re.compile(r"^(?:\./)?(?:data|figures)/")
SEPARATORS = {"&&", "||", ";", "|", "&", "(", ")", ";;", "|&"}
REDIRECTS = {">", ">>", ">|", "&>", "&>>"}
CLOBBER = {"tee", "rm", "truncate", "touch", "shred"}
COPY_INTO = {"cp", "mv", "install", "ln", "rsync"}
IN_PLACE = {"sed", "perl"}


def generated(token: str) -> bool:
    """True if `token` names a path under data/ or figures/."""
    return bool(GENERATED.match(token))


def refusal(command: str) -> str | None:
    """Return the offending fragment if `command` writes generated output.

    Args:
        command: the shell command line the Bash tool is about to run.

    Returns:
        A short description of the write, or None if there is none. A command
        shlex cannot parse returns None: it would fail in the shell as well.
    """
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=True)
        lexer.whitespace_split = True
        tokens = list(lexer)
    except ValueError:
        return None

    simple, current = [], []
    for token in tokens:
        if token in SEPARATORS:
            simple.append(current)
            current = []
        else:
            current.append(token)
    simple.append(current)

    for argv in simple:
        if not argv:
            continue
        for i, token in enumerate(argv[:-1]):
            if token in REDIRECTS and generated(argv[i + 1]):
                return f"{token} {argv[i + 1]}"
        words = [t for t in argv if t not in REDIRECTS]
        name = os.path.basename(words[0]) if words else ""
        if any(re.search(r"\bscripts/run_\w+\.py$", w) for w in words):
            continue
        args = words[1:]
        targets = [a for a in args if generated(a)]
        if name in CLOBBER and targets:
            return f"{name} {targets[0]}"
        if name in IN_PLACE and targets and any(
            re.fullmatch(r"-\w*i\S*|--in-place\S*", a) for a in args
        ):
            return f"{name} -i {targets[0]}"
        if name in COPY_INTO:
            operands = [a for a in args if not a.startswith("-")]
            if len(operands) >= 2 and generated(operands[-1]):
                return f"{name} ... {operands[-1]}"
        if name == "dd":
            for a in args:
                if a.startswith("of=") and generated(a[3:]):
                    return f"dd {a}"
    return None


payload = json.load(sys.stdin)
found = refusal(payload.get("tool_input", {}).get("command", ""))
if found:
    print(
        f"Refused: `{found}` writes to generated output under data/ or "
        "figures/. Regenerate it with the script recorded for it in "
        "data/manifest.json (see the rc-numerics skill).",
        file=sys.stderr,
    )
    sys.exit(2)
