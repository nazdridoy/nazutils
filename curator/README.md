# Curator — Video Course Library Manager

**Curator** is a CLI tool designed to audit, lint, visualize, and triage local video course libraries.

It serves as the primary management tool for structuring IT, DevOps, programming, and media course collections, utilizing `courses.toml` as the single source of truth for library rules and AI triage prompts.

---

## Features

- **Lesson Auditor (`count`)**: Scans courses and counts sections and video files (`.mp4`, `.mkv`, `.avi`, `.webm`, etc.).
- **Convention Linter (`lint`)**: Enforces directory naming standards across categories, sub-topics, and courses.
- **Hierarchy Visualizer (`print`)**: Displays a clean, live annotated directory tree of your library.
- **Combined Health Check (`summary`)**: One-pass report combining linting status and course/video totals.
- **AI-Powered Triage (`triage`)**: Generates structured, context-rich prompts for LLMs (ChatGPT, Claude, Gemini) to organize unsorted courses into your library structure.

---

## Requirements

- **Python ≥ 3.11** (uses standard library `tomllib`)

---

## Quick Start

```bash
# Clone or place curator in your library
curator --help

# Run a combined health report
curator summary

# Audit video lesson counts
curator count

# Scan for directory naming violations
curator lint

# Print live full hierarchy
curator print

# Generate AI triage context for unsorted items
curator triage
```

---

## Commands & Usage

### 1. `count` — Lesson Auditor

Walks every course in the library and prints a formatted table showing section and video counts per course.

```bash
# Audit full library (staging directory excluded by default)
curator count

# List available top-level categories
curator count --list-categories

# Filter by category name (case-insensitive)
curator count --filter Networking

# Include unsorted staging directory in count
curator count --unsorted

# Format output (text, markdown, json)
curator count --format json
```

### 2. `lint` — Naming Convention Linter

Scans category, sub-topic, and course folder names against regex rules defined in `courses.toml`.

```bash
# Scan full library
curator lint

# Skip top-level category validation
curator lint --no-categories

# Quiet mode (exit code only: 0 = clean, 1 = violations)
curator lint --quiet
```

### 3. `print` — Live Full Hierarchy

Outputs an annotated directory tree showing courses, sub-topics, sections, and lesson counts.

```bash
# Print hierarchy to stdout
curator print

# Filter to specific category
curator print --filter 02_Linux

# Output as markdown (ready for docs or README)
curator print --format markdown
```

### 4. `summary` — Health Report

Runs linting and lesson auditing in a single pass to produce a box-bordered executive summary.

```bash
curator summary
curator summary --format markdown
```

### 5. `triage` — AI-Ready Unsorted Context Dump

Generates a context payload containing your library rules, category decision guide, and unsorted directory scan. Paste this into an AI model to receive exact `mv` commands and target paths.

```bash
# Standard triage dump
curator triage

# Prevent truncation of long subdirectory / file listings
curator triage --full

# Output individual self-contained blocks per unsorted item
curator triage --each

# Output as markdown (ideal for LLM web interfaces)
curator triage --format markdown
```

---

## Configuration (`courses.toml`)

Curator is driven entirely by `courses.toml` located at your library root. A sample template is provided in `courses.toml.example`.

```toml
[library]
name = "IT-DevOps Course Library"
unsorted_dir = "0x0_unsorted"
excluded_dirs = [".git", "utils", "0x0_unsorted"]

[naming.rules]
category = "NN_Title_Case — two-digit numeric prefix + Title_Case"
subtopic = "Title_Case — underscores only, no spaces or hyphens"
course = "Source_CourseName"

[triage.prompt]
title = "AI Task Prompt"
preamble = "For each item above, provide:"
instructions = [
    "Suggested target path",
    "Suggested renamed folder/file",
    "The exact `mv` shell command",
    "Confidence level",
    "Notes"
]
```

---

## Standalone Setup / Installation

To use Curator as a standalone project for any media/course library:

1. Copy `curator` and `_curator_lib.py` into your system `PATH` (e.g., `~/.local/bin/`) or your project's scripts folder.
2. Copy `courses.toml.example` to `courses.toml` in your library root directory.
3. Customize `courses.toml` with your own categories, naming rules, and triage criteria.

Curator automatically detects `courses.toml` in your current working directory (`CWD`) or the parent directory of `curator`.

---

## License

MIT License
