# tab2callout

`tab2callout` is a Python CLI utility that reads HTML tab widgets (`wps_tabs` format) from stdin and converts each tab into an [Obsidian](https://obsidian.md)-style collapsible callout. No external dependencies - standard library only.

## Features

- **Clipboard-native**: Designed for `wl-paste | ./tab2callout | wl-copy` one-liners.
- **Rich content support**: Handles paragraphs, headings, ordered/unordered lists, code blocks (`<pre>`), images, tables, and nested elements.
- **Configurable callout type**: Override the default `note` type with any Obsidian callout keyword (`tip`, `info`, `warning`, `abstract`, …).
- **Zero dependencies**: Uses only Python 3 standard library (`html.parser`, `argparse`, `re`).

---

## Installation & Setup

Ensure you have Python 3 installed. No external dependencies are required.

1. Make the script executable:
   ```bash
   chmod +x tab2callout
   ```

2. Optionally place it in your `PATH`:
   ```bash
   cp tab2callout ~/.local/bin/tab2callout
   ```

---

## Usage

```bash
<input source> | ./tab2callout [options] | <output destination>
```

### Options

| Option | Description | Default |
| :--- | :--- | :--- |
| `--callout-type TYPE` | Obsidian callout type for each tab block | `note` |
| `--version` | Show version and exit | - |
| `-h`, `--help` | Show help message and exit | - |

---

## Examples

### Wayland clipboard (round-trip)
```bash
wl-paste | ./tab2callout | wl-copy
```

### X11 clipboard (round-trip)
```bash
xclip -o -sel clip | ./tab2callout | xclip -i -sel clip
```

### From a saved HTML file
```bash
cat page.html | ./tab2callout
```

### From an inline snippet
```bash
echo '<ul class="wps_tabs">...</ul>' | ./tab2callout
```

### Use a different callout type
```bash
wl-paste | ./tab2callout --callout-type tip
```

---

## Output Format

Each HTML tab becomes a collapsible Obsidian callout:

```markdown
> [!note]- **Tab Name**
>
> Tab content rendered as markdown…
```

The `-` after the type makes the callout collapsible by default in Obsidian. Change it to `+` in the output if you prefer expanded by default.

---

## Supported HTML Content

| HTML element | Rendered as |
| :--- | :--- |
| `<p>` | Paragraph |
| `<h1>`–`<h6>` | ATX headings (`#`–`######`) |
| `<ul>` / `<ol>` | Unordered / ordered list |
| `<pre>` | Fenced code block (` ``` `) |
| `<code>` | Inline code |
| `<strong>` / `<b>` | Bold (`**…**`) |
| `<em>` / `<i>` | Italic (`*…*`) |
| `<a>` | Markdown link `[text](url)` |
| `<img>` | Markdown image `![alt](src)` |
| `<table>` | GFM pipe table |
| `<br>` | Hard line break |
