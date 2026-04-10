# Users, Groups and Sudo Hardening

Reference for managing user accounts, groups, and privilege escalation on
Debian 12 / Ubuntu 24.04 SaaS servers. Focuses on least privilege and auditability.

## 1. User and group model

Every Linux account has a numeric UID and primary GID stored in `/etc/passwd`
and `/etc/group`. The kernel only cares about the numbers; usernames are a
convenience for humans.

Account categories:

| Range             | Purpose                                      |
|-------------------|----------------------------------------------|
| `0`               | `root` — the superuser. Always UID 0.        |
| `1` to `999`      | System/service accounts (nginx, postgres)    |
| `1000` to `59999` | Regular human users created by `adduser`     |
| `65534`           | `nobody` — unprivileged fallback identity    |

Rules of thumb for a multi-tenant SaaS host:

- Never give human users UIDs inside the system range.
- Every daemon runs as its own dedicated system user, never as `root`.
- Never reuse a UID that once belonged to a deleted account.
- The `nobody` account exists to own files that nothing should touch; do not
  log in as `nobody`, and do not run services as `nobody` (give them their
  own user instead).

```bash
# Inspect the account database
getent passwd | awk -F: '{printf "%-20s UID=%s GID=%s shell=%s\n",$1,$3,$4,$7}'
getent group  | awk -F: '{printf "%-20s GID=%s members=%s\n",$1,$3,$4}'
```

## 2. Creating users securely

On Debian and Ubuntu prefer `adduser` (a Perl wrapper) over raw `useradd`.
`adduser` reads `/etc/adduser.conf`, creates the home directory with
correct permissions, copies skeleton files from `/etc/skel`, and prompts
for the password interactively.

```bash
# Create a regular admin account
sudo adduser --shell /bin/bash --gecos "Jane Doe,,," jdoe

# Create a service account — no login shell, no home
sudo adduser --system --group --no-create-home --shell /usr/sbin/nologin myapp
```

Defaults worth knowing in `/etc/login.defs`:

```text
UMASK           027
PASS_MAX_DAYS   90
PASS_MIN_DAYS   1
PASS_WARN_AGE   7
ENCRYPT_METHOD  YESCRYPT    # Debian 12 default; strong
SHA_CRYPT_MIN_ROUNDS 10000
```

For bulk scripting use `useradd` directly:

```bash
sudo useradd -m -s /bin/bash -G sudo,adm -c "Backup Operator" backupadm
sudo passwd backupadm   # or: sudo chpasswd < creds.txt
```

## 3. Disabling the root account

A shared `root` login is an audit nightmare: every action attributed to
`root` could have been anyone who knows the password. Best practice on
Debian/Ubuntu is to disable direct root login and route all privilege
through named sudo users.

```bash
# Lock the password hash so password login as root is refused
sudo passwd -l root

# Disable the login shell entirely (belt and braces)
sudo usermod -s /usr/sbin/nologin root

# Confirm
sudo grep '^root:' /etc/shadow    # hash field starts with '!' or '*'
```

Notes:

- Ubuntu cloud images already ship with root locked.
- SSH root login must also be blocked: `PermitRootLogin no` in
  `/etc/ssh/sshd_config`.
- Recovery console still works because `systemd` `rescue.target` uses `sulogin`
  which accepts root's *hashed* password via the `--force` path; document the
  DR procedure and store the recovery credentials in a vault.

## 4. Sudo hardening

### 4.1 Always edit with visudo

`visudo` validates syntax before saving. A broken `/etc/sudoers` can lock
every admin out of the box.

```bash
sudo visudo                              # edits /etc/sudoers
sudo visudo -f /etc/sudoers.d/90-ops     # edits a drop-in file
sudo visudo -c                           # check all sudoers files
```

### 4.2 Per-user and per-group rules

```text
# /etc/sudoers.d/10-admins  (mode 0440, owned by root)
User_Alias   OPS = jdoe, asmith
Host_Alias   SAAS = web01, web02, db01
Cmnd_Alias   RESTART_APP = /bin/systemctl restart myapp, \
                            /bin/systemctl status  myapp

OPS        SAAS = (root) RESTART_APP
%sudo      ALL  = (ALL:ALL) ALL
```

### 4.3 Defaults worth setting

```text
Defaults  env_reset
Defaults  mail_badpass
Defaults  secure_path="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
Defaults  timestamp_timeout=5        # re-prompt for password every 5 minutes
Defaults  passwd_tries=3
Defaults  use_pty                    # run commands under a pty (required for logging)
Defaults  log_input, log_output      # session recording in /var/log/sudo-io
Defaults  iolog_dir="/var/log/sudo-io/%{user}"
Defaults  logfile="/var/log/sudo.log"
Defaults  !visiblepw
Defaults  requiretty                 # block non-interactive sudo
```

`secure_path` prevents a malicious user from prepending a directory with a
trojan `passwd` binary. `timestamp_timeout=0` forces a password on *every*
sudo invocation (high-security hosts only).

### 4.4 Drop-in files

Any file under `/etc/sudoers.d/` is included automatically, but it must:

- Contain no tilde (`~`) or dot in the filename.
- Be owned by `root:root`.
- Have mode `0440`.

```bash
sudo install -m 0440 -o root -g root ./90-deploy /etc/sudoers.d/90-deploy
sudo visudo -c   # verify
```

### 4.5 Checking privileges

```bash
sudo -l              # list what the current user may run
sudo -l -U jdoe      # (as root) list what jdoe may run
```

## 5. Least-privilege sudo

