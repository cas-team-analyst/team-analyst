# Creates team-analyst-plugin.zip in the .claude-plugin folder.
#
# Usage (run from project root):
#  `python plugins/create_plugin_cowork.py

import zipfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PLUGIN_DIR = PROJECT_ROOT / ".claude-plugin"
OUTPUT_DIR = PROJECT_ROOT / "plugins"
OUTPUT_ZIP = OUTPUT_DIR / "teamanalyst-cowork.zip"
ZIP_FILENAME = "teamanalyst-cowork.zip"

TOP_LEVEL_FILES = []

EXTRA_DIRS = [
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

    # Add skills directory
    skills_dir = PROJECT_ROOT / "skills"
    if skills_dir.exists():
        for child in sorted(skills_dir.rglob("*")):
            if child.is_file():
                # Skip improve-agent and python skill folders
                relative_path = child.relative_to(skills_dir)
                if relative_path.parts[0] in ("improve-agent", "python"):
                    continue
                arcname = "skills/" + relative_path.as_posix()
                files.append((child, arcname))
    else:
        print(f"WARNING: skills/ not found, skipping")

    # Add .claude-plugin directory (excluding marketplace.json and the output zip file)
    plugin_dir = PROJECT_ROOT / ".claude-plugin"
    if plugin_dir.exists():
        for child in sorted(plugin_dir.rglob("*")):
            if child.is_file() and child.name not in (ZIP_FILENAME, "marketplace.json"):
                arcname = child.relative_to(PROJECT_ROOT).as_posix()
                files.append((child, arcname))
    else:
        print(f"WARNING: .claude-plugin/ not found, skipping")

    return files


def main():
    # Ensure the output directory exists
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    files = collect_files()

    with zipfile.ZipFile(OUTPUT_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
        for abs_path, arcname in files:
            zf.write(abs_path, arcname)
            print(f"  added: {arcname}")

    print(f"\nCreated: {OUTPUT_ZIP}")
    print(f"Total files: {len(files)}")


if __name__ == "__main__":
    main()
