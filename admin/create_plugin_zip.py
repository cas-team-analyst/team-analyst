# Creates team-analyst-plugin.zip in the .claude-plugin folder.
#
# Usage (run from project root):
#   .venv\Scripts\Activate.ps1; python admin/create_plugin_zip.py

import zipfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PLUGIN_DIR = PROJECT_ROOT / ".claude-plugin"
OUTPUT_ZIP = PLUGIN_DIR / "team-analyst-plugin.zip"
ZIP_FILENAME = "team-analyst-plugin.zip"

TOP_LEVEL_FILES = [
    "AGENTS.md",
    "AUDIT.md",
    "PROJECT.md",
    "REPLICATE.md",
    "requirements.txt"
]

EXTRA_DIRS = [
    ".claude",
    ".claude-plugin",
]


def collect_files():
    files = []

    for name in TOP_LEVEL_FILES:
        path = PROJECT_ROOT / name
        if path.exists():
            files.append((path, name))
        else:
            print(f"WARNING: {name} not found, skipping")

    # Add skills directory, mapping .claude/skills to skills/ in the zip
    skills_dir = PROJECT_ROOT / ".claude" / "skills"
    if skills_dir.exists():
        for child in sorted(skills_dir.rglob("*")):
            if child.is_file():
                arcname = "skills/" + child.relative_to(skills_dir).as_posix()
                files.append((child, arcname))
    else:
        print(f"WARNING: .claude/skills/ not found, skipping")

    # Add agents directory, mapping .claude/agents to agents/ in the zip
    agents_dir = PROJECT_ROOT / ".claude" / "agents"
    if agents_dir.exists():
        for child in sorted(agents_dir.rglob("*")):
            if child.is_file():
                arcname = "agents/" + child.relative_to(agents_dir).as_posix()
                files.append((child, arcname))
    else:
        print(f"WARNING: .claude/agents/ not found, skipping")

    # Add .claude-plugin directory (excluding the output zip file)
    plugin_dir = PROJECT_ROOT / ".claude-plugin"
    if plugin_dir.exists():
        for child in sorted(plugin_dir.rglob("*")):
            if child.is_file() and child.name != ZIP_FILENAME:
                arcname = child.relative_to(PROJECT_ROOT).as_posix()
                files.append((child, arcname))
    else:
        print(f"WARNING: .claude-plugin/ not found, skipping")

    return files


def main():
    # Ensure the .claude-plugin directory exists
    PLUGIN_DIR.mkdir(exist_ok=True)
    
    files = collect_files()

    with zipfile.ZipFile(OUTPUT_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
        for abs_path, arcname in files:
            zf.write(abs_path, arcname)
            print(f"  added: {arcname}")

    print(f"\nCreated: {OUTPUT_ZIP}")
    print(f"Total files: {len(files)}")


if __name__ == "__main__":
    main()