Do not use `ALL=(ALL) ALL` for service or automation accounts. Grant the
exact command with full absolute paths.

```text
# /etc/sudoers.d/50-backup
Cmnd_Alias BACKUP = /usr/local/sbin/backup-db.sh, \
                    /usr/local/sbin/backup-uploads.sh

backupadm  ALL = (root) NOPASSWD: BACKUP
```

Rules:

- Always use absolute paths. Relative paths are rejected.
- `NOPASSWD` is only acceptable when the command list is tightly scoped and
  the script itself has no user-controlled arguments.
- Never allow editors, pagers, or shells via sudo (`vi`, `less`, `bash`) —
  they all offer a shell escape.
- Use wildcards with care. `/bin/systemctl restart *` lets the user restart
  `ssh`, which terminates sessions.

## 6. Sudo session logging

With `use_pty` plus `log_input`/`log_output`, sudo records every keystroke
and every byte of terminal output per session.

```bash
sudo mkdir -p /var/log/sudo-io
sudo chmod 700 /var/log/sudo-io
sudo ls /var/log/sudo-io/           # one dir per user, per session
sudo sudoreplay -l                  # list sessions
sudo sudoreplay jdoe/00/00/01       # replay a session in real time
```

Ship `/var/log/sudo-io/` and `/var/log/sudo.log` to the central log host
immediately — a local attacker can delete them after privilege escalation.

## 7. Auditing existing accounts

```bash
# List all accounts with their shells and UIDs
awk -F: '{printf "%-20s UID=%-5s shell=%s\n",$1,$3,$7}' /etc/passwd

# Accounts with a real login shell
getent passwd | awk -F: '$7 ~ /\/(ba|z|da)?sh$/ {print $1, $7}'

# Members of the sudo group (principal privilege group on Debian)
getent group sudo

# Recent logins
lastlog | awk 'NR==1 || $2!="**Never"'

# Failed logins (install bsdutils if missing)
sudo lastb | head -40

# Audit failure counts (with faillock)
sudo faillock --user jdoe
```

Detect dormant accounts (no login in 90 days):

```bash
lastlog -b 90 | awk 'NR>1 && $0 !~ /Never/ {print $1}'
```

## 8. Locking, unlocking and expiring accounts

```bash
# Temporarily disable a user (password hash replaced with '!')
sudo usermod -L jdoe
sudo passwd  -l jdoe

# Unlock
sudo usermod -U jdoe

# Hard expire on a specific date (YYYY-MM-DD)
sudo chage -E 2026-12-31 contractor1

# Remove the expiry
sudo chage -E -1 contractor1

# Show current status
sudo chage -l jdoe
```

A locked account cannot log in by password, but SSH key login still works
unless you also:

```bash
sudo usermod -s /usr/sbin/nologin jdoe
sudo mv /home/jdoe/.ssh/authorized_keys{,.disabled}
```

## 9. Password aging policy

Force every human account to rotate, age, and warn consistently:

```bash
sudo chage -M 90 -m 7 -W 7 -I 14 jdoe
# -M 90 : max age 90 days
# -m 7  : min 7 days before next change (stops churn-to-reuse)
# -W 7  : warn 7 days before expiry
# -I 14 : lock 14 days after expiry
```

Set the defaults once in `/etc/login.defs` so new accounts inherit them:

```text
PASS_MAX_DAYS   90
PASS_MIN_DAYS   7
PASS_WARN_AGE   7
```

## 10. Disabling unused system accounts

System accounts such as `games`, `lp`, `news`, `uucp`, `gnats`, `irc` are
usually pointless on a server. Give them a nologin shell so they cannot be
used as a pivot:

```bash
for u in games lp news uucp irc gnats list; do
  sudo usermod -s /usr/sbin/nologin "$u" 2>/dev/null || true
done

# Verify nobody has a login shell they don't need
awk -F: '$7 ~ /sh$/ && $3<1000 {print}' /etc/passwd
```

## 11. UID 0 check

Exactly one account must have UID 0: `root`. Anything else is a backdoor.

```bash
awk -F: '$3==0 {print}' /etc/passwd
# expected output:
# root:x:0:0:root:/root:/usr/sbin/nologin
```

Add this check to a nightly audit job and alert on any extra line.

## 12. Anti-patterns

- **Shared accounts.** Every admin must have a named account. No
  "ops" or "support" accounts used by more than one person.
- **Editing `/etc/sudoers` directly.** Always use `visudo` — typos lock you out.
- **`NOPASSWD: ALL`** — turns sudo into a root backdoor, defeats the whole point.
- **World-writable `sudoers.d` file.** `chmod 440` is the only acceptable mode.
- **Allowing shell/editor via sudo.** `sudo vi /etc/hosts` gives a root shell
  through `:shell`. Use `sudoedit` instead.
- **Leaving `PermitRootLogin yes` in sshd_config** after disabling root.
- **No sudo logging.** You cannot prove least privilege without an audit trail.
- **Reusing UIDs.** File ownership is tracked by UID; reusing gives the new
  account silent access to the old account's files.

## Cross-references

- `references/pam-authentication.md` — account lockout, password quality, MFA
- `references/file-permissions-acls.md` — home directory and dotfile perms
- `references/selinux-apparmor.md` — sudo interaction with MAC profiles
- `references/ssh-hardening.md` — SSH key management and `PermitRootLogin`
- `cicd-jenkins-debian` skill — agent accounts and sudo-less deploy users
- `mysql-administration` skill — MySQL accounts mapped to Linux users
