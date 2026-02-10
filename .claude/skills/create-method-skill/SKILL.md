---
name: create-method-skill
description: Guide for creating new actuarial reserving method skills. Use this when asked to create a skill for a new reserving method (e.g., Cape Cod, Expected Loss Ratio, Frequency/Severity, etc.). Provides the standard template and structure for method skills to ensure consistency and completeness.
---

# Create Actuarial Reserving Method Skill

Guide for creating new skills that document actuarial loss reserving methods. This ensures consistency across method skills and comprehensive coverage of all necessary components.

## Quick Reference

**When to create a method skill:**
- Adding a new reserving method to the study (Cape Cod, Expected Loss Ratio, Frequency/Severity, etc.)
- Documenting a specialized technique (Large Loss Adjustments, Trend & Development, etc.)
- Creating method-specific guidance for the reserving workflow

**Standard method skill structure:**
1. Quick Reference (overview, required inputs, outputs, packages)
2. Detailed Methodology (step-by-step with data requirements)
3. Python Implementation (code samples with full class)
4. Outputs and Selection Process (how to create candidates)
5. Diagnostic Displays (visualization code)
6. Progress Tracking Template (copy-paste ready for PROGRESS.md)
7. Actuarial Selections Required (decision points with guidance)
8. Integration guidance (how method fits in overall study)
9. Limitations and considerations
10. References

**Key components every method skill needs:**
- Clear description of the method and when to use it
- Data requirements (raw and processed formats)
- Python implementation with working code sample
- Selection candidate generation
- Progress tracking template
- Actuarial selection guidance (critical!)
- Documentation requirements

---

## When to Create a Method Skill

Create a new method skill when:

1. **Adding a new reserving method** to the standard toolkit
   - Examples: Cape Cod, Expected Loss Ratio, Frequency/Severity, Incremental Loss Ratio
   
2. **Documenting a specialized technique** used in reserving
   - Examples: Large Loss Adjustments, Trend & Development, Loss Ratio Method
   
3. **The method has specific steps** that need to be followed consistently
   
4. **The method requires actuarial selections** that need guidance
   
5. **Python code samples** would be helpful for implementation

Do NOT create a method skill when:
- The technique is too simple (use CLAUDE.md memory instead)
- It's a general data processing step (include in main workflow)
- It's specific to one project only (document in project README)

---

## Standard Method Skill Structure

### File Organization

```
.claude/skills/METHOD-NAME/
├── SKILL.md                 # Main skill file (required)
├── examples/                # Optional: example input/output files
│   ├── sample_data.csv
│   └── sample_output.xlsx
└── templates/               # Optional: templates for documentation
    └── selection_memo.md
```

### SKILL.md Frontmatter Template

```yaml
---
name: method-name
description: Guide for applying the [METHOD NAME] for actuarial loss reserving. Use this when asked to calculate ultimate losses using [method abbreviation], [key use case 1], [key use case 2], or [when to use this method vs others].
---
```

**Naming convention:** 
- Use lowercase with hyphens
- Be descriptive: `cape-cod-method`, `expected-loss-ratio-method`
- Include "method" in the name for clarity

**Description tips:**
- Start with "Guide for applying..."
- Include method abbreviation if commonly used
- List 2-4 specific triggers when Claude should use this skill
- Mention key differentiators from other methods

---

## Required Sections

### Section 1: Title and Introduction (2-4 paragraphs)

```markdown
# [Method Name]

[One paragraph describing what the method is and its core principle]

**Core Principle:** [One sentence explaining the fundamental concept]

[Optional: One paragraph on history/context if relevant]
```

**Example:**
```markdown
# Cape Cod Method

The Cape Cod method is a loss reserving technique that calculates a priori expected ultimate losses based on the relationship between actual reported losses and exposure. It combines aspects of the Bornhuetter-Ferguson and Expected Loss Ratio methods, deriving an implied expected loss ratio from the data itself rather than requiring an external estimate.

**Core Principle:** Use the relationship between reported losses and exposure to estimate an on-level expected loss ratio, then apply this to all accident years.
```

---

### Section 2: Quick Reference

Must include **all** of these subsections:

