# Creates one zip per skill folder in skills/, placed in skills-import/.
# Each zip contains the skill folder's contents at the zip root (e.g. SKILL.md,
# not reserving-analysis/SKILL.md) so it can be uploaded directly as a Claude
# Skill in Claude Chat (desktop or web).
#
# Usage (run from project root):
#  python skills-import/create_skills_zips.py

import zipfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = PROJECT_ROOT / "skills"
OUTPUT_DIR = Path(__file__).resolve().parent

EXCLUDE_DIR_NAMES = {"__pycache__", ".pytest_cache"}
EXCLUDE_SUFFIXES = {".pyc"}
EXCLUDE_FILENAMES = {"conftest.py"}


def collect_skill_dirs():
    return sorted(p.parent for p in SKILLS_DIR.glob("*/SKILL.md"))


def collect_files(skill_dir: Path):
    files = []
    for child in sorted(skill_dir.rglob("*")):
        if not child.is_file():
            continue
        if child.suffix in EXCLUDE_SUFFIXES:
            continue
        if child.name in EXCLUDE_FILENAMES:
            continue
        if EXCLUDE_DIR_NAMES & set(child.relative_to(skill_dir).parts[:-1]):
            continue
        arcname = child.relative_to(skill_dir).as_posix()
        files.append((child, arcname))
    return files


def main():
    skill_dirs = collect_skill_dirs()

    for skill_dir in skill_dirs:
        output_zip = OUTPUT_DIR / f"{skill_dir.name}.zip"
        files = collect_files(skill_dir)

        with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zf:
            for abs_path, arcname in files:
                zf.write(abs_path, arcname)

        print(f"Created: {output_zip} ({len(files)} files)")

    print(f"\nTotal skill zips: {len(skill_dirs)}")


if __name__ == "__main__":
    main()
