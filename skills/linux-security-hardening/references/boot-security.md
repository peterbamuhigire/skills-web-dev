# Boot Security (Debian 12 / Ubuntu 24.04)

Purpose: Harden the boot chain — GRUB, Secure Boot, kernel lockdown, and LUKS —
so physical or console access cannot bypass the operating system.

## Why boot security matters

Linux authentication stops at userspace. Anyone with physical or console
access to an unhardened server can edit the GRUB kernel command line, boot
into single-user mode by appending `init=/bin/bash`, and get a root shell
without any password. From there they can reset the root password, add an
SSH key, or dump `/etc/shadow`. Cloud KVM consoles, iDRAC, and iLO expose
the same attack surface remotely. Every boot stage — firmware, bootloader,
initramfs, kernel — must refuse to load unauthorised code, and the disk
itself should refuse to give up plaintext without a key.

## GRUB password protection

GRUB supports PBKDF2-hashed passwords that gate any attempt to edit boot
entries at the menu.

```bash
sudo grub-mkpasswd-pbkdf2
# Enter password twice; it prints: grub.pbkdf2.sha512.10000.<salt>.<hash>
```

Append to `/etc/grub.d/40_custom` (do not edit `grub.cfg` directly):

```bash
cat <<'EOF' | sudo tee -a /etc/grub.d/40_custom
set superusers="admin"
password_pbkdf2 admin grub.pbkdf2.sha512.10000.<SALT>.<HASH>
EOF

sudo update-grub
```

To keep unauthenticated users able to boot the default entry but require a
password to edit it, add `--unrestricted` to each menu entry in
`/etc/grub.d/10_linux`.

What this prevents:

- Editing the kernel command line at the menu to add `init=/bin/bash`,
  `rw`, or `single`.
- Booting an alternative kernel or rescue entry.

What this does not prevent:

- Booting from USB or PXE — disable those in BIOS/UEFI.
- Pulling the disk and reading it on another machine — that needs disk
  encryption.
- Firmware-level tampering — that needs a BIOS password and Secure Boot.

## UEFI Secure Boot

Secure Boot verifies signatures on the bootloader and kernel. A rootkit
replacing `/boot/grubx64.efi` fails verification and UEFI refuses to hand
off control.

Debian 12 and Ubuntu 24.04 both ship signed packages out of the box:
`shim-signed`, `grub-efi-amd64-signed`, and signed kernels in `linux-image-*`.

Verify current state:

```bash
mokutil --sb-state
# SecureBoot enabled   -> good
# SecureBoot disabled  -> enable in UEFI firmware setup
```

Signing your own kernel modules (for example, an out-of-tree driver):

```bash
# Generate a one-off MOK (Machine Owner Key)
openssl req -new -x509 -newkey rsa:2048 -keyout MOK.key -outform DER \
    -out MOK.der -nodes -days 3650 -subj "/CN=local module signing/"

# Import the key; you will set a one-time password
sudo mokutil --import MOK.der

# Reboot; MOK Manager prompts you to enrol the key by typing that password
sudo reboot

# After reboot, sign the module
sudo /usr/src/linux-headers-$(uname -r)/scripts/sign-file sha256 \
    MOK.key MOK.der /lib/modules/$(uname -r)/extra/mymodule.ko
```

## Kernel lockdown mode

Linux supports a runtime "lockdown" state that restricts what even a root
user can do when Secure Boot is active. It blocks loading unsigned modules,
writing to `/dev/mem`, arbitrary `kexec`, unsafe BPF, reading kernel memory
via kprobes, and other kernel-integrity bypass paths.

```bash
cat /sys/kernel/security/lockdown
# none / [integrity] / confidentiality
```

- `none` — locked down features unrestricted.
- `integrity` — kernel runtime integrity is protected; this is what Secure
  Boot should trigger automatically on modern kernels.
- `confidentiality` — also blocks reading kernel memory, which can prevent
  some debugging tools.

Force a lockdown level at boot by adding `lockdown=integrity` to the kernel
command line in `/etc/default/grub`:

```bash
GRUB_CMDLINE_LINUX_DEFAULT="quiet splash lockdown=integrity"
sudo update-grub
```

## Disk encryption with LUKS

LUKS (Linux Unified Key Setup) is the standard full-disk encryption format
for Linux. It encrypts the block device and stores one or more keyslots in
a header; any keyslot can unlock the master key.