```markdown
## Quick Reference

**[Number] Steps (or Key Formula):**
[Numbered list of main steps, OR the key formula if method is simple]

**Progress Template:** See [Progress Tracking Template](#progress-tracking-template) section below to copy into PROGRESS.md

**Actuarial Selections:** See [Actuarial Selections Required](#actuarial-selections-required) section for decision points

**Required Inputs:**
- [List all required data inputs]
- [Include formats/sources]

**Key Outputs:**
- [List primary outputs]
- [What gets used in selections]

**Python Packages:** `pandas`, `numpy`, [other specific packages]

**Advantages:**
- [Pro 1]
- [Pro 2]

**Disadvantages:**
- [Con 1]  
- [Con 2]

**When to Use [Method]:**
- [Scenario 1]
- [Scenario 2]
- [Scenario 3]

**Comparison to [Related Method]:**
[Brief 1-2 sentence comparison to most similar method]
```

---

### Section 3: Detailed Methodology

Break the method into clear steps:

```markdown
---

## Detailed Methodology

### Step 1: Data Requirements

#### Raw Data Formats

[Describe what formats the data might arrive in]

**Format 1: [Name]**
```
[Example table or structure]
```

**Format 2: [Name]**
```
[Example table or structure]
```

#### Data Processing Requirements

**Transform to standard format:**
- [Transformation 1]
- [Transformation 2]

**Validation checks:**
- [Check 1]
- [Check 2]

**Standard processed format:**
[Describe the final format needed for calculations]

---

### Step 2: [Calculation/Analysis Step]

[Detailed explanation of this step]

**Formula:**
```
[Mathematical formula if applicable]
```

**Explanation of terms:**
- `Term1` = [definition]
- `Term2` = [definition]

[Continue for each major step...]
```

---

### Section 4: Python Implementation

**Critical:** Provide a complete working implementation that users can run.

```markdown
---

### Step [N]: Python Implementation

#### Useful Packages

```python
import pandas as pd
import numpy as np
# [Other imports with comments on what they're for]
```

**Package `[special-package]`:** [Brief description and install command]

#### Code Sample: [Method Name] Implementation

```python
import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple

class [MethodName]Method:
    """
    Implements the [Method Name] method for loss reserving.
    
    [2-3 sentences describing what the class does]
    """
    
    def __init__(self, [parameters]):
        """
        Initialize [Method Name] method.
        
        Parameters:
        -----------
        [param1] : type
            [description]
        [param2] : type
            [description]
        """
        # Implementation
        pass
    
    def [calculate_something](self) -> pd.DataFrame:
        """
        [Method description]
        
        Returns:
        --------
        pd.DataFrame : [what it returns]
        """
        # Implementation
        pass
    
    def run_analysis(self) -> pd.DataFrame:
        """
        Run complete [Method Name] analysis.
        
        Returns:
        --------
        pd.DataFrame : Complete results with all intermediate calculations
        """
        # Implementation
        pass
    
    def export_results(self, filepath: str):
        """
        Export results to Excel with multiple sheets.
        """
        # Implementation
        pass


# Example Usage
if __name__ == "__main__":
    # Sample data
    [...]
    
    # Initialize and run
    method = [MethodName]Method([...])
    results = method.run_analysis()
    
    # Display results
    print(results)
    
    # Export
    method.export_results('[method_name]_results.xlsx')
```

[Include a complete, runnable example that demonstrates the method]
```

**Requirements for code:**
- Must be complete and runnable (not pseudocode)
- Include docstrings for all methods
- Include an example usage in `if __name__ == "__main__":`
- Include export_results() method for Excel output
- Handle edge cases gracefully
- Follow Python best practices

---

### Section 5: Outputs and Selection Process

```markdown
---

### Step [N]: Outputs and Selection Process

#### Primary Outputs

**1. [Output Name]:**
[Description and example table]

**2. [Output Name]:**
[Description and example table]

#### Creating Selection Candidates

[Explain what variations create different candidates]

**Method Variations to Consider:**
1. **Variation 1:** [Description]
2. **Variation 2:** [Description]

**Selection Process:**

```python
def create_selection_candidates([params]) -> pd.DataFrame:
    """
    Generate multiple [method] estimates using different assumptions.
    
    Returns DataFrame with ultimate losses by accident year for each scenario.
    """
    candidates = pd.DataFrame(index=[...])
    
    # Scenario 1: [Description]
    [code]
    candidates['[method]_[scenario1]'] = results1
    
    # Scenario 2: [Description]
    [code]
    candidates['[method]_[scenario2]'] = results2
    
    [... more scenarios ...]
    
    return candidates

