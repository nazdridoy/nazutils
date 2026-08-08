# Ex

`ex` is a universal archive extractor. It detects the archive format by file extension and calls the appropriate extraction tool automatically, so you never need to remember which flags go with which format.

## Supported Formats

| Extension(s)              | Tool used       |
| :------------------------ | :-------------- |
| `.tar.gz`, `.tgz`         | `tar xzf`       |
| `.tar.bz2`, `.tbz2`       | `tar xjf`       |
| `.tar.xz`, `.tar.zst`     | `tar xf`        |
| `.tar`                    | `tar xf`        |
| `.gz`                     | `gunzip`        |
| `.bz2`                    | `bunzip2`       |
| `.rar`                    | `unrar x`       |
| `.zip`                    | `unzip`         |
| `.Z`                      | `uncompress`    |
| `.7z`                     | `7z x`          |
| `.deb`                    | `ar x`          |

## Usage

```bash
./ex <archive> [archive2 ...]
```

### Options

| Flag | Description |
| :--- | :---------- |
| `-h`, `--help` | Show help message |

## Examples

```bash
# Extract a single archive
./ex archive.tar.gz

# Extract multiple archives at once
./ex file1.zip file2.tar.bz2 file3.7z
```

## Getting Started

```bash
chmod +x ex

# Optional: symlink to your PATH
ln -s "$(pwd)/ex" ~/.local/bin/ex
```

> [!NOTE]
> Each format requires its respective extraction tool to be installed (`tar`, `unzip`, `unrar`, `7z`, `bunzip2`, `uncompress`, `ar`). The script will fail gracefully if the required tool is missing.
