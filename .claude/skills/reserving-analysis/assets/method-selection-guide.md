## Method Selection Guide

### Chain Ladder — Paid

**Appropriate Circumstances:** Stable payment timing and case adequacy; minimal calendar year distortion; reasonable paid credibility by age.

**Triangle Diagnostics to Check:** Paid to incurred ratio early stable; paid link ratios by age stable across periods; closed to reported consistent with history.

**Implications for Selection:** Prefer paid LDFs for early and mid ages; shorten tail if settlements are faster; reduce weight if early paid is weak.

---

### Chain Ladder — Incurred

**Appropriate Circumstances:** Stable case reserve adequacy; early paid sparse but incurred credible; limited one-off reserve actions.

**Triangle Diagnostics to Check:** Incurred minus paid gap stable by age; incurred link ratios stable across periods; case reserve per open steady.

**Implications for Selection:** Prefer incurred LDFs at early ages; cross-check with paid view for tail; avoid when adequacy is changing.

---

### Bornhuetter-Ferguson (BF)

**Appropriate Circumstances:** Unstable early development; thin recent volume or structural change; need to anchor to an external prior.

**Triangle Diagnostics to Check:** Early paid or incurred ratios volatile; counts or mix shifting in recent periods; evidence of reporting or settlement shift.

**Implications for Selection:** Blend prior with development factors; increase prior weight at early ages; phase to CL by later ages.

---

### Cape Cod

**Appropriate Circumstances:** Exposure measure available and reliable; need a data-driven prior by segment; heterogeneous volumes across periods.

**Triangle Diagnostics to Check:** Exposure trends align with counts; loss per unit exposure reasonably stable; limited calendar year distortion.

**Implications for Selection:** Set prior via exposure-based rates; smooth across sparse periods; use CL tail selection after prior.

---

### Berquist-Sherman — Case Adequacy

**Appropriate Circumstances:** Changing case reserve strength; incurred and paid diverge by age; reserve actions suspected.

**Triangle Diagnostics to Check:** Incurred minus paid gap trending; case reserve per open drifting; incurred link ratios shifting.

**Implications for Selection:** Restate incurred to a common adequacy level; then apply CL or BF on the restated series; document the adjustment and its impact.

---

### Berquist-Sherman — Settlement/Closure

**Appropriate Circumstances:** Changing closure speed; paid timing altered by operational changes; reopen activity impacting tails.

**Triangle Diagnostics to Check:** Closed over reported shifting by age; paid link ratios moving earlier or later; open counts duration changing.

**Implications for Selection:** Restate to constant settlement rates; then apply CL or BF on adjusted paid; adjust tail to the new closure pattern.

---

### Frequency-Severity

**Appropriate Circumstances:** Mix or severity changes are material; policy or limit changes impact severity; count frequency moving independently.

**Triangle Diagnostics to Check:** Counts and severity triangles diverge; severity trend by period or calendar year; censoring or large loss effects visible.

**Implications for Selection:** Model counts and severity separately; apply trend and censoring explicitly; recombine to total losses and reserves.

---

### Benktander

**Appropriate Circumstances:** Need an iterative BF-to-CL transition; desire a smoother credibility shift; limited early data but improving at later ages.

**Triangle Diagnostics to Check:** Early ages volatile yet later ages stable; prior credible but not dominant; development factors reliable after mid ages.

**Implications for Selection:** Iterate from BF toward CL with weights; apply higher prior weight early and lower later; useful bridge in change environments.

---

### Mack (Distribution-Free CL)

**Appropriate Circumstances:** Need a reserve variability estimate; classical CL assumptions are acceptable; desire parameter and process MSE.

**Triangle Diagnostics to Check:** Residuals by age roughly homoscedastic; link ratio stability by period reasonable; no strong calendar year bias.

**Implications for Selection:** Use for mean and MSE, not a full distribution; supports interval estimates; pair with tail uncertainty assessment.

---

### Bootstrap ODP

**Appropriate Circumstances:** Need a predictive reserve distribution; over-dispersed Poisson fits increments; desire full stochastic simulation.

**Triangle Diagnostics to Check:** Incremental residuals are ODP-like; limited structural breaks post-cleaning; sufficient data volume by cell.

**Implications for Selection:** Simulate full reserve distribution; stress with alternative tails and trends; report percentiles and TVaR.

---

### Calendar Year Adjusted CL

**Appropriate Circumstances:** Inflation or calendar level effects present; operational shifts by calendar period; need to separate calendar year from accident year effects.

**Triangle Diagnostics to Check:** Calendar heatmaps show drift; recent diagonals systematically high; paid and incurred both trend by calendar year.

**Implications for Selection:** De-trend by calendar year then apply CL; reapply projected calendar year factors; document inflation and operational assumptions.

---

### Reopen/Survival Models

**Appropriate Circumstances:** Material reopen activity at late ages; long-tail lines with reopen risk; closure hazard is changing.

**Triangle Diagnostics to Check:** Closed-then-reopen counts visible; late paid increments elevated; open duration lengthening.

**Implications for Selection:** Model hazard of closure and reopen; layer on top of CL or Frequency-Severity; extend and widen tail factors.

---

### Tail Extrapolation / Curve Fit

**Appropriate Circumstances:** Sparse late development; need an explicit tail beyond the triangle; desire smooth convergence to ultimate.

**Triangle Diagnostics to Check:** Late age link ratios noisy; cumulative approaching asymptote; industry tail references available.

**Implications for Selection:** Fit curve families to late link ratios; blend with industry or expert tails; stress test sensitivity to the tail assumption.

---

### Reinsurance / Severity Censoring

**Appropriate Circumstances:** Attachment changes or large loss censoring present; quota share or excess layers present; gross and net patterns differ.

**Triangle Diagnostics to Check:** Severity capped at attachment; net paid and incurred diverge from gross; large loss triangles informative.

**Implications for Selection:** Apply censoring in the severity model; use net-of-attachment development; set separate CAT and large loss loads.

---