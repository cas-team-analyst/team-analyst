# Project Metadata
- Client: Example / Training Data
- Line of Business: Workers' Compensation
- Risk Type: Lots of clerical, relatively low hazard
- Payroll Range: $100M–$500M
- Evaluation Date: 12/31/2024
- Accident Periods: 2001–2024 (24 accident years)
- Development Ages: 11–287 months (24 ages, roughly annual)

# Contacts/Stakeholders
- *To be documented*

# Special Considerations
- *To be documented during planning phase*

# Data
| File Name | Description | Location | Special Notes |
|-----------|-------------|----------|---------------|
| Triangle Examples 1.xlsx | WC loss development triangles | data/ | 4 sheets: metadata (Tri 1), paid losses (Paid 1), incurred losses (Inc 1), claim counts (Ct 1) |

# File Summaries

## Triangle Examples 1.xlsx

**Sheets:**

| Sheet | Contents | Shape | Notes |
|-------|----------|-------|-------|
| Tri 1 | Metadata | 3 rows x 2 cols | Line: WC, Risk: clerical/low-hazard, Payroll: $100M-$500M |
| Paid 1 | Paid loss triangle | 24 AYs x 24 ages | AY 2001–2024, ages 11–287 months |
| Inc 1 | Incurred (reported) loss triangle | 24 AYs x 24 ages | Same structure as Paid 1 |
| Ct 1 | Claim count triangle | 24 AYs x 24 ages | Same structure, values are claim counts |

**Structure:** Standard upper-left development triangle. First column = Accident Year (2001–2024). Column headers = development ages in months (11, 23, 35, ..., 287). Null values fill the lower-right of each triangle (not yet developed).
