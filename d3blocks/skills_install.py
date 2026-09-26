"""Manage the d3blocks Agent Skill."""
# ------------------------------------
# Name        : skills_install.py
# Author      : E.Taskesen
# Contact     : erdogant@gmail.com
# Licence     : See licences
# ------------------------------------

from pathlib import Path
import argparse
import platform
import shutil
import sys


KNOWN_HARNESSES = {
    "claude": ".claude",
    "opencode": ".opencode",
    "agents": ".agents",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def skill_path():
    """Return the path to the bundled d3blocks Agent Skill."""
    return Path(__file__).resolve().parent / "skills" / "d3blocks"


def _global_root() -> Path:
    """Return the OS-appropriate home directory for global installs.

    - Linux / macOS : ``~``  (``Path.home()``)
    - Windows       : ``%USERPROFILE%``  (also ``Path.home()`` on modern Python,
                      but we fall back to the env-var explicitly for clarity)
    """
    return Path.home()


def _detect_installed_harnesses(root: Path) -> list[str]:
    """Return the names of harnesses whose skill directories already exist
    under *root*.

    Only the harnesses listed in ``KNOWN_HARNESSES`` are considered.  A
    harness is "installed" when its top-level dot-directory exists (e.g.
    ``~/.claude``); the ``skills/`` sub-directory need not be present yet.
    """
    found = []
    for name, dotdir in KNOWN_HARNESSES.items():
        if (root / dotdir).exists():
            found.append(name)
    return found


# ---------------------------------------------------------------------------
# Core install logic
# ---------------------------------------------------------------------------

def install_skill(harness: str = "claude", *, global_install: bool = False) -> Path:
    """Install the d3blocks Agent Skill.

    Parameters
    ----------
    harness : str, default='claude'
        Name of the AI coding harness.  The skill is installed to::

            [root]/.<harness>/skills/d3blocks/

        where *root* is the current working directory for a local install or
        the user home directory for a global install.  Any harness name is
        accepted; unknown names produce a warning.

    global_install : bool, default=False
        When ``True``, install into the user's home directory instead of the
        current working directory.

    Returns
    -------
    pathlib.Path
        The resolved destination directory.
    """
    source = skill_path()
    if not source.exists():
        raise FileNotFoundError(f"Bundled d3blocks skill not found: {source}")

    # Strip any leading dot — we add it ourselves.
    harness = harness.lstrip(".")

    root = _global_root() if global_install else Path.cwd()
    destination = root / f".{harness}" / "skills" / "d3blocks"

    if harness not in KNOWN_HARNESSES:
        print(
            f"Warning: '{harness}' is not a known AI harness. "
            f"Installing anyway to:\n{destination}"
        )

    destination.parent.mkdir(parents=True, exist_ok=True)

    if destination.exists():
        shutil.rmtree(destination)

    shutil.copytree(source, destination)

    scope = "globally" if global_install else "locally"
    print(f"d3blocks skill installed {scope} to:\n{destination}")
    return destination


def install_skill_auto(global_install: bool = False) -> list[Path]:
    """Auto-detect installed harnesses and install the skill into all of them.

    Detection checks which ``.<harness>`` directories exist under *root*
    (the user home directory for a global install, or the current working
    directory for a local install).  If none are found the function exits
    with a helpful message rather than silently doing nothing.

    Parameters
    ----------
    global_install : bool, default=False
        When ``True``, detect and install relative to the user home directory.

    Returns
    -------
    list of pathlib.Path
        Destination directories that were written.
    """
    root = _global_root() if global_install else Path.cwd()
    scope_label = f"global ({root})" if global_install else f"local ({root})"

    detected = _detect_installed_harnesses(root)

    if not detected:
        known = ", ".join(KNOWN_HARNESSES)
        print(
            f"No known AI harness directories found under {root}.\n"
            f"Looked for: {known}\n"
            f"Use --harness <name> to install for a specific harness."
        )
        return []

    print(f"Auto-detected harnesses ({scope_label}): {', '.join(detected)}")

    destinations = []
    for harness in detected:
        dest = install_skill(harness, global_install=global_install)
        destinations.append(dest)

    return destinations


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    """Command-line interface for d3blocks."""
    parser = argparse.ArgumentParser(
        prog="d3blocks",
        description="d3blocks command-line interface.",
    )

    subparsers = parser.add_subparsers(dest="command")

    # ------------------------------------------------------------------
    # d3blocks install ...
    # ------------------------------------------------------------------
    install_parser = subparsers.add_parser(
        "install",
        help="Install d3blocks components.",
    )

    install_subparsers = install_parser.add_subparsers(
        dest="install_command",
    )

    skill_install_parser = install_subparsers.add_parser(
        "skill",
        help="Install the d3blocks Agent Skill.",
    )

    skill_install_parser.add_argument(
        "--harness",
        default=None,
        metavar="NAME",
        help=(
            "AI coding harness to install into (e.g. claude, opencode, agents). "
            "Omit to use --auto detection."
        ),
    )

    skill_install_parser.add_argument(
        "--global",
        dest="global_install",
        action="store_true",
        default=False,
        help=(
            "Install into the user home directory (~/.claude/skills/d3blocks/) "
            "instead of the current project directory. "
            f"Detected home: {_global_root()}"
        ),
    )

    skill_install_parser.add_argument(
        "--auto",
        action="store_true",
        default=False,
        help=(
            "Auto-detect all installed AI harnesses and install the skill into "
            "each one. Uses the current directory by default; combine with "
            "--global to detect and install into the home directory."
        ),
    )

    # ------------------------------------------------------------------
    # d3blocks skill
    # ------------------------------------------------------------------
    skill_parser = subparsers.add_parser(
        "skill",
        help="Manage the d3blocks Agent Skill.",
    )

    skill_subparsers = skill_parser.add_subparsers(
        dest="skill_command",
    )

    skill_subparsers.add_parser(
        "path",
        help="Show the path to the bundled d3blocks Agent Skill.",
    )

    args = parser.parse_args()

    # ------------------------------------------------------------------
    # Dispatch
    # ------------------------------------------------------------------

    # d3blocks install skill
    if args.command == "install":
        if args.install_command == "skill":
            if args.auto:
                install_skill_auto(global_install=args.global_install)
            else:
                harness = args.harness or "claude"
                install_skill(harness, global_install=args.global_install)
        else:
            install_parser.print_help()

    # d3blocks skill path
    elif args.command == "skill":
        if args.skill_command == "path":
            print(skill_path())
        else:
            skill_parser.print_help()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
