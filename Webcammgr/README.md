# Webcammgr

`webcammgr` is an interactive terminal utility for managing webcam devices on Linux. It lists all detected video devices, shows their current enabled/disabled state, and lets you toggle access using an `fzf`-powered selection menu.

## Features

- Shows webcam module (`uvcvideo`) load status
- Lists all `/dev/video*` devices with access permissions
- Enable or disable **all** webcams by loading/unloading the kernel module
- Enable or disable **individual** devices by adjusting file permissions
- Interactive `fzf` menu — no flags to memorise

## Requirements

| Dependency | Package | Purpose |
| :--------- | :------ | :------ |
| `v4l2-ctl` | `v4l2-utils` | Enumerate devices and query capabilities |
| `fzf`      | `fzf`        | Interactive action selection |
| `sudo`     | —            | `modprobe` and `chmod` on device nodes |

## Usage

```bash
./webcammgr
```

No arguments needed. The script presents an interactive menu based on the current state of your webcam hardware.

### Menu Options

| Action | Effect |
| :----- | :----- |
| Enable all webcam devices | Runs `sudo modprobe uvcvideo` |
| Disable all webcam devices | Runs `sudo modprobe -r uvcvideo` |
| Enable `<device>` | Restores `660` permissions on `/dev/<device>` |
| Disable `<device>` | Removes all permissions (`000`) on `/dev/<device>` |
| Exit | Quits without changes |

> [!NOTE]
> Changes made by this tool are **ephemeral** — they are lost on reboot. Module state is restored by the kernel at next boot, and device permissions are reset by udev.

> [!CAUTION]
> This script uses `sudo` to load/unload kernel modules and modify device node permissions. Review the script before running it on shared systems.

## Getting Started

```bash
chmod +x webcammgr

# Optional: symlink to PATH
ln -s "$(pwd)/webcammgr" ~/.local/bin/webcammgr
```
