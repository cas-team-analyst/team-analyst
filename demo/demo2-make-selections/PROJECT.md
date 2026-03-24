# Project Metadata
- Client: (to be confirmed)
- Line of Business: Workers' Compensation (WC)
- Risk Type: Lots of clerical, relatively long-tailed
- Payroll Range: $100M-$500M
- Evaluation Date: 12/31/2024
- Accident Periods: 2001-2024 (25 years)
- Development Ages: 11, 23, 35, ..., 287 months (annual, 25 ages)

# Contacts/Stakeholders
- *To be documented*

# Special Considerations
- *To be documented during planning phase*

# Data
| File Name | Description | Location | Special Notes |
|-----------|-------------|----------|---------------|
| Triangle Examples 1.xlsx | WC loss development triangles (paid, incurred, counts) | data/ | 4 sheets; annual evaluations 2001-2024 |

# File Summaries

## Triangle Examples 1.xlsx

**Sheets:** Tri 1, Paid 1, Inc 1, Ct 1

### Sheet: Tri 1 - Metadata
- Describes the dataset: Line = WC, Risk type = lots of clerical (relatively long-tailed), Payroll range = $100M-$500M

### Sheet: Paid 1 - Paid Loss Triangle
- Shape: 25 accident years (2001-2024) x 25 development ages (11 to 287 months)
- Row header column: "Age of Evaluation" / "Accident Year"
- Values: cumulative paid losses in dollars (range ~$300K at age 11 up to ~$3M at maturity)
- Standard upper-left triangle format (nulls in future evaluations)

### Sheet: Inc 1 - Incurred Loss Triangle
- Same structure as Paid 1 (25 AYs x 25 dev ages)
- Values: cumulative incurred losses in dollars (slightly higher than paid, range ~$450K-$3.2M)

### Sheet: Ct 1 - Claim Count Triangle
- Same structure (25 AYs x 25 dev ages)
- Values: cumulative claim counts (range ~260-700 claims per AY)
- Note: header row not detected by parser (uses generated column names), but structure mirrors Paid/Inc sheets