- Debian installer offers "Guided — use entire disk and set up encrypted
  LVM" — pick it at install time whenever possible; retrofitting LUKS
  to an existing system is disruptive.
- Use LUKS2 (the default on Debian 12 / Ubuntu 24.04); it uses Argon2id
  for key derivation and has more resistance to GPU/ASIC brute force than
  LUKS1.

Inspect an existing volume:

```bash
sudo cryptsetup luksDump /dev/nvme0n1p3
# Shows version (LUKS2), cipher, key derivation, and each keyslot
```

Manage keyslots:

```bash
# Add a second passphrase (for a recovery key, for example)
sudo cryptsetup luksAddKey /dev/nvme0n1p3

# Remove a keyslot
sudo cryptsetup luksKillSlot /dev/nvme0n1p3 1
```

### Unattended unlock for servers

A headless server cannot prompt for a passphrase at boot. Two common
patterns for network-bound disk encryption:

- **Clevis + Tang** — the server stores an encrypted "binding" in the LUKS
  header. At boot, it contacts a Tang server on the management network to
  recover the unlock key. If the Tang server is unreachable, the disk stays
  encrypted.

  ```bash
  sudo apt install -y clevis clevis-luks clevis-initramfs

  # Bind slot to a Tang server
  sudo clevis luks bind -d /dev/nvme0n1p3 tang \
      '{"url":"http://tang.internal.example.com"}'

  sudo update-initramfs -u -k all
  ```

- **TPM 2.0** — bind the key to the server's TPM so it only unlocks on
  that specific hardware. Use `clevis-tpm2` or `systemd-cryptenroll`:

  ```bash
  sudo systemd-cryptenroll --tpm2-device=auto \
      --tpm2-pcrs=0+2+7 /dev/nvme0n1p3
  ```

  PCR bindings tie the unlock to the measured boot state; a firmware
  change will break the seal (which is usually what you want).

## Initramfs protection

The initramfs runs before any root filesystem is mounted. An attacker who
can write to `/boot` can inject a trojan that captures the LUKS passphrase.

- On Secure Boot systems `/boot/vmlinuz-*` and `/boot/initrd.img-*` are
  signed as part of the kernel package; UEFI verification catches tampering
  with the kernel image.
- Add `/boot/vmlinuz-*`, `/boot/initrd.img-*`, `/boot/grub/grub.cfg`, and
  `/etc/default/grub` to your file integrity baseline (AIDE, Wazuh FIM,
  Tripwire) and alert on any change outside an apt transaction.
- For maximum protection, mount `/boot` read-only and remount only during
  kernel updates.

## Physical access mitigations

Boot security is worthless if an attacker can open the case and clone the
disk. Defences in depth:

- Locked server room or colocation cage.
- Chassis intrusion switch wired to the BMC.
- BIOS/UEFI supervisor password on every server.
- Boot order restricted to the internal disk; USB/PXE boot disabled.
- Measured boot events forwarded to the SIEM.
- Console (KVM, iDRAC, iLO) on a dedicated management VLAN behind the
  firewall, not routable from the internet.

## Anti-patterns

- Deploying a multi-admin server with no GRUB password, under the
  assumption that nobody will be at the console. Cloud KVM consoles count.
- Disabling Secure Boot "to get a vendor driver to load" and forgetting to
  re-enable it — sign the module properly with a MOK instead.
- LUKS with a weak passphrase like `Passw0rd!`. Argon2id is strong but
  cannot save a dictionary word; use a diceware passphrase of 6+ words.
- Running with `lockdown=none` on a Secure Boot system; you lose most of
  the integrity protections Secure Boot is supposed to provide.
- Storing the Clevis Tang server on the same network as the encrypted
  server and sharing power/uplink; a single outage takes both offline.
- Forgetting to back up the LUKS header (`cryptsetup luksHeaderBackup`) —
  header corruption turns the disk into a brick.

## Cross-references

- `linux-security-hardening/references/patch-management.md` — reboot
  coordination for kernel updates that re-run the Secure Boot chain.
- `linux-security-hardening/references/cis-benchmark-checklist.md` — audit
  controls for bootloader permissions and Secure Boot state.
- `network-security/references/firewall-architecture.md` — isolating the
  management plane that hosts Tang and BMC.
- `cicd-devsecops/SKILL.md` — signing artefacts and protecting build keys.
