# Creates every uploadable/importable zip in import/.
#
#  import/teamanalyst-plugin-cowork.zip  Claude Cowork plugin (.claude-plugin/, skills/, agents/)
#  import/teamanalyst-plugin-other.zip   Agent Plugins 1.0 folder (plugin.json, skills/) for Cursor,
#                                        Antigravity IDE, and other tools that read that format
#  import/<skill>.zip                    One zip per skill with the skill contents at the zip root,
#                                        for Claude Chat/Desktop and Microsoft Copilot Agent Builder
#
# Fails if the plugin versions differ across manifests.
#
# Usage (run from project root):
#  python create_import_zips.py

import json
import sys
import zipfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SKILLS_DIR = PROJECT_ROOT / "skills"
CLAUDE_PLUGIN_DIR = PROJECT_ROOT / ".claude-plugin"
OUTPUT_DIR = PROJECT_ROOT / "import"
COWORK_ZIP = OUTPUT_DIR / "teamanalyst-plugin-cowork.zip"
OTHER_ZIP = OUTPUT_DIR / "teamanalyst-plugin-other.zip"

VERSION_FILES = [
    "plugin.json",
    ".claude-plugin/plugin.json",
    "gemini-extension.json",
]

EXCLUDE_DIR_NAMES = {"__pycache__", ".pytest_cache"}
EXCLUDE_SUFFIXES = {".pyc"}
EXCLUDE_FILENAMES = {"conftest.py"}


def is_excluded(relative_path: Path):
    return (
        bool(EXCLUDE_DIR_NAMES & set(relative_path.parts[:-1]))
        or relative_path.suffix in EXCLUDE_SUFFIXES
        or relative_path.name in EXCLUDE_FILENAMES
    )


def collect_dir(directory: Path, arc_prefix: str = ""):
    """All shippable files under directory, arcnames relative to it (plus optional prefix)."""
    files = []
    for child in sorted(directory.rglob("*")):
        if not child.is_file():
            continue
        relative_path = child.relative_to(directory)
        if is_excluded(relative_path):
            continue
        files.append((child, arc_prefix + relative_path.as_posix()))
    return files


def check_versions():
    versions = {f: json.loads((PROJECT_ROOT / f).read_text(encoding="utf-8"))["version"] for f in VERSION_FILES}
    market = json.loads((CLAUDE_PLUGIN_DIR / "marketplace.json").read_text(encoding="utf-8"))
    for plugin in market["plugins"]:
        if "version" in plugin:
            versions[".claude-plugin/marketplace.json:" + plugin["name"]] = plugin["version"]
    if len(set(versions.values())) != 1:
        sys.exit(f"ERROR: version mismatch: {versions}")


def collect_cowork_files():
    """Claude plugin layout: selector agents copied to agents/ without the .agent suffix."""
    files = []
    for agent in sorted(SKILLS_DIR.rglob("agents/*.agent.md")):
        files.append((agent, "agents/" + agent.name.replace(".agent.md", ".md")))
    for path, arcname in collect_dir(SKILLS_DIR, "skills/"):
        if path.name.endswith(".agent.md"):
            continue
        files.append((path, arcname))
    # marketplace.json is for repo installs only
    for path, arcname in collect_dir(CLAUDE_PLUGIN_DIR, ".claude-plugin/"):
        if path.name != "marketplace.json":
            files.append((path, arcname))
    return files


def collect_other_files():
    """Agent Plugins 1.0 layout: root plugin.json plus skills/ (agents stay inside their skill)."""
    return [(PROJECT_ROOT / "plugin.json", "plugin.json")] + collect_dir(SKILLS_DIR, "skills/")


def write_zip(output: Path, files):
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zf:
        for abs_path, arcname in files:
            zf.write(abs_path, arcname)
    print(f"Created: {output} ({len(files)} files)")


def main():
    check_versions()
    OUTPUT_DIR.mkdir(exist_ok=True)

    write_zip(COWORK_ZIP, collect_cowork_files())
    write_zip(OTHER_ZIP, collect_other_files())

    skill_dirs = sorted(p.parent for p in SKILLS_DIR.glob("*/SKILL.md"))
    for skill_dir in skill_dirs:
        write_zip(OUTPUT_DIR / f"{skill_dir.name}.zip", collect_dir(skill_dir))

    print(f"\nTotal zips: {2 + len(skill_dirs)}")


if __name__ == "__main__":
    main()
