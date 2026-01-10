# R Code Review

Comprehensive code review for R scripts and packages. This command uses the **r-code-reviewer** agent (Opus) to perform thorough quality assessment.

## Review Scope

### Style Review
- Tidyverse style guide compliance
- Naming conventions (snake_case, meaningful names)
- Code formatting and indentation
- Pipe usage and readability

### Quality Review
- Function design (single responsibility, pure functions)
- Error handling patterns
- Documentation completeness
- DRY principle adherence

### Performance Review
- Vectorization opportunities
- Memory efficiency
- Computational bottlenecks
- Parallel processing opportunities

### Security Review
- Input validation
- Credential handling
- SQL injection prevention
- Safe file operations

### Testing Review
- Test coverage assessment
- Test quality and patterns
- Edge case coverage
- Mocking practices

### TMwR Review (Tidymodels Workflow Review)
- **Data Leakage Detection** (CRITICAL)
  - Recipe fitted on test data (DL-001)
  - Preprocessing before split (DL-002)
  - Target encoding without CV (DL-003)
  - Feature selection using test data (DL-004)
  - prep() before initial_split() (DL-005)
- **Resampling Violations** (MAJOR/CRITICAL)
  - Missing stratified sampling (RS-001)
  - Evaluating on training data (RS-002)
  - Tuning without nested CV (RS-003)
  - Missing random seeds (RS-004)
  - Validation set reuse (RS-005)
- **Workflow Issues** (MINOR/MAJOR)
  - Not using workflows (WF-001)
  - Inconsistent preprocessing train/test (WF-002)
  - Not finalizing workflow after tuning (WF-003)
- **Evaluation Issues** (MAJOR)
  - Only accuracy for imbalanced data (ME-001)
  - Wrong metrics for model mode (ME-002)
  - Missing calibration assessment (ME-003)
  - Missing confidence intervals (ME-004)
  - Different resamples for comparison (ME-005)
- **Reproducibility Issues** (MINOR/MAJOR)
  - Missing set.seed() (RP-001)
  - Missing tidymodels_prefer() (RP-002)
  - Hard-coded paths (RP-003)
  - Missing renv (RP-004)
  - Missing session info (RP-005)

## Usage

```
/r-code-review [path] [review_type]
```

### Parameters
- `path`: Path to R file, directory, or package (default: current directory)
- `review_type`: One of `full`, `style`, `performance`, `security`, `tests`, `tmwr` (default: full)

### Review Types

| Type | Description |
|------|-------------|
| `full` | All review types including TMwR |
| `style` | Tidyverse style guide compliance only |
| `performance` | Vectorization, memory, speed optimization |
| `security` | Input validation, credential handling |
| `tests` | Test coverage and quality |
| `tmwr` | Tidymodels workflow review (data leakage, resampling, evaluation) |

## Output Location

Review report will be written to:
```
output/
└── reports/
    └── code_review_[timestamp].md
```

## Review Report Structure

1. **Executive Summary**
   - Overall assessment
   - Key findings count by severity
   - Recommended priority actions

2. **Detailed Findings**
   - Each issue with:
     - Severity (Critical, Major, Minor, Suggestion)
     - Location (file:line)
     - Description
     - Recommendation
     - Code example (before/after)

3. **Metrics**
   - Lines of code
   - Function count and complexity
   - Test coverage (if available)
   - Documentation coverage

4. **Positive Observations**
   - Well-written code patterns
   - Good practices observed

## Examples

```
/r-code-review R/ full
```
Performs a comprehensive review of all R files in the R/ directory including TMwR compliance.

```
/r-code-review scripts/analysis.R tmwr
```
Performs a focused TMwR review for tidymodels workflow anti-patterns.

### TMwR Review Output

TMwR reviews include:
- **TMwR Compliance Score**: 0-100 based on anti-pattern severity
- **Issue Findings**: Each with ID, severity, location, description
- **Before/After Examples**: Remediation code for each issue
- **Checklist Summary**: Pass/fail for 10-point TMwR compliance checklist

## Integration with CI/CD

The review output can be integrated into GitHub Actions or other CI pipelines:

```yaml
- name: R Code Review
  run: |
    # Generate review report
    # Parse for critical issues
    # Fail if critical issues found
```

## Notes

- Review is read-only - no code modifications are made
- All suggestions are written to the output folder
- Large codebases may be reviewed in sections
