"""
pytest configuration and shared fixtures.
"""
import sys
from pathlib import Path

# Add project root and skills directories to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Add individual skill directories for easier imports
skills_dir = project_root / ".claude" / "skills"
for skill_path in skills_dir.iterdir():
    if skill_path.is_dir():
        sys.path.insert(0, str(skill_path))

# pytest fixtures can be added here if needed in the future