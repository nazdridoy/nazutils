# nazutils

`nazutils` is a personal collection of nano-projects, helper scripts, and CLI utilities. While developed primarily for personal workflows, they are shared as open source in case they are useful to others.

Each utility is self-contained in its own directory with a dedicated `README.md` explaining its options and usage.

---

## Utilities Overview

| Utility | Directory | Language | Description |
| :--- | :--- | :---: | :--- |
| **`seqrename`** | [`Seqrename/`](./Seqrename) | Python | Sequentially batch-renames files with customizable prefix, padding, gap-filling, and interactive previews. |
| **`mdassetdl`** | [`Mdassetdl/`](./Mdassetdl) | Python | Downloads remote static assets (images, GIFs) in Markdown notes locally and rewrites URL paths to relative links. |
| **`mdtablefix`** | [`Mdtablefix/`](./Mdtablefix) | Python | Scans and fixes Markdown tables that lack a preceding blank line required for proper rendering. |
| **`ghdummypatgen`** | [`Ghdummypatgen/`](./Ghdummypatgen) | Python | Generates randomized, mock GitHub Personal Access Tokens and workflow keys (`ghp_`, `ghs_`, `github_pat_`) for testing. |
| **`tab2callout`** | [`Tab2callout/`](./Tab2callout) | Python | Reads HTML tab widgets (`wps_tabs` format) from stdin and converts each tab into an Obsidian-style collapsible callout. |
| **`base64imgbank`** | [`Base64imgbank/`](./Base64imgbank) | Bash | Extracts inline base64 images from Markdown files to a separate image bank note, replacing them with clean Obsidian-style backlinks. |
| **`fontstyle`** | [`Fontest/`](./Fontest) | Bash | Displays a colorized terminal test pattern checking ANSI escape sequences (bold, italic, colors, etc.). |
| **`fontsymbols`** | [`Fontest/`](./Fontest) | Bash | Renders a table preview of various Nerd Fonts icon ranges to check glyph compatibility and boundary clipping. |

---

## Getting Started

### 1. Requirements
- Most utilities require **Python 3.8+** (standard library only, no `pip install` required).
- Bash scripts require a Bash-compatible environment (Linux, macOS, or WSL).

### 2. Make Executable
To run a utility, make its script executable:
```bash
chmod +x <utility-folder>/<utility-name>

# Example:
chmod +x Seqrename/seqrename
```

### 3. Global Installation (Optional)
If you want to run a specific command from anywhere on your system, you can symlink it to a folder in your local `PATH` (typically `~/.local/bin` or `/usr/local/bin`):

```bash
# Example: Symlinking seqrename to your local bin directory
ln -s "$(pwd)/Seqrename/seqrename" ~/.local/bin/seqrename
```

> [!NOTE]
> These tools are completely independent. You only need to set up and run the specific utilities that are useful to your own workflows.
