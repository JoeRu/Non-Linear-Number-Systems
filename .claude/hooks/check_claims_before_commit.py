#!/usr/bin/env python3
"""PreToolUse hook: run scripts/check_claims.py before any `git commit`.

The claim ledger is cheap to validate and CI would reject the push anyway;
catching it here keeps a broken ledger out of the commit history.

What is validated is what the commit records: the index, exported to a
temporary tree with `git checkout-index`. Only `git commit -a`/`--all`, or a
commit naming paths, takes content from the working tree, and then the
working tree is validated instead.

Detection parses the command with shlex, so quoted option values containing
spaces (`git -C "/a b" commit`, `git -c 'user.name=A B' commit`) are seen. A
command shlex cannot parse is checked whenever it mentions both `git` and
`commit`: an unparseable command fails towards validating, not skipping.
"""
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path

# Global git options that consume the following token as their value.
GIT_OPTS_WITH_VALUE = {"-C", "-c", "--git-dir", "--work-tree", "--namespace",
                       "--exec-path", "--super-prefix", "--config-env"}
SHELL_SEPARATORS = {"&&", "||", ";", "|", "&", "(", ")", ";;", "|&"}


def commit_invocations(command: str) -> list[list[str]] | None:
    """Return the argument lists of every `git ... commit ...` in `command`.

    Args:
        command: the shell command line the Bash tool is about to run.

    Returns:
        One list per commit invocation holding the arguments after `commit`,
        or None if the command could not be tokenised.
    """
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=True)
        lexer.whitespace_split = True
        tokens = list(lexer)
    except ValueError:
        return None
    found = []
    i = 0
    while i < len(tokens):
        if os.path.basename(tokens[i]) != "git":
            i += 1
            continue
        j = i + 1
        while j < len(tokens) and tokens[j].startswith("-"):
            j += 2 if tokens[j] in GIT_OPTS_WITH_VALUE else 1
        if j < len(tokens) and tokens[j] == "commit":
            k = j + 1
            while k < len(tokens) and tokens[k] not in SHELL_SEPARATORS:
                k += 1
            found.append(tokens[j + 1:k])
        i = j + 1
    return found


def takes_working_tree(args: list[str]) -> bool:
    """True when a commit's content comes from the working tree, not the index.

    Args:
        args: the arguments following `commit`.

    Returns:
        True for `-a`/`--all`/`--include`/`--only`, a combined short flag
        containing `a`, or explicit pathspecs.
    """
    takes_value = {"-m", "-F", "-C", "-c", "-t", "--author", "--date",
                   "--fixup", "--squash", "--cleanup", "--file", "--message",
                   "--reuse-message", "--reedit-message", "--template"}
    skip = False
    for arg in args:
        if skip:
            skip = False
            continue
        if arg == "--":
            return True
        if arg in takes_value:
            skip = True
        elif arg in ("--all", "--include", "--only", "-i", "-o"):
            return True
        elif re.fullmatch(r"-[a-zA-Z]+", arg) and "a" in arg[1:] and not arg.startswith("-m"):
            return True
        elif not arg.startswith("-"):
            return True  # a pathspec
    return False


def run_check(root: Path, python: str, tree: Path) -> subprocess.CompletedProcess:
    """Run the claim validator against `tree`, from inside it."""
    return subprocess.run([python, "scripts/check_claims.py"], cwd=tree,
                          capture_output=True, text=True)


payload = json.load(sys.stdin)
command = payload.get("tool_input", {}).get("command", "")
invocations = commit_invocations(command)
if invocations is None:
    if not (re.search(r"\bgit\b", command) and re.search(r"\bcommit\b", command)):
        sys.exit(0)
    invocations = [["-a"]]  # unparseable: validate the most permissive source
if not invocations:
    sys.exit(0)

root = Path(os.environ.get("CLAUDE_PROJECT_DIR", payload.get("cwd", "."))).resolve()
venv_python = root / ".venv" / "bin" / "python"
python = str(venv_python) if venv_python.exists() else sys.executable

if any(takes_working_tree(args) for args in invocations):
    proc = run_check(root, python, root)
    source = "working tree"
else:
    with tempfile.TemporaryDirectory(prefix="claims-index-") as tmp:
        subprocess.run(["git", "-C", str(root), "checkout-index", "-a",
                        f"--prefix={tmp}/"], check=True)
        proc = run_check(root, python, Path(tmp))
    source = "staged index"

if proc.returncode != 0:
    print(
        f"scripts/check_claims.py failed on the {source}; fix the claim ledger "
        "before committing:\n" + (proc.stdout + proc.stderr)[-6000:],
        file=sys.stderr,
    )
    sys.exit(2)
