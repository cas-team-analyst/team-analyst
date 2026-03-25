# Project Metadata

| Field | Value |
|---|---|
| Project Name | Demo 2 - Make Selections |
| Analysis Date | 2026-03-25 |
| Analyst | Claude (AI) |
| Data Source | Claude Agent Triangles 5 Demo Data.xlsx |
| Lines of Business | Single (unnamed) |
| Accident Year Type | Fiscal |
| Accident Years | 2008 - 2025 (18 years) |
| Development Ages | 15, 27, 39, ..., 219 months (18 ages, 12-month intervals starting at 15) |
| Evaluation Date | 219 months from AY 2008 start |
| Methods | Chain Ladder |

# Data Files

## Claude Agent Triangles 5 Demo Data.xlsx

**Sheets:**

| Sheet | Description | Rows | Columns |
|---|---|---|---|
| Inc | Incurred Losses triangle | 18 AYs + prior selections row | 18 development ages |
| Pd | Paid Losses triangle | 18 AYs + prior selections row | 18 development ages |
| Count | Claim Count triangle | 18 AYs + prior selections row | 18 development ages |

**Key Details:**
- Accident years 2008–2025 (fiscal)
- Development ages in months: 15, 27, 39, 51, 63, 75, 87, 99, 111, 123, 135, 147, 159, 171, 183, 195, 207, 219
- Each sheet contains a "Prior Age-to-Age Selections" row at the bottom with prior LDF selections
- Triangle is upper-left filled (most recent years have fewer development periods)