# Usage
selection_candidates = create_selection_candidates([...])
selection_candidates.to_excel('selections/[method]_candidates.xlsx')
```

#### Documentation for Selections

Create a selection memo documenting:

1. **[Key decision 1]:** [What needs to be documented]
2. **[Key decision 2]:** [What needs to be documented]

**Template for selection documentation:**
```markdown
## [Method Name] Method - Selections

### Method Overview
[Brief overview]

### [Key Selection 1]
- Selected: [value]
- Rationale: [explanation]
- Alternatives considered: [list with reasons not selected]

[Continue for each key selection...]

### Resulting Ultimate Losses
Total ultimate losses: $[amount]
Total IBNR: $[amount]

### Reasonability
[Checks performed and results]
```
```

---

### Section 6: Diagnostic Displays

Provide code for useful visualizations:

```markdown
---

## Diagnostic Displays

### Key visualizations to create:

```python
import matplotlib.pyplot as plt
import seaborn as sns

def create_diagnostic_charts(method: [MethodName]Method):
    """Generate diagnostic charts for [Method Name] analysis."""
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # 1. [Chart 1 name]
    ax1 = axes[0, 0]
    [plotting code]
    ax1.set_title('[Chart Title]')
    
    # 2. [Chart 2 name]
    ax2 = axes[0, 1]
    [plotting code]
    ax2.set_title('[Chart Title]')
    
    # 3. [Chart 3 name]
    ax3 = axes[1, 0]
    [plotting code]
    ax3.set_title('[Chart Title]')
    
    # 4. [Chart 4 name]
    ax4 = axes[1, 1]
    [plotting code]
    ax4.set_title('[Chart Title]')
    
    plt.tight_layout()
    plt.savefig('analysis/[method]_diagnostics.png', dpi=300, bbox_inches='tight')
    plt.close()

# Generate diagnostics
create_diagnostic_charts(method)
```

**Recommended diagnostic charts:**
- [Method-specific chart 1]
- [Method-specific chart 2]
- Comparison to other methods (if applicable)
- Sensitivity analysis visualization
```

---

### Section 7: Progress Tracking Template

**Critical:** This section gets copied into the main PROGRESS.md as the actuary works through the method.

```markdown
---

## Progress Tracking Template

Copy this section into your main PROGRESS.md under "Step 3: Selections Process" when working the [Method Name] method.

\`\`\`markdown
#### Selection Level: [Method Name]
**Status:** [Not Started / In Progress / Completed]
**Method:** [Method Name]
**Started:** [Date]

##### 3A: Data Preparation
- [ ] [Specific data task 1]
- [ ] [Specific data task 2]
- [ ] [Specific data task 3]

**Data Sources:**
- [Data item 1]: [Source]
- [Data item 2]: [Source]

**Data Quality Issues:**
[Space to document issues]

**Files Created:**
- `/data/processed/[filename]`

##### 3B: [Calculation Step Name]
- [ ] [Specific calculation task 1]
- [ ] [Specific calculation task 2]
- [ ] [Specific calculation task 3]

**[Table or Checklist Name]:**

| [Column 1] | [Column 2] | [Column 3] | [Column 4] |
|-----------|-----------|-----------|-----------|
| [Item 1]  |           |           |           |
| [Item 2]  |           |           |           |

**Files Created:**
- `/analysis/[filename]`

##### 3C: [Selection/Recommendation Step]
- [ ] [Task 1]
- [ ] [Task 2]

**Recommendations:**

| [What's Being Selected] | [Option 1] | [Option 2] | Recommended | Reasoning |
|------------------------|-----------|-----------|-------------|-----------|
| [Item 1]                |           |           |             |           |

**Files Created:**
- `/analysis/[filename]`

##### 3D: Discussion & Refinement
**Discussion Date:** [Date]  
**Participants:** [Names]

**Questions from Actuary:**
[Space for questions]

**Feedback Received:**
[Space for feedback]

**Refinements Made:**
[Space to document changes]

##### 3E: Final Selections
- [ ] Selections finalized
- [ ] Documented in selections file

**Final Selections:**

| [Parameter] | Selected Value | Rationale |
|------------|---------------|-----------|
| [Param 1]  |               |           |

**Files Created:**
- `/selections/[method]_selections.md`

##### 3F: [Method] Ultimate Calculation
- [ ] Calculated ultimate losses by accident year
- [ ] Calculated IBNR
- [ ] Generated summary tables
- [ ] Created comparison to [other method]

**[Method Name] Ultimate Losses:**

| Accident Year | Latest Loss | [Method] Ultimate | IBNR | [Comparison Method] | Difference |
|--------------|------------|------------------|------|-------------------|------------|
| [Year]       |            |                  |      |                   |            |
| **Total**    |            |                  |      |                   |            |

**Summary Statistics:**
- Total Ultimate: $[amount]
- Total IBNR: $[amount]
- IBNR %: [%]

**Files Created:**
- `/analysis/[method]_results.xlsx`

##### 3G: Reasonability Testing
- [ ] [Reasonability check 1]
- [ ] [Reasonability check 2]
- [ ] [Reasonability check 3]

**[Method-Specific Reasonability Checks]:**
[Tables or descriptions of checks]

**Files Created:**
- `/analysis/[method]_reasonability.xlsx`

---
\`\`\`

---
```

