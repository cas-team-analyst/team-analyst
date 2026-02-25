---
name: reserving workflow
description: Perform steps to complete actuarial reserving analysis, beginning with data provided by the user.
---
# Reserving Workflow Skill

This skill guides the agent through a complete actuarial reserving analysis, starting from validated data provided by the user and producing reserve estimates using standard actuarial methods.

## Instructions

### Step 1 — Load and Validate Data

Follow all steps in `.claude/skills/validate-data/SKILL.md` to request data from the user and validate it. Complete every step in that skill (load, identify format, check format, identify available data elements, and the appropriate validation path — loss run or triangle) before proceeding.

Once the user has confirmed the data summary at the end of the validate-data skill, return here and continue with Step 2.

---

### Step 2 — Extract Canonical Format

Follow all steps in `.claude/skills/extract-canonical/SKILL.md` to convert the validated data into a canonical long-format CSV, store its metadata, and extract the latest diagonal.

#### 2a — Canonical Extraction (`assets/1a-extract-triangle.py` / `1b-extract-loss-run.py`)

Run the appropriate substep based on the data format confirmed in Step 1.

- **Triangle:** Use the **original input file** if cumulative, or the **`-cumulative` file** from validate-data Step 6 if incremental. Use `extract_canonical_from_triangles()`.
- **Loss Run:** Use the column mapping resolved during validate-data Step 5. Use `extract_canonical_from_loss_run()`.

The output is saved to `{stem}-canonical.csv`. Confirm the path to the user and store it.

#### 2b — Store Metadata (`assets/2-store-metadata.py`)

Gather the following from the user, asking each question separately:
1. **Valuation date** (e.g. "2024-12-31")
2. **Line of business** (e.g. "Workers Compensation")
3. **Specific coverage** (if applicable, else "N/A")
4. **Loss currency** (e.g. "USD")

Call `store_metadata()` with these values. If the valuation date check is inconsistent, ask the user to confirm or correct it. Store the metadata path.

#### 2c — Extract Diagonal (`assets/3-extract-diagonal.py`)

Extract the latest diagonal for all available measures from the canonical CSV using `extract_diagonal()`.

Confirm to the user:
> "I've extracted the latest diagonal for **{measures}** and saved it to **{output_path}**. This will be our starting point for the actuarial projections."

Once complete, proceed to Step 3. (Note: Step 3 will cover performing the actuarial analysis).
