# mdtablefix

`mdtablefix` is a simple Python CLI utility that checks and fixes Markdown tables lacking a preceding empty line. Many Markdown parsers (including GitHub, VS Code, Obsidian, and standard processors) require a blank line before a table header to correctly identify and render it as a table.

## Features

- **Dry-run Scan**: Shows a visual, colorized diff of files needing fixes and the exact lines involved before writing anything.
- **In-place Auto-fixing**: Automatically inserts a blank line before table headers with the `--apply` flag.
- **Code Block Protection**: Safely ignores tables inside code blocks (fenced with ` ``` `).
- **Target Filtering**: Recursively searches the target folder while ignoring hidden directories (like `.git`).

---

## Installation & Setup

Ensure you have Python 3 installed. No external dependencies are required.

1. Make the script executable:
   ```bash
   chmod +x mdtablefix
   ```

2. Run it directly or place it in your local `PATH` (e.g., `~/.local/bin` or `/usr/local/bin`):
   ```bash
   # Example of copying to a bin folder in your home directory
   cp mdtablefix ~/.local/bin/mdtablefix
   ```

---

## Usage

```bash
./mdtablefix [target_directory] [options]
```

### Options

| Option / Argument | Description | Required | Default |
| :--- | :--- | :---: | :--- |
| `target_directory` | The path to scan. | No | Parent directory of the script |
| `--apply` | Write the fixes (insert blank lines) in-place to modified files. | No | Dry-run (scan only) |
| `-h`, `--help` | Show the help message and exit. | No | — |

---

## Examples

### 1. The Issue
If a markdown file contains a table without a preceding blank line, it may render as plain text:
```markdown
Here is the table info:
| Header A | Header B |
| :--- | :--- |
| Cell 1 | Cell 2 |
```

### 2. Dry-run Scan
Running `./mdtablefix` scans the directory:
```text
✨ mdtablefix ✨
────────────────────────────────────────────────────────────
📂 Target: /home/user/vault
⚙️  Mode: Dry-run (Scan only)
────────────────────────────────────────────────────────────

●  DRY-RUN  notes/cheatsheet.md:14
     13 | Here is the table info:
     +    [Insert blank line]
     14 | | Header A | Header B |

────────────────────────────────────────────────────────────
SUMMARY
────────────────────────────────────────────────────────────
  📁 Files checked:   5
  ⚠️  Broken files:   1
  ⚙️  Status:         1 files require fixes
────────────────────────────────────────────────────────────

👉 Run with --apply to automatically apply all fixes:
   ./mdtablefix --apply
```

### 3. Applying the Fix
Run the script with the `--apply` flag to fix the files in-place:
```bash
./mdtablefix --apply
```

This updates the file so it renders correctly:
```markdown
Here is the table info:

| Header A | Header B |
| :--- | :--- |
| Cell 1 | Cell 2 |
```
