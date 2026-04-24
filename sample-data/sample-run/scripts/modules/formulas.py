import re

# Regex for sheet refs in formulas:
#   'Sheet Name'!   — quoted (required when name has space/hyphen/etc)
#   SheetName!      — unquoted (alphanumeric + underscore only)
# Quoted names may contain escaped quotes (''), but we ignore that edge case here.
_QUOTED_SHEET_REF = re.compile(r"'([^'!]+)'!")
_UNQUOTED_SHEET_REF = re.compile(r"(?<![A-Za-z0-9_'\"\]])([A-Za-z_][A-Za-z0-9_]*)!")

def rewrite_formula_sheet_refs(formula, rename_map):
    """
    Rewrite sheet refs in a formula string per rename_map {old_name: new_name}.
    Quoted refs become 'new name'!; unquoted refs become 'new name'! if new name
    contains special chars, else new_name! directly.
    """
    if not isinstance(formula, str) or not formula.startswith("="):
        return formula

    def _quote_if_needed(name):
        # Excel requires quoting when sheet name contains anything other than
        # letters, digits, or underscores.
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", name):
            return name
        return f"'{name}'"

    def _quoted_sub(m):
        old = m.group(1)
        new = rename_map.get(old, old)
        return f"{_quote_if_needed(new)}!"

    def _unquoted_sub(m):
        old = m.group(1)
        new = rename_map.get(old, old)
        return f"{_quote_if_needed(new)}!"

    result = _QUOTED_SHEET_REF.sub(_quoted_sub, formula)
    result = _UNQUOTED_SHEET_REF.sub(_unquoted_sub, result)
    return result