**Guidelines for progress template:**
- Use sections 3A-3G (or more if needed)
- Include specific tasks with checkboxes
- Provide tables for tracking selections
- Include "Files Created" at end of each section
- Make it detailed enough to follow step-by-step
- Include placeholders for dates, names, amounts

---

### Section 8: Actuarial Selections Required

**Critical:** Document every decision point where actuarial judgment is needed.

```markdown
---

## Actuarial Selections Required

### Overview of Selection Points

The [Method Name] method requires the actuary to make selections at [number] critical points. [Brief overview sentence.]

### Selection 1: [First Major Decision]

**Decision:** [Clear statement of what needs to be decided]

**Options:**
1. **Option 1:** [Description]
2. **Option 2:** [Description]
3. **Option 3:** [Description]

**Considerations:**

**Option 1:**
- **Use when:** [Circumstances where this is appropriate]
- **Pros:**
  - [Pro 1]
  - [Pro 2]
- **Cons:**
  - [Con 1]
  - [Con 2]
- **Questions to ask:**
  1. [Question 1]
  2. [Question 2]

[Repeat for other options]

**Key Questions:**
1. [Overall question 1]
2. [Overall question 2]
3. [Overall question 3]

**Red Flags:**
- [Warning sign 1]
- [Warning sign 2]

**Documentation Required:**
- [Doc item 1]
- [Doc item 2]
- [Doc item 3]

---

### Selection 2: [Second Major Decision]

[Repeat same structure as Selection 1]

---

[Continue for all major selections]

---

### Best Practices for Documentation

**For each selection, document:**
1. **What was selected:** [Specifics]
2. **Why it was selected:** [Rationale]
3. **What alternatives were considered:** [Options]
4. **Impact of alternatives:** [Sensitivity]
5. **Comparison to prior:** [Changes and reasons]

**Create supporting exhibits:**
- [Exhibit 1]
- [Exhibit 2]

**Maintain audit trail:**
- [Audit item 1]
- [Audit item 2]

---
```

**Guidelines for selections section:**
- Cover EVERY decision point requiring judgment
- For each selection, provide:
  - Clear decision statement
  - Multiple options with pros/cons
  - When to use each option
  - Questions to guide thinking
  - Red flags to watch for
  - Required documentation
- Use real actuarial language and considerations
- Think about what a regulator would want to see documented

---

### Section 9: Integration with Overall Study

