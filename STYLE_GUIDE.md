# CLI Tool Style & Consistency Guide

This document establishes the consistency standards for all command-line interface (CLI) utilities in `nazutils`. Refer to these guidelines when modifying existing scripts or adding new tools.

---

## 1. Docstring Headers (Single Source of Truth)

To keep scripts clean and maintainable, top-level module docstrings must remain brief, high-level, and formatted consistently. Do **not** hardcode version numbers or detailed flags in the module docstring.

Every Python script must begin with a docstring using this exact layout:

```python
#!/usr/bin/env python3
"""
<prog_name>
================================
<A brief, action-oriented description of the utility>

Run  ./<prog_name> --help  for full usage.
"""
```

*Example:*
```python
#!/usr/bin/env python3
"""
seqrename
================================
Sequentially batch-renames files in a directory with customizable
prefix, padding, gap-filling, and interactive previews.

Run  ./seqrename --help  for full usage.
"""
```

---

## 2. Version Management

All tools must have a single source of truth for their version number to prevent inconsistencies:

1. **Define a Constant**: Always declare the version using a module-level string constant named `VERSION` immediately below the imports.
   ```python
   VERSION = "1.0.0"
   ```
2. **Expose the Version**: Add a standard `--version` CLI option utilizing `argparse`.
   ```python
   parser.add_argument(
       '--version', 
       action='version', 
       version=f'%(prog)s {VERSION}'
   )
   ```
3. **Dynamic Banners**: If the utility prints an execution header/banner, interpolate the `VERSION` constant and dynamic program name instead of hardcoding:
   ```python
   # Inside argparse context:
   print(f"\n✨ {parser.prog} v{VERSION} ✨")

   # Outside argparse context (e.g. standalone helper functions):
   prog_name = os.path.basename(sys.argv[0])
   print(f"\n✨ {prog_name} v{VERSION} ✨")
   ```

---

## 3. Command-Line Interface (argparse)

To ensure consistent `--help` menus, error checking, and option styling, all Python CLI tools must use Python's built-in `argparse` module:

- Do **not** hardcode the program name using the `prog` parameter in `argparse.ArgumentParser`. By omitting it, `argparse` automatically defaults to the actual filename (`os.path.basename(sys.argv[0])`). This allows the script to be renamed or symlinked without breaking help messages:
  ```python
  parser = argparse.ArgumentParser(
      description="Brief description..."
  )
  ```
- Use `%(prog)s` inside descriptions and epilogs to dynamically reference the program name (e.g., `./%(prog)s --apply`).
- Use `argparse.RawDescriptionHelpFormatter` if you want to include formatted multiline `epilog` blocks showing concrete command examples.
- Positional arguments, options, defaults, and type validation should be strictly handled through `parser.add_argument()`.

---

## 4. Dependencies & Runtime

- **No external dependencies**: Utilities must rely solely on Python's standard library. Do not require users to run `pip install`.
- **Portability**: Code should target compatibility with Python 3.8+ and run reliably on Linux, macOS, and WSL environments.
