# mdassetdl

A zero-dependency Python utility for Markdown note vaults. It finds remote image and GIF links in `.md` files, downloads them locally, rewrites the links to relative paths, and keeps the original URLs as invisible inline comments.

> **No `pip install` required** — Python 3.8+ standard library only.

---

## How It Works

```
1. Scan    →  find all remote image links in the target .md file(s)
2. Preview →  show a summary table of what will happen
3. Confirm →  prompt to proceed, view details, or review file-by-file
4. Execute →  download assets and/or rewrite links
```

Nothing is written until you confirm. Press `Ctrl+C` or answer `N` at any prompt to abort cleanly.

---

## Quick Start

```bash
# One file
./mdassetdl "CCNA_Sem_1/Module 1 - Networking Today.md"

# All .md files in a directory (top-level only, non-recursive)
./mdassetdl CCNA_Sem_1/

# Strip a common filename prefix for cleaner asset subfolder names
./mdassetdl CCNA_Sem_1/ --strip-prefix "CCNA 1 v7.0 Curriculum "
```

---

## Asset Directory Structure

When the target is a **directory**, each `.md` file gets its own subfolder inside `Assets/`.
This keeps assets isolated per-file, prevents cross-file filename conflicts, and stays manageable even with hundreds of files.

```
Assets/
  Module-1-Networking-Today/       ← subfolder named from the .md stem
    2020-05-20_201301.jpg
    End-Devices.gif
  Module-2-Basic-Switch-Config/
    diagram.jpg
  Module-3-Protocols-and-Models/
    network-model.png
```

When the target is a **single `.md` file**, a flat layout is used:

```
Assets/
  image.jpg
  End-Devices.gif
```

Use `--flat-assets` to force the flat layout even for a directory target.

---

## Link Format After Update

Every rewritten link keeps the original URL as a standard HTML comment on the next line — universally hidden in GitHub, VS Code, Obsidian (Reading View + Live Preview), and all CommonMark-compliant renderers:

```markdown
Before:
  ![](https://itexamanswers.net/wp-content/uploads/2020/05/End-Devices.gif)

After:
  ![](Assets/Module-1-Networking-Today/End-Devices.gif)
  <!-- original: https://itexamanswers.net/wp-content/uploads/2020/05/End-Devices.gif -->
```

---

## Preview & Confirmation

### Single file

```
  [PREVIEW] Summary
  ────────────────────────────────────────────────────────────────────────
  File                                                  Found    DL  Update  Skip
  Module 1 - Networking Today.md                           35    33      33     2
  ────────────────────────────────────────────────────────────────────────
  Total: 33 to download | 33 links to update | 2 video links skipped

  [d] Show detail   [g] Go ahead   [a] Abort
  Choice [d/g/a]: d

  > Module 1 - Networking Today.md
  ──────────────────────────────────────────────────────────────────
  + [Module 1...:  72]  DOWNLOAD -> Module-1-Networking-Today/2020-05-20_195543.jpg
                        from https://itexamanswers.net/.../2020-05-20_195543.jpg
  + [Module 1...: 121]  DOWNLOAD -> Module-1-Networking-Today/End-Devices.gif
                        from https://itexamanswers.net/.../End-Devices.gif
  ! [Module 1...:  60]  SKIP  https://www.youtube.com/watch?v=...  <- video link
  ! [Module 1...: 464]  SKIP  https://www.youtube.com/watch?v=...  <- video link

  Choice [d/g/a]: g
```

### Directory (multiple files)

```
  [PREVIEW] Summary
  ────────────────────────────────────────────────────────────────────────
  File                                                  Found    DL  Update  Skip
  Module 1 - Networking Today.md                           35    33      33     2
  Module 2 - Basic Switch and End Device Config.md         25    17      17     8
  Module 3 - Protocols and Models.md                       39    38      38     1
  ...
  ────────────────────────────────────────────────────────────────────────
  Total: 432 to download | 432 links to update | 34 video links skipped

  [d] Detailed view (opens pager)
  [f] File-by-file review
  [g] Go ahead (trust summary)
  [a] Abort
  Choice [d/f/g/a]:
```

| Choice | Behaviour |
|---|---|
| `d` | Opens the full per-asset detail in `$PAGER` → `less` → `more` → `pydoc` → print |
| `f` | Walk through each file one by one: `[y] Yes, process` / `[s] Skip this file` / `[a] Abort all` |
| `g` | Execute immediately, trust the summary |
| `a` | Abort — nothing written |

### Real-time download progress

```
  > Module 1 - Networking Today.md
    [1/33] Downloading: 2020-05-20_195543.jpg  ✓
    [2/33] Downloading: End-Devices.gif  ✓
    [3/33] Downloading: Network-Media.jpg  ✓
    ...
    Links updated: 33
```

