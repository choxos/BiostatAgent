# R Documentation Generation

Generate comprehensive documentation from R codebases. This command uses the **r-docs-architect** agent to create roxygen2 documentation, README files, pkgdown sites, and architecture documentation.

## Workflow Steps

### 1. Codebase Analysis
- Scan R files for functions and classes
- Identify exported vs internal functions
- Map function dependencies
- Detect existing documentation

### 2. Documentation Generation
Generate comprehensive documentation:
- roxygen2 function documentation
- Package-level documentation
- Dataset documentation
- Vignette outlines

### 3. README Creation
- Project overview
- Installation instructions
- Quick start examples
- Badge integration

### 4. pkgdown Configuration
- Site structure (_pkgdown.yml)
- Reference organization
- Article arrangement
- Custom styling

### 5. Architecture Documentation
- System diagrams (Mermaid)
- Component relationships
- Data flow visualization
- API reference

## Usage

```
/r-doc-generate [path] [doc_type] [options]
```

### Parameters
- `path`: Path to R package or project (default: current directory)
- `doc_type`: One of `full`, `roxygen`, `readme`, `pkgdown`, `architecture` (default: full)
- `options`: Comma-separated options (see below)

### Documentation Types

**full**: Complete documentation suite
- All roxygen2 documentation
- README with badges
- pkgdown configuration
- Architecture diagrams
- Vignette templates

**roxygen**: Function documentation only
- roxygen2 comments for all functions
- Parameter documentation
- Return value documentation
- Examples

**readme**: README generation
- Project description
- Installation guide
- Usage examples
- Contributing guidelines

**pkgdown**: Website configuration
- _pkgdown.yml configuration
- Reference organization
- Article structure
- Theme settings

**architecture**: Architecture documentation
- System overview diagrams
- Component documentation
- Data flow diagrams
- API reference

### Options

- `overwrite`: Overwrite existing docs (default: no)
- `badges`: Include badges in README (default: yes)
- `examples`: Generate examples (default: yes)
- `vignettes`: Create vignette templates (default: yes)

## Output Location

```
output/
└── documentation/
    ├── man/                    # roxygen2 generated docs
    │   ├── function1.Rd
    │   └── function2.Rd
    ├── README.md               # Project README
    ├── _pkgdown.yml            # pkgdown configuration
    ├── vignettes/
    │   ├── getting-started.Rmd
    │   └── advanced-usage.Rmd
    └── architecture/
        ├── overview.md         # System overview
        └── diagrams/           # Mermaid/graphviz files
```

## Example

```
/r-doc-generate my_package full badges,vignettes
```

This generates complete documentation for my_package with badges and vignettes.

## Documentation Standards

### roxygen2 Template

```r
#' Function Title
#'
#' Detailed description of what the function does.
#'
#' @param x Description of parameter x.
#' @param y Description of parameter y.
#'
#' @return Description of return value.
#'
#' @examples
#' # Basic usage
#' result <- function_name(x = 1, y = 2)
#'
#' @export
#' @family related functions
#' @seealso [related_function()]
```

### README Template

```markdown
# Package Name

<!-- badges: start -->
[![R-CMD-check](badge-url)](badge-link)
[![CRAN status](badge-url)](badge-link)
<!-- badges: end -->

## Overview

Brief description of the package.

## Installation

```r
install.packages("pkg")
```

## Usage

```r
library(pkg)
# Basic example
```

## Getting Help

- Documentation: https://user.github.io/pkg/
- Issues: https://github.com/user/pkg/issues
```

## Generated Content

### Function Documentation
- Auto-detects parameter types
- Generates @return based on function body analysis
- Creates runnable @examples
- Adds appropriate @export tags
- Links related functions with @family

### README Components
- Dynamic badges based on CI configuration
- Installation for CRAN and GitHub
- Usage examples from package functions
- Documentation links

### pkgdown Configuration
- Organizes functions by topic
- Groups related articles
- Configures search
- Sets up navigation

### Architecture Diagrams
- Function dependency graphs
- Data flow diagrams
- Package structure visualization
- API endpoint mapping

## Integration

### With devtools
```r
# After generating docs
devtools::document()
devtools::check()
pkgdown::build_site()
```

### With GitHub Actions
Generated workflows include:
- Documentation building
- pkgdown deployment
- README rendering

## Notes

- Original code is never modified
- All documentation goes to output/documentation/
- Review generated docs before integrating
- Templates follow tidyverse style
