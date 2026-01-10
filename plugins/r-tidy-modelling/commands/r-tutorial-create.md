# R Tutorial Creation

Create step-by-step tutorials and educational content from R code. This command uses the **r-tutorial-engineer** agent to transform code into progressive learning experiences.

## Workflow Steps

### 1. Code Analysis
- Analyze target code structure
- Identify key concepts to teach
- Determine prerequisite knowledge
- Map learning progression

### 2. Learning Design
- Define learning objectives
- Structure content progressively
- Plan exercises and checkpoints
- Design assessments

### 3. Content Creation
- Write explanatory narrative
- Create code walkthroughs
- Develop practice exercises
- Add tips and common pitfalls

### 4. Interactive Features (Optional)
- Convert to learnr format
- Add quiz questions
- Create hints and solutions
- Set up exercise checking

### 5. Output Generation
- Generate tutorial document(s)
- Create exercise files
- Build learnr app (if requested)
- Export in requested format

## Usage

```
/r-tutorial-create [source] [topic] [format] [level]
```

### Parameters
- `source`: Path to R code/script to document, or topic keyword
- `topic`: Tutorial topic/title
- `format`: One of `rmd`, `qmd`, `learnr`, `html` (default: qmd)
- `level`: One of `beginner`, `intermediate`, `advanced` (default: intermediate)

### Tutorial Types

**Code Walkthrough**
- Step-by-step explanation of existing code
- Line-by-line annotations
- Concept explanations
- Output interpretation

**Concept Tutorial**
- Topic-focused learning
- Progressive examples
- Practice exercises
- Knowledge checks

**How-To Guide**
- Task-oriented
- Minimal explanation
- Copy-paste ready
- Quick reference

**Cookbook**
- Recipe-style solutions
- Common patterns
- Variations and alternatives
- Best practices

### Formats

**rmd**: R Markdown document
- Static tutorial document
- Can be rendered to HTML/PDF
- Includes executable code

**qmd**: Quarto document
- Modern R Markdown alternative
- Enhanced features
- Multi-format output

**learnr**: Interactive tutorial
- Shiny-based interactivity
- In-browser code execution
- Progress tracking
- Quiz questions

**html**: Static HTML
- Standalone web page
- Shareable link
- No R required to view

## Output Location

```
output/
└── tutorials/
    ├── tutorial_name/
    │   ├── tutorial.qmd           # Main tutorial
    │   ├── exercises/
    │   │   ├── exercise_01.R      # Practice files
    │   │   └── exercise_02.R
    │   ├── solutions/
    │   │   ├── solution_01.R      # Answer keys
    │   │   └── solution_02.R
    │   └── data/                   # Example data
    └── tutorial_name_learnr/       # If learnr format
        └── tutorial.Rmd
```

## Example

```
/r-tutorial-create R/analysis.R "Survival Analysis Basics" learnr beginner
```

This creates a beginner-level learnr tutorial teaching survival analysis based on the code in R/analysis.R.

## Tutorial Structure

### Standard Tutorial

```markdown
# Tutorial Title

## Learning Objectives

By the end of this tutorial, you will be able to:
- Objective 1
- Objective 2
- Objective 3

## Prerequisites

Before starting, you should:
- Have R installed
- Be familiar with basic R syntax
- Have packages X, Y, Z installed

## Introduction

Overview and motivation...

## Section 1: [Topic]

### Concept Explanation
[Theory and background]

### Example Code
[Annotated code with output]

### Try It Yourself
[Exercise prompt]

<details>
<summary>Solution</summary>
[Solution code]
</details>

## Section 2: [Topic]
...

## Summary

Key takeaways:
- Point 1
- Point 2
- Point 3

## Next Steps

To continue learning:
- Tutorial link 1
- Tutorial link 2
```

### learnr Tutorial

```r
---
title: "Tutorial Title"
output: learnr::tutorial
runtime: shiny_prerendered
---

```{r setup, include=FALSE}
library(learnr)
library(tidyverse)
knitr::opts_chunk$set(echo = FALSE)
```

## Introduction

Welcome text...

## Topic 1

### Explanation

Concept explanation...

### Exercise

Write code to...

```{r exercise1, exercise=TRUE}
# Your code here

```

```{r exercise1-hint}
# Try using the function...
```

```{r exercise1-solution}
# Complete solution
```

### Quiz

```{r quiz1}
quiz(
  question("Question text?",
    answer("Wrong answer"),
    answer("Correct answer", correct = TRUE),
    answer("Another wrong answer")
  )
)
```
```

## Content Features

### Code Annotations
- Line-by-line explanations
- Output interpretation
- Why certain approaches are used
- Common variations

### Exercises
- Fill-in-the-blank code
- Debug exercises
- Extend existing code
- Write from scratch

### Progressive Difficulty
- Start with simple examples
- Add complexity gradually
- Challenge problems at end
- Extension ideas for advanced learners

### Visual Aids
- Diagrams for concepts
- Flowcharts for processes
- Output screenshots
- Comparison tables

## Notes

- Original code is never modified
- All tutorials go to output/tutorials/
- Includes standalone exercise files
- Solutions provided separately
- Example data included when needed
