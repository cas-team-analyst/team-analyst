---
name: python
description: Guide for Python development in this project. Use any time you write Python.
---

# Writing Python

Guide for Python development in this project.

## Quick Reference

**Guidelines:**
- Read files as all strings and convert later if you need to.
- Use openpyxl to manipulate Excel files.
- Use code from skills whenever possible.

**Code organization:**
- Imports at top
- Main logic first, helpers towards bottom (read main logic first)
- Include usage note at top showing how to run from project root and how to run related tests if applicable

**Critical rules:**
- **NEVER use try/catch, fallbacks, or defaults** - Create visible failures with full stack traces
- **Replace Unicode with ASCII** - Avoid encoding issues on Windows terminals
- **No empty `__init__.py`** unless necessary

**Package Installation:**
- Always use PowerShell commands instead of VS Code extensions or MCP. 
- Always use .venv.
- Use these steps: 1. Add it to `requirements.txt`; 2. Run `& .venv/Scripts/Activate.ps1; pip-audit -r requirements.txt` to check for vulnerabilities (do not install packages with known high vulnerabilities); 3. Run `& .venv/Scripts/Activate.ps1; pip install -r requirements.txt` to do the install.

**Running Python:**
- Always activate .venv first and run from the project root: `& .venv/Scripts/Activate.ps1; path-to-file/python script.py`
- Create temporary test scripts instead of complex PowerShell commands (to avoid syntax errors which are very difficult to avoid), delete after use.

**Testing:**
- If file has test reference at top and you change it, run tests
- Always address warnings
- Add `pytest` tests as appropriate.

# Running Python

- If you are going to run python code, create a script to avoid syntax errors. 
- Remove any test or debug scripts when you are done with them, unless you were specifically asked to create the test. 
- Make sure to activate the virtual environment at .venv before running python scripts; `& ".venv\Scripts\Activate.ps1"; python my_script.py`
- To escape `"`, use `""`, not `\"`.
