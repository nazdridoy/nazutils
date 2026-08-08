# Qcow2compress

`qcow2-compress` compresses a QEMU qcow2 disk image in-place using sparse conversion via `qemu-img`. It eliminates wasted space from deleted guest data without modifying the VM configuration.

## How It Works

The script converts the image to a new compressed temporary file first. If conversion succeeds, the temp file atomically replaces the original. If it fails, the original is left untouched and the temp file is cleaned up.

```
disk.qcow2 ──► qemu-img convert -c ──► disk.qcow2.tmp
                                              │ success
                                              ▼
                                        mv → disk.qcow2
```

## Requirements

| Dependency  | Package      |
| :---------- | :----------- |
| `qemu-img`  | `qemu-utils` |

## Usage

```bash
./qcow2-compress <disk.qcow2>
```

### Options

| Flag | Description |
| :--- | :---------- |
| `-h`, `--help` | Show help message |

## Examples

```bash
# Compress a disk image in the current directory
./qcow2-compress vm-disk.qcow2

# Compress a disk image at an absolute path
./qcow2-compress /var/lib/libvirt/images/my-vm.qcow2
```

> [!IMPORTANT]
> Shut down the VM before compressing its disk image. Compressing a live disk that is being written to will corrupt the resulting image.

> [!NOTE]
> Compression ratio depends heavily on how much free/deleted space is inside the guest filesystem. Running a guest-side `fstrim` (or `zerofill`) before compressing maximises the savings.

## Getting Started

```bash
chmod +x qcow2-compress

# Optional: symlink to PATH
ln -s "$(pwd)/qcow2-compress" ~/.local/bin/qcow2-compress
```
