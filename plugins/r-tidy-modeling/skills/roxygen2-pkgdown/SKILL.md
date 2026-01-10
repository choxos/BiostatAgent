# roxygen2 and pkgdown

## Overview

Complete reference for roxygen2 documentation syntax and pkgdown site configuration. Covers all roxygen2 tags, cross-referencing, and advanced pkgdown customization.

## roxygen2 Fundamentals

### Basic Tags

```r
#' @title Short title (optional, first paragraph used if omitted)
#' @description Longer description (optional, second paragraph used if omitted)
#' @details Additional details section
#' @param name Description of parameter
#' @return Description of return value
#' @examples Runnable R code
#' @export Add function to NAMESPACE exports
#' @keywords keyword1 keyword2
#' @author Author Name
```

### Parameter Documentation

```r
#' @param x A numeric vector of values.
#' @param y Character string specifying the method. One of:
#'   - `"method1"`: Description of method 1
#'   - `"method2"`: Description of method 2
#' @param data A data frame containing:
#'   \describe{
#'     \item{col1}{Description of column 1}
#'     \item{col2}{Description of column 2}
#'   }
#' @param ... Additional arguments passed to [other_function()].
#' @param .data Internal use only. Data frame to process.
```

### Return Value Documentation

```r
#' @return A numeric vector of the same length as `x`.

#' @return A list with components:
#'   \describe{
#'     \item{fitted}{Fitted values from the model.}
#'     \item{residuals}{Model residuals.}
#'     \item{coefficients}{Named vector of coefficients.}
#'   }

#' @return A tibble with columns:
#'   * `term`: Character. The term name.
#'   * `estimate`: Numeric. Point estimate.
#'   * `std.error`: Numeric. Standard error.

#' @return Invisibly returns the input `x`.
```

### Examples

```r
#' @examples
#' # Basic usage
#' result <- my_function(1:10)
#'
#' # With options
#' result <- my_function(1:10, method = "fast")
#'
#' \dontrun{
#' # Code that shouldn't be run (e.g., requires authentication)
#' connect_to_database()
#' }
#'
#' \donttest{
#' # Code that runs but is skipped in R CMD check (slow examples)
#' slow_computation(big_data)
#' }
#'
#' @examplesIf interactive()
#' # Only run interactively
#' open_plot_window()
```

## Cross-Referencing

### Linking to Functions

```r
#' See [other_function()] for details.
#' This wraps [stats::lm()].
#' Similar to [dplyr::mutate()].
#' See [pkg::function()] from external package.

#' @seealso [related_function()], [another_function()]
#' @seealso
#' * [function1()] for X
#' * [function2()] for Y
#' * [pkg::function3()] for Z
```

### Linking to Topics

```r
#' See [topic-name] for the vignette.
#' See \code{vignette("topic")} for details.
#' See the \href{https://example.com}{website}.
```

## Advanced roxygen2 Tags

### Inheritance

```r
#' @inheritParams other_function
#' @inheritDotParams other_function arg1 arg2
#' @inherit other_function return
#' @inherit other_function details
#' @inheritSection other_function Section Name
```

### Function Families

```r
#' @family data import functions
#' @concept data manipulation
```

### Multiple Functions Per File

```r
#' Function A
#' @rdname shared-docs
#' @export
function_a <- function(x) {}

#' Function B
#' @rdname shared-docs
#' @export
function_b <- function(x) {}

#' @rdname shared-docs
#' @usage NULL
#' @aliases function_a function_b
```

### Conditional Exports

```r
#' @rawNamespace if (getRversion() >= "4.0") export(new_function)
```

### S3 Methods

```r
#' @export
#' @method print myclass
print.myclass <- function(x, ...) {}

#' @exportS3Method
print.myclass <- function(x, ...) {}
```

### S4 Classes and Methods

```r
#' MyClass
#'
#' @slot x Numeric slot
#' @slot y Character slot
#'
#' @exportClass MyClass
setClass("MyClass", slots = c(x = "numeric", y = "character"))

#' @exportMethod mymethod
setMethod("mymethod", "MyClass", function(object) {})
```

### Imports

```r
#' @import dplyr
#' @importFrom ggplot2 ggplot aes
#' @importMethodsFrom pkg method
#' @importClassesFrom pkg Class
```

## Markdown in roxygen2

### Enable Markdown

```r
# In DESCRIPTION:
Roxygen: list(markdown = TRUE)
```

### Markdown Syntax

```r
#' **Bold** and *italic* text
#'
#' - Bullet point 1
#' - Bullet point 2
#'
#' 1. Numbered item 1
#' 2. Numbered item 2
#'
#' `inline code` and [links](https://example.com)
#'
#' ```r
#' # Code block
#' x <- 1:10
#' ```
#'
#' | Column 1 | Column 2 |
#' |----------|----------|
#' | A        | B        |
```

## pkgdown Configuration

### Basic _pkgdown.yml

```yaml
url: https://user.github.io/pkg/

