# Mkd

`mkd` combines `mkdir -p` and `cd` into a single command. It creates one or more directories (including any intermediate parent paths) and then navigates into the result. When multiple directories are created at once, it uses `fzf` to let you pick which one to enter.

## Usage

```bash
./mkd <directory> [directory2 ...]
```

### Options

| Flag | Description |
| :--- | :---------- |
| `-h`, `--help` | Show help message |

## Examples

```bash
# Create and enter a single nested directory
./mkd projects/new-idea

# Create multiple directories, then fzf-pick which to enter
./mkd dir1 dir2 dir3
```

## Requirements

- `fzf` — required only when creating **multiple** directories at once.

## Important: `cd` Limitation

As a standalone script, `cd` runs in a subprocess and **cannot change your parent shell's working directory**. The script prints the created path to stdout, but your shell will not navigate there.

To get the full `cd` behaviour, add a shell function wrapper to your `~/.zshrc` or `~/.bashrc`:

```bash
# Bash wrapper
mkd() {
    local target
    target=$(command mkd --print-dir "$@") && mkdir -p "$@" && cd "$target"
}
```

```zsh
# Zsh wrapper (add to ~/.zshrc)
mkd() {
    local dirs=("$@")
    command mkdir -p "${dirs[@]}" || return 1
    if (( ${#dirs[@]} > 1 )); then
        local selected
        selected=$(printf '%s\n' "${dirs[@]}" | fzf --prompt="Select directory: " --height=~50%)
        [[ -n "$selected" ]] && cd "$selected" && pwd
    else
        cd "${dirs[1]}" && pwd
    fi
}
```

> [!TIP]
> The Zsh shell function above is the recommended approach and mirrors the original behaviour from the system shell config exactly.

## Getting Started

```bash
chmod +x mkd

# Optional: symlink to PATH for the standalone mkdir-only usage
ln -s "$(pwd)/mkd" ~/.local/bin/mkd
```
