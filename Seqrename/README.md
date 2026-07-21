# Seqrename

`seqrename` is a Python CLI tool to sequentially rename files in a directory. It handles batch renaming to structured patterns (like `prefix-001.ext`) while letting you preview changes and safely fill gaps in existing sequences.

## Features

- **Custom Prefix & Padding**: Specify a prefix and zero-padded digit length (e.g., `image-001.png`).
- **Interactive Preview**: Shows a dry-run preview of all proposed renames and prompts before executing.
- **Gap-Filling**: Automatically detects and uses missing sequence numbers in the target pattern (e.g., fills in `prefix-002.ext` if `001` and `003` exist).
- **Collision Protection**: Aborts immediately if a rename would overwrite an existing file.
- **Smart Filtering**: Skips hidden files, the script itself, and files that already match the target pattern.

---

## Installation & Setup

Ensure you have Python 3 installed. No external dependencies are required.

1. Make the script executable:
   ```bash
   chmod +x seqrename
   ```

2. Run it directly or place it in your local `PATH` (e.g., `~/.local/bin` or `/usr/local/bin`):
   ```bash
   # Example of copying to a bin folder in your home directory
   cp seqrename ~/.local/bin/seqrename
   ```

---

## Usage

```bash
./seqrename -p <prefix> -n <digits> [options]
```

### Options

| Flag | Long Option | Description | Required | Default |
| :--- | :--- | :--- | :---: | :--- |
| `-p` | `--prefix` | Prefix for new filenames. | **Yes** | - |
| `-n` | `--digits` | Number of digits for sequence padding. | **Yes** | - |
| `-t` | `--path` | Target directory containing the files. | No | `.` (current directory) |
| `-f` | `--fill-gaps` | Fill existing sequence gaps before appending new numbers. | No | `False` |
| `-y` | `--yes` | Skip the interactive confirmation prompt. | No | `False` |

---

## Examples

### 1. Basic Sequential Renaming
Suppose you have a folder of new wallpapers:
- `cyberpunk_street.png`
- `cozy_cabin.jpg`

Running the following command to organize them:
```bash
./seqrename -p wallpaper -n 3
```

Shows this preview and asks for confirmation:
```text
--- Preview: 2 files to rename ---
  cozy_cabin.jpg -> wallpaper-001.jpg
  cyberpunk_street.png -> wallpaper-002.png

(-y to skip confirmation, Ctrl+C to abort)
Proceed? [y/N]
```
Pressing `y` will rename the files to `wallpaper-001.jpg` and `wallpaper-002.png`.

### 2. Gap-Filling Mode
Suppose you already have organized wallpapers:
- `wallpaper-001.png`
- `wallpaper-003.jpg` (notice `002` is missing!)

If you download a new image `space_nebula.png` and want to fill the gap first:
```bash
./seqrename -p wallpaper -n 3 -f
```

It scans the directory, finds the missing index `2`, and maps it:
```text
--- Preview: 1 files to rename ---
  space_nebula.png -> wallpaper-002.png
```

Without the `-f` flag, `space_nebula.png` would have been named `wallpaper-004.png`.

### 3. Skip Confirmation
To run renames instantly without a prompt:
```bash
./seqrename -p wallpaper -n 3 -y
```
