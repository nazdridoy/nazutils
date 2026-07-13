# base64imgbank

`base64imgbank` is a Bash script designed for Obsidian / Markdown vaults to extract inline base64 encoded images from notes. It saves the extracted base64 strings to a separate "image bank" note inside an `Images/` subdirectory and replaces the massive inline base64 blobs in your original note with clean, lightweight Obsidian-style backlinks.

## Features

- **Reduces Note Bloat**: Moves huge base64 strings out of your main notes so they load instantly and remain clean to edit.
- **Obsidian Backlinks**: Replaces the inline base64 data with standard Obsidian backlinks (`![[Images/note_image_Bank.md#ID_xxx]]`), preserving image rendering inside Obsidian.
- **Safety Backup**: Creates a `.bak` backup of your original note before modifying anything.
- **Automated Directory Structure**: Automatically creates the `Images/` subfolder relative to your note if it doesn't already exist.

---

## Installation & Setup

Ensure you are using a Bash-compatible environment (Linux, macOS, or WSL).

1. Make the script executable:
   ```bash
   chmod +x base64imgbank
   ```

2. Run it directly or place it in your local `PATH` (e.g., `~/.local/bin` or `/usr/local/bin`):
   ```bash
   # Example of copying to a bin folder in your home directory
   cp base64imgbank ~/.local/bin/base64imgbank
   ```

---

## Usage

```bash
./base64imgbank <path_to_note.md>
```

---

## Example

### 1. Before
If you have a note `my_note.md` containing a base64 image:
```markdown
# My Note
Here is an image:
![alt text](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADIA... "optional title")
```

### 2. Running the script
```bash
./base64imgbank my_note.md
```

### 3. After
A backup of your note is created as `my_note.md.bak`, and the following changes are made:

**`my_note.md` is updated to:**
```markdown
# My Note
Here is an image:
![[Images/my_note_image_Bank.md#ID_1720894567000000000]]
```

**An image bank file `Images/my_note_image_Bank.md` is created with:**
```markdown
###### ID_1720894567000000000
![alt text](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADIA... "optional title")
```