---

## Restoring Backups

Before rewriting any `.md` file, the script saves a `.md.bak` beside it. Use `--restore` to roll back.

```bash
# Restore all backups in a directory
./mdassetdl CCNA_Sem_1/ --restore

# Restore a single file's backup
./mdassetdl "CCNA_Sem_1/Module 1 - Networking Today.md" --restore

# Skip the confirmation prompt
./mdassetdl CCNA_Sem_1/ --restore --yes
```

```
  mdassetdl v2.0.0  [RESTORE MODE]
  Target : /home/.../CCNA_Sem_1

  [PREVIEW] Backup files found:
  ------------------------------------------------------------
  Module 1 - Networking Today.md.bak
    -> restore to: Module 1 - Networking Today.md  (exists)
  Module 2 - Basic Switch and End Device Config.md.bak
    -> restore to: Module 2 - Basic Switch and End Device Config.md  (exists)
  ...
  ------------------------------------------------------------
  17 file(s) will be restored.
  (Backup files are kept after restore.)

  Restore all? [y/N]:
```

> `.bak` files are **kept** after restore — you can restore again later without re-running the download.

---

## Video & Non-downloadable Links

YouTube, Vimeo, Twitch, and similar video embeds are detected and listed in the preview as **skipped**. They are never downloaded or modified.

```
  ! [Module 1...:  60]  SKIP  https://www.youtube.com/watch?v=Lj9egtxBdLg  <- video link
```

---

## All Options

```
./mdassetdl [options] target
```

| Flag | Short | Description |
|---|---|---|
| `target` | | Path to a `.md` file **or** a directory (top-level `.md` files only, non-recursive) |
| `--download-only` | | Download assets but do **not** modify the `.md` file |
| `--update-only` | | Rewrite links only — no downloading. Assets must already exist locally |
| `--assets-dir NAME` | | Asset folder name (default: `Assets`). Relative to target |
| `--flat-assets` | | Use a single flat `Assets/` folder instead of per-file subfolders |
| `--strip-prefix TEXT` | | Strip this prefix from `.md` stems when naming per-file subfolders. If omitted, the full stem is used |
| `--extensions EXT,...` | | Comma-separated extensions to download (default: `avif,bmp,gif,ico,jpeg,jpg,png,svg,tif,tiff,webp`) |
| `--force` | | Re-download assets even if they already exist locally |
| `--restore` | | Restore `.md.bak` backups, replacing current `.md` files |
| `--yes` | `-y` | Skip all confirmation prompts (scripting / CI) |
| `--verbose` | `-v` | Line-by-line log of every download and link update |
| `--version` | | Show version and exit |
| `--help` | `-h` | Show help and exit |

---

## Examples

```bash
# Full run — download + update links (single file):
./mdassetdl "CCNA_Sem_1/Module 1 - Networking Today.md"

# Full run — whole directory, shorter subfolder names:
./mdassetdl CCNA_Sem_1/ --strip-prefix "CCNA 1 v7.0 Curriculum "

# Download assets only, don't touch .md files:
./mdassetdl CCNA_Sem_1/ --download-only

# Update links only (assets already downloaded):
./mdassetdl CCNA_Sem_1/ --update-only

# Flat asset folder — everything in one Assets/ dir:
./mdassetdl CCNA_Sem_1/ --flat-assets

# Custom asset folder name:
./mdassetdl CCNA_Sem_1/ --assets-dir media

# Force re-download (overwrite existing files):
./mdassetdl CCNA_Sem_1/ --force

# Non-interactive — no prompts, auto-confirm:
./mdassetdl CCNA_Sem_1/ --yes

# Verbose output — see every download and link change:
./mdassetdl CCNA_Sem_1/ --verbose --yes

# Restore backups after a run:
./mdassetdl CCNA_Sem_1/ --restore
```

---

## Safety Guarantees

| Guarantee | Detail |
|---|---|
| **Preview before write** | Always shown; nothing written until you confirm |
| **Original URLs preserved** | Kept as `<!-- original: https://... -->` on the next line — hidden in GitHub, VS Code, and Obsidian |
| **Automatic backup** | `.md.bak` created beside each file before any link rewrite |
| **Restore any time** | `--restore` rolls back `.md` files from their `.bak` |
| **Idempotent** | Already-local links are never re-processed on a second run |
| **Cross-file conflict-free** | Per-file subfolders give each file its own asset namespace |
| **Intra-file collision-safe** | Two URLs with the same filename get a short hash suffix |
| **Video links untouched** | YouTube / Vimeo / etc. are detected and always skipped |