```markdown
---

## Integration with Overall Reserving Study

The [Method Name] method typically produces [description of output] that serves as [role in overall study]:

1. **Run [Method Name]** with selected assumptions → Produces [Method] ultimate estimate
2. **Run [other methods]** → Additional estimates
3. **Compare methods** → Understand differences
4. **Weight methods** → [Typical weighting guidance]
5. **Document selections** → Rationale for method weights
6. **Create final estimate** → Blended ultimate

**Typical weighting:**
[Guidance on how much weight this method typically receives]

**When this method should get more weight:**
- [Scenario 1]
- [Scenario 2]

**When this method should get less weight:**
- [Scenario 1]
- [Scenario 2]

**Example workflow:**

```python
def create_weighted_ultimate([parameters]) -> pd.DataFrame:
    """
    Create weighted ultimate estimate combining multiple methods.
    """
    [Example code showing how this method integrates with others]
    
    return blended_results
```
```

---

### Section 10: Limitations and Considerations

```markdown
---

## Limitations and Considerations

### When [Method Name] May Not Be Appropriate

1. **[Limitation 1]:** [Detailed explanation]
2. **[Limitation 2]:** [Detailed explanation]
3. **[Limitation 3]:** [Detailed explanation]

### Reasonability Checks

Before finalizing selections:
- [Check 1]
- [Check 2]
- [Check 3]

### Common Issues and Solutions

**Issue: [Common problem]**
- Cause: [Explanation]
- Solution: [How to address]
- Alternative: [Alternative approach]

[Repeat for other common issues]

---
```

---

### Section 11: References

```markdown
---

## References

- [Author]. "[Title]." [Publication], [Year].
- [Online resource with URL]
- [Python package documentation with URL]
- [Industry standard or study]

---
```

Always include:
- Academic/industry papers if applicable
- CAS syllabus readings
- Wikipedia if available and accurate
- Python package documentation
- Industry association resources

---

## Checklist for Completing a Method Skill

Before considering a method skill complete, verify:

### Structure
- [ ] YAML frontmatter with descriptive name and comprehensive description
- [ ] Title and introduction (2-4 paragraphs)
- [ ] Quick Reference section with all required subsections
- [ ] Detailed Methodology broken into clear steps
- [ ] Data Requirements section (raw formats and processing)
- [ ] Python Implementation section with complete working code
- [ ] Outputs and Selection Process section with candidate generation
- [ ] Diagnostic Displays section with visualization code
- [ ] Progress Tracking Template (ready to copy into PROGRESS.md)
- [ ] Actuarial Selections Required (comprehensive decision guidance)
- [ ] Integration with Overall Study section
- [ ] Limitations and Considerations section
- [ ] References section

### Content Quality
- [ ] Clear explanation of when to use this method vs others
- [ ] All required data inputs identified with formats
- [ ] Python code is complete and runnable (not pseudocode)
- [ ] Code includes example usage with sample data
- [ ] Selection candidates generation is explained and coded
- [ ] Every actuarial decision point is documented with guidance
- [ ] Progress template has 5-7 subsections (3A through 3G or more)
- [ ] Each selection includes: options, pros/cons, questions, red flags, documentation
- [ ] Comparison to at least one related method
- [ ] At least 3 diagnostic visualizations recommended

### Actuarial Completeness
- [ ] Addresses common concerns actuaries would have
- [ ] Includes sensitivity analysis guidance
- [ ] Comparison to prior analysis considerations
- [ ] Documentation requirements for audit trail
- [ ] Regulatory/compliance considerations if applicable
- [ ] Industry benchmark comparisons if applicable

### Usability
- [ ] Can be used by someone unfamiliar with the method
- [ ] Code can be copied and run with minimal modifications
- [ ] Progress template can be copied directly into PROGRESS.md
- [ ] Clear navigation with section links in Quick Reference
- [ ] Examples use realistic actuarial data and terminology

---

## Examples to Reference

When creating a new method skill, reference these existing skills as templates:

1. **chain-ladder-method** - Good example of:
   - Classic development method structure
   - LDF selection guidance
   - Age-to-age calculations
   
2. **bornhuetter-ferguson-method** - Good example of:
   - Methods requiring external inputs (ELR)
   - Blending actual and expected
   - Sensitivity analysis emphasis
   - Method comparison sections

Study their structure and adapt for your new method while maintaining consistency.

---

## Tips for Writing Effective Method Skills

