# Fontest

`Fontest` is a utility folder containing lightweight terminal/font capability check scripts. These tools help verify ANSI escapes, styling capabilities, colors, and Nerd Font symbols/glyphs rendering in your current terminal emulator.

## Scripts Included

### 1. `fontstyle`
Tests terminal rendering for basic ANSI escape sequences (styles and colors).
- **Styles Tested**: Bold, Italic, Underline, Blink, Reverse, and Hidden.
- **Colors Tested**: Red, Green, Yellow, Blue, Magenta, Cyan, and White.

**Usage**:
```bash
./fontstyle
```

---

### 2. `fontsymbols`
Tests the rendering of Nerd Font symbols (glyphs) across different popular icon ranges (Pomicons, Powerline, Devicons, Font Awesome, Octicons, Material Design Icons, Weather Icons, etc.).
- Helps identify if your active font correctly implements Nerd Font icons, and visually checks if symbols overflow cell boundaries.

**Usage**:
```bash
./fontsymbols [columns]
```
- `columns` (optional): Set custom column wrap width for the symbol preview table (default: `16`).

**Example**:
```bash
# Render symbol table with 8 columns
./fontsymbols 8
```
