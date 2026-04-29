# Boor tail methods: parameters and when to use them

Source: Joseph Boor, *Estimating Tail Development Factors: What to do When the Triangle Runs Out* (CLRS handout; methods numbered as in that paper). This note summarizes **how the CLI maps to those methods** and **what you must choose deliberately**—there is **no default tail method** in `p05_run_chain_ladder.py`.

## Shared ideas

- **Link ratios (LDFs)** here are the same **volume-weighted** age-to-age factors as in `chain_ladder.link_ratios`.
- **Tail factor** is applied in the code as a **scalar multiplier on last-column ultimates** after standard chain-ladder projection (Boor’s tail is one link-style step to ultimate from the last observed development).
- **Credibility and line of business** matter: Boor stresses that early-period link ratios often reflect reporting and initial case setup, not long-tail settlement—see his “Brief Digression” on activity by maturity. Prefer **mature-only fits** (`--tail-exp-mature-min-t`) when the early pattern is not representative of the tail.

## Method 1 — Bondy (`--tail-method bondy`)

- **What it does:** Uses the **last estimated link ratio** from the triangle as the tail factor (“repeat the last link ratio”).
- **When it can be reasonable:** Short-tail lines or late maturities where the last LDF is already small and stable.
- **Risk:** Long-tail lines with slow LDF decay; often criticized as too thin for distant ultimate.
- **Parameters:** None (last **finite** LDF in the vector).

## Method 2 — Modified Bondy (`--tail-method modified_bondy`)

- **What it does:** Inflates the development portion: **`1 + 2d`** where the last ratio is **`1 + d`**, or optionally **`last_ratio**2` (`--modified-bondy-mode square_ratio`).
- **When:** Same use cases as Bondy, but you want a **more conservative** tail than plain Bondy (still often not “fully conservative” on long tails).
- **Parameters:** `--modified-bondy-mode double_dev | square_ratio`.

## Method 4 — McClenahan paid / exponential decay on synthetic incrementals (`--tail-method mcclenahan_paid`)

- **What it does:** Builds a **synthetic cumulative path** from a base (100) times successive LDFs, takes **incrementals**, estimates a **tail decay ratio `r`** from **late** incremental-to-incremental ratios (only ratios **strictly below 1**), then applies Boor’s **closed-form** tail using monthly decay **`p = r^(1/12)`**.
- **When:** You accept a **parametric decay** on paid-style patterns implied by the **triangle’s LDFs** (not raw paid dollars by period unless your triangle is paid and columns are consistent).
- **Required parameters:** `--tail-m-months` and `--tail-a-months` (evaluation maturity **m** and average reporting lag **a**, in months, per Boor/McClenahan).
- **Optional:** `--tail-mcclenahan-last-n` (how many late decay ratios to average; default 5).
- **Checks:** Requires **`0 < r < 1`** from the data; denominator of the closed form must stay positive—otherwise inputs or the LDF pattern are inconsistent with the model.

## Method 5 — Skurnick (`--tail-method skurnick_paid`)

- **What it does:** Takes **incremental paid** along the **oldest accident year (first row)** of the **cumulative** triangle, fits **`ln(incremental_y) = ln(A) + y ln(r)`** for **`y = 1..Y`**, then applies Boor’s closed form **`tail = (1 - r) / (1 - r - r^Y)`** (same numeric pattern as the **`(1-r)/(1-r-r^n)`** examples in the handout).
- **When:** **Monotone decreasing** incremental paid in the tail of the oldest year; vulnerable to **“hump-shaped”** early payment patterns—Boor recommends **limiting the fit to mature years** (not separately exposed in CLI yet; pre-truncate the triangle columns or prepare a triangle whose oldest row reflects the tail window).
- **Parameters:** None beyond the triangle; **oldest row must have at least two finite cumulatives** and positive incrementals.

## Method 6 — Exponential decay of LDF development portions (`--tail-method exp_dev_ldf`)

- **What it does:** For each used LDF **`f`**, let **`d = f - 1`**. Regress **`ln(d)` on `t`**, where **`t`** is the **1-based** development index aligned to factor columns. **`D = exp(intercept)`**, **`r = exp(slope)`**. Tail either:
  - **Quick:** `1 + D * r^K / (1 - r)` with **`K = --tail-exp-future-periods`** (Boor’s small-`d` shortcut), or
  - **Product:** multiply projected future **`1 + D r^t`** until the development portion is negligible (`--tail-exp-dev-mode product`).
- **Improvement 2 (exact last link):** `--tail-exp-exact-last` rescales the fitted tail using the ratio of **actual** vs **fitted** development portion at the **last observed** period.
- **Improvement 3 (mature-only fit):** `--tail-exp-mature-min-t` restricts regression to **`t >=` that index**.
- **When:** LDF development portions decay roughly **exponentially** in the window you fit; poor fit (systematic residuals) means you should **narrow the fit window** or pick another method.

## Explicit user choices (`none`, `scalar`)

- **`none`:** No tail multiplier (ultimate = chain-ladder ultimate at last development column).
- **`scalar`:** You supply **`--tail-scalar`** explicitly (judgmental or external benchmark).

## Practical workflow

1. Read this reference and pick a **tail-method** consistent with **data shape** (monotone tail vs hump; short vs long tail).
2. Run the CLI with **`--tail-method ...`** and any **required** numeric inputs (McClenahan **m** and **a**; scalar value; optional Method 6 knobs).
3. If Method 6 residuals look poor, retry with **`--tail-exp-mature-min-t`** and/or **`--tail-exp-exact-last`**, or switch method—do not rely on a “default” tail.