template:
  bootstrap: 5
  bootswatch: flatly

navbar:
  structure:
    left: [intro, reference, articles, tutorials, news]
    right: [search, github]
  components:
    github:
      icon: fab fa-github
      href: https://github.com/user/pkg

reference:
  - title: Main Functions
    desc: Core functionality
    contents:
      - main_function
      - helper_function
  - title: Utilities
    contents:
      - starts_with("util_")
  - title: internal
    contents:
      - internal_function

articles:
  - title: Getting Started
    navbar: ~
    contents:
      - pkgname
  - title: Advanced Topics
    contents:
      - advanced-usage
      - customization

news:
  releases:
    - text: "Version 1.0.0"
      href: https://github.com/user/pkg/releases/tag/v1.0.0
```

### Reference Organization

```yaml
reference:
  - title: Data Import
    desc: Functions for importing data
    contents:
      - read_data
      - read_csv_data
      - matches("^read_")

  - title: Data Transformation
    contents:
      - transform_data
      - starts_with("transform_")

  - title: Analysis
    contents:
      - has_concept("analysis")

  - title: Visualization
    contents:
      - has_keyword("plot")

  - subtitle: Core Plots
    contents:
      - plot_main

  - subtitle: Diagnostic Plots
    contents:
      - plot_diagnostics
```

### Custom Styling

```yaml
template:
  bootstrap: 5
  bootswatch: flatly
  bslib:
    primary: "#0054AD"
    border-radius: 0.5rem
    btn-border-radius: 0.25rem
  includes:
    in_header: |
      <!-- Google Analytics -->
      <script async src="https://www.googletagmanager.com/gtag/js"></script>
```

### Home Page Customization

```yaml
home:
  title: Package Name
  description: One-line description

  links:
    - text: Learn more
      href: https://example.com

  sidebar:
    structure: [links, license, community, citation, authors, dev]
```

### Articles Configuration

```yaml
articles:
  - title: Tutorials
    navbar: Tutorials
    contents:
      - articles/getting-started
      - articles/basic-usage

  - title: Advanced
    navbar: Advanced
    contents:
      - articles/advanced-topics

  - title: Internal
    contents:
      - articles/internal-docs
    # Not in navbar
```

## Building pkgdown Site

### Build Commands

```r
# Build entire site
pkgdown::build_site()

# Build specific parts
pkgdown::build_home()
pkgdown::build_reference()
pkgdown::build_articles()
pkgdown::build_news()

# Preview locally
pkgdown::preview_site()

# Check site
pkgdown::check_pkgdown()
```

### GitHub Actions Deployment

```yaml
# .github/workflows/pkgdown.yaml
on:
  push:
    branches: [main, master]
  release:
    types: [published]
  workflow_dispatch:

name: pkgdown

jobs:
  pkgdown:
    runs-on: ubuntu-latest
    env:
      GITHUB_PAT: ${{ secrets.GITHUB_TOKEN }}
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
      - uses: r-lib/actions/setup-pandoc@v2
      - uses: r-lib/actions/setup-r@v2
        with:
          use-public-rspm: true
      - uses: r-lib/actions/setup-r-dependencies@v2
        with:
          extra-packages: any::pkgdown, local::.
          needs: website
      - name: Build site
        run: pkgdown::build_site_github_pages(new_process = FALSE, install = FALSE)
        shell: Rscript {0}
      - name: Deploy to GitHub pages
        uses: JamesIves/github-pages-deploy-action@v4
        with:
          clean: false
          branch: gh-pages
          folder: docs
```

## Workflow

```r
# Development cycle
devtools::document()        # Generate man/ files
devtools::check()           # Check package
pkgdown::build_site()       # Build website

# Quick preview
pkgdown::build_reference_index()
pkgdown::build_article("vignette-name")
```

## Common Patterns

### Reexporting Functions

```r
#' @importFrom magrittr %>%
#' @export
magrittr::`%>%`

#' @importFrom rlang .data
#' @export
rlang::.data
```

### Deprecated Functions

```r
#' @description
#' `r lifecycle::badge("deprecated")`
#'
#' This function is deprecated. Use [new_function()] instead.
#'
#' @keywords internal
#' @export
old_function <- function(...) {
  lifecycle::deprecate_warn("1.0.0", "old_function()", "new_function()")
  new_function(...)
}
```

### Internal Functions

```r
#' Internal function
#'
#' @keywords internal
#' @noRd
internal_helper <- function(x) {}
```
