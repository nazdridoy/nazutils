# ghdummypatgen

`ghdummypatgen` is a simple Python CLI utility to generate dummy GitHub Personal Access Tokens (PATs) and workflow keys. This is useful for generating realistic dummy credentials for test environments, test fixtures, documentation examples, or validating secrets scanning configurations.

## Features

Generates realistic mock tokens conforming to GitHub's official formats:
- **Classic Personal Access Tokens** (`ghp_` prefix followed by 36 characters)
- **GitHub Actions / Server Tokens** (`ghs_` prefix followed by 36 characters)
- **Fine-grained Personal Access Tokens** (`github_pat_` prefix followed by 22 characters, an underscore, and 59 characters)

---

## Installation & Setup

Ensure you have Python 3 installed. No external dependencies are required.

1. Make the script executable:
   ```bash
   chmod +x ghdummypatgen
   ```

2. Run it directly or place it in your local `PATH` (e.g., `~/.local/bin` or `/usr/local/bin`):
   ```bash
   # Example of copying to a bin folder in your home directory
   cp ghdummypatgen ~/.local/bin/ghdummypatgen
   ```

---

## Usage

```bash
./ghdummypatgen [num_keys]
```

### Arguments

- `num_keys` (optional): The number of keys to generate for each token type. Defaults to `5` if not specified.

---

## Examples

### 1. Generate 2 keys per type
Running `./ghdummypatgen 2` produces:
```text
ghp_R3A7rT9x8qZ4mK2pL5wY6zN8vB1cD3fG5hJ9
ghp_k2m8P4N9zB1c3fG5hJ9y6wY8vL5rT7xQ2aZ4
ghs_M9n2b7vC5x3z1aQ8wE6rT4yU5iO3pP0aD2fG
ghs_t8y6u4i2o0p8a6s4d2f0g8h6j4k2l0z9x7c5
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6j4k
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2a6
```
*(Note: The actual characters generated will be randomized ascii letters and digits on each run)*
