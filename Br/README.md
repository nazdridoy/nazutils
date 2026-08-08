# Br

`br` is an ephemeral bridge interface manager for Linux. It wraps `ip link` bridge operations into a clean, composable CLI with coloured output. Bridges created with `br` are **lost on reboot** — for persistent bridges, use `nmcli`.

## Usage

```
br <subcommand> [args] [--options]
```

## Subcommands

| Subcommand | Syntax | Description |
| :--------- | :----- | :---------- |
| `create`   | `br create <name> [--stp]` | Create and bring up a bridge |
| `destroy`  | `br destroy <name>` | Tear down and remove a bridge |
| `attach`   | `br attach <iface> <bridge>` | Attach a network interface to a bridge |
| `detach`   | `br detach <iface>` | Detach an interface from its bridge |
| `ip`       | `br ip <bridge> <cidr>` | Assign an IP address to a bridge |
| `list`     | `br list` | Show all bridge member links |
| `status`   | `br status [<name>]` | Show state of one or all bridges |
| `bulk`     | `br bulk create <prefix> <count> [--stp]` | Create N bridges named `<prefix>1`…`<prefix>N` |
| `bulk`     | `br bulk destroy <prefix> <count>` | Destroy N bridges by prefix |
| `help`     | `br help` | Show help |

## Options

| Flag | Description |
| :--- | :---------- |
| `--stp` | Keep STP enabled on creation (default: STP disabled for faster link-up) |

## Examples

```bash
# Create a bridge, assign an IP, and attach an interface
br create br-lab
br ip br-lab 192.168.100.1/24
br attach eth1 br-lab

# Check the state of all bridges
br status

# Create 5 bridges with the prefix "br-test"
br bulk create br-test 5

# Tear them all down
br bulk destroy br-test 5

# Remove a single bridge and its member
br detach eth1
br destroy br-lab
```

## Requirements

| Dependency     | Package        | Purpose |
| :------------- | :------------- | :------ |
| `ip`           | `iproute2`     | Create/delete bridge links |
| `bridge`       | `bridge-utils` | List bridge members (`bridge link show`) |
| `sudo`         | —              | `ip link` operations require root |

> [!NOTE]
> Bridges created with this tool are **ephemeral** and are lost on reboot. For persistent bridges, use `nmcli` or configure them in your network manager.

> [!TIP]
> STP (Spanning Tree Protocol) is disabled by default to avoid the 30-second port forwarding delay. Pass `--stp` to keep it enabled if you have loops in your network topology.

## Getting Started

```bash
chmod +x br

# Symlink to PATH for global access
ln -s "$(pwd)/br" ~/.local/bin/br
```