### Use Actuarial Language
- Write for an actuarial audience
- Use standard terminology (IBNR, development, ultimate, etc.)
- Reference common actuarial concepts
- Assume reader has actuarial background but may not know this specific method

### Be Specific
- Don't say "calculate appropriate factors" - say "calculate age-to-age factors using 5-year volume-weighted average"
- Don't say "consider alternatives" - list specific alternatives to consider
- Provide actual numeric examples when possible

### Think About the User's Workflow
- What will they do first? Second? Third?
- What questions will they have at each step?
- What could go wrong and how do they fix it?
- What do they need to document for regulators/auditors?

### Include Realistic Examples
- Use realistic loss amounts (millions, not hundreds)
- Use realistic accident years (current year minus appropriate lag)
- Use realistic data patterns (not perfect smooth data)
- Show how to handle edge cases

### Document Decision Points Thoroughly
- Every selection needs: what, why, alternatives, pros/cons, questions, documentation
- Think about explaining your selections to a skeptical auditor
- What would you want documented if reviewing this analysis?

### Make Code Production-Ready
- Not just "demo code" - actual usable implementation
- Error handling for edge cases
- Clear variable names
- Docstrings for all functions/methods
- Export functionality to Excel
- Logging or progress indicators for long-running calculations

---

## Testing Your Method Skill

Before finalizing, test the skill:

1. **Read-through test:**
   - Can you follow it step-by-step without getting lost?
   - Are there any ambiguous instructions?
   - Any jargon that needs explanation?

2. **Code test:**
   - Copy the code and run it
   - Does it work without modifications?
   - Are all imports available?
   - Does output match what's described?

3. **Completeness test:**
   - Can an actuary use this to complete the method without other resources?
   - Are all selection points covered?
   - Is documentation guidance sufficient?

4. **Progress template test:**
   - Copy the progress template to a test file
   - Walk through filling it out
   - Is anything missing?
   - Are sections in logical order?

5. **Comparison test:**
   - Compare to chain-ladder-method and bornhuetter-ferguson-method
   - Is structure consistent?
   - Is level of detail similar?
   - Are all standard sections included?

---

## Creating Method Skills for Different Complexity Levels

### Simple Methods (e.g., Expected Loss Ratio Method)

**Characteristics:**
- Few steps (2-4)
- Minimal calculations
- Few selection points

**Adjustments:**
- Shorter Detailed Methodology section
- Simpler code implementation (maybe just functions, not a class)
- Fewer subsections in Progress Template (3A-3D instead of 3A-3G)
- Still need comprehensive Actuarial Selections section
- Focus more on when to use vs other methods

### Complex Methods (e.g., Frequency/Severity with GLM fitting)

**Characteristics:**
- Many steps (10+)
- Statistical modeling
- Many selection points

**Adjustments:**
- May need multiple subsections in Detailed Methodology
- More extensive code with additional classes/functions
- More subsections in Progress Template (3A-3J+)
- Extensive Actuarial Selections section with additional decision points
- May need separate sensitivity analysis section
- Consider creating additional supporting files in skill directory

### Adjustment Techniques (e.g., Large Loss Adjustments)

**Characteristics:**
- Applied to other methods
- Modifies data before running standard methods
- Procedural rather than a standalone method

**Adjustments:**
- Focus on when/how to apply the adjustment
- Integration section explains which methods to apply adjustment to
- Progress template may be shorter (adjustment is subset of another method)
- Code might focus on data transformation functions
- Selections focus on threshold/adjustment criteria

---

## Maintaining and Updating Method Skills

As methods are used in practice:

**Update when:**
- Bugs found in code
- Better approaches discovered
- Additional selection scenarios identified
- User feedback suggests unclear sections
- New Python packages become available
- Regulatory requirements change

**Version control:**
- Note significant changes in commit messages
- Consider adding version history section for major updates
- Document why changes were made

**Keep consistent:**
- When updating one method skill, check if others need similar updates
- Maintain consistent structure across all method skills
- Update cross-references between skills

---

## References

- See existing skills: chain-ladder-method, bornhuetter-ferguson-method
- improve-agent skill for general skill creation guidance
- Friedland, Jacqueline. "Estimating Unpaid Claims Using Basic Techniques." CAS, 2010.
- CAS Exam materials for method descriptions
