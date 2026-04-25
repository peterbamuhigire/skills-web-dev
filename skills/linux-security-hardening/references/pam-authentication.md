# PAM Authentication and Account Policy

Reference for configuring Pluggable Authentication Modules (PAM) on
Debian 12 / Ubuntu 24.04 to enforce password quality, lockout, and MFA.

## 1. What PAM is

PAM (Pluggable Authentication Modules) is the abstraction layer between
applications that need to authenticate (login, sshd, sudo, cron, su) and
the actual authentication backends (local `/etc/shadow`, LDAP, Kerberos,
TOTP, biometric readers). An application calls the PAM API; PAM reads a
per-service config file and runs the modules it lists in order.

This means policies only have to be written once: tighten password quality
in the common file and every login path picks it up.

## 2. Config layout on Debian

```text
/etc/pam.d/
  common-auth       # shared auth stack (pulled in via @include)
  common-account
  common-password
  common-session
  common-session-noninteractive
  sshd              # SSH daemon
  sudo              # sudo command
  login             # virtual console login
  su                # su command
  cron              # cron jobs
```

Every service file normally pulls in the `common-*` files, so you edit one
place and every service inherits. Debian ships a helper, `pam-auth-update`,
that manages these common files idempotently from profile fragments in
`/usr/share/pam-configs/`. Hand-editing the common files still works, but
`pam-auth-update` will overwrite your changes the next time a PAM package
upgrades — prefer a profile file when shipping to production.

## 3. PAM stack types and control flags

Each PAM line is of the form:

```text
<type>   <control>   <module>  [arguments]
```

**Types** (categories of checks run in separate stacks):

| Type       | Purpose                                                      |
|------------|--------------------------------------------------------------|
| `auth`     | Identify and authenticate the user (passwords, keys, TOTP).  |
| `account`  | Check account validity (expiry, time of day, host policy).   |
| `password` | Change credentials (quality checks go here).                 |
| `session`  | Set up and tear down the session (mounts, limits, logging).  |

**Control flags**:

| Flag         | Meaning                                                   |
|--------------|-----------------------------------------------------------|
| `required`   | Must succeed; failure returns error but stack continues. |
| `requisite`  | Must succeed; failure returns immediately.                |
| `sufficient` | Success short-circuits the stack as OK.                   |
| `optional`   | Result does not affect the final outcome.                 |
| `[...]`      | Fine-grained control like `[success=1 default=ignore]`.   |

Ordering matters. A `sufficient pam_unix.so` that returns OK before a
`required pam_faillock.so` would skip the lockout counter, which is a
configuration bug.

## 4. Password quality with pam_pwquality

`libpam-pwquality` provides the quality checker and a config file.

```bash
sudo apt install libpam-pwquality
```

Edit `/etc/security/pwquality.conf`:

```ini
minlen      = 14        # minimum length
minclass    = 3         # at least 3 of: lower, upper, digit, other
dcredit     = -1        # at least 1 digit   (negative = required count)
ucredit     = -1        # at least 1 upper
lcredit     = -1        # at least 1 lower
ocredit     = -1        # at least 1 symbol
maxrepeat   = 3         # no 4 identical chars in a row
maxclassrepeat = 4
gecoscheck  = 1         # reject names from GECOS field
dictcheck   = 1         # use cracklib dictionary
usercheck   = 1         # reject username substrings
enforcing   = 1
retry       = 3
difok       = 5         # at least 5 chars different from old password
```

Then in `/etc/pam.d/common-password`, ensure the pwquality line runs
before `pam_unix.so`:

```text
password  requisite    pam_pwquality.so retry=3
password  [success=1 default=ignore]  pam_unix.so obscure use_authtok yescrypt shadow \
                                              remember=5
password  requisite    pam_deny.so
password  required     pam_permit.so
```

`remember=5` on `pam_unix.so` keeps a history of the last 5 hashes in
`/etc/security/opasswd` so users cannot cycle between two favourites.
`yescrypt` is the strong Debian 12 default hashing algorithm.

## 5. Account lockout with pam_faillock

`pam_faillock` is the modern replacement for `pam_tally2`. It lives in
`libpam-modules` and stores counters under `/run/faillock/`.

`/etc/security/faillock.conf`:

```ini
deny          = 5        # lock after 5 consecutive failures
unlock_time   = 900      # auto-unlock after 15 minutes
fail_interval = 900      # within this window
even_deny_root = no      # don't lock root out of the console
audit         = yes
silent        = no
```

Integration in `/etc/pam.d/common-auth`:

```text
auth   required    pam_faillock.so preauth
auth   [success=1 default=ignore]  pam_unix.so nullok
auth   [default=die]  pam_faillock.so authfail
auth   sufficient  pam_faillock.so authsucc
auth   requisite   pam_deny.so
auth   required    pam_permit.so
```

Ops commands:

```bash
sudo faillock --user jdoe              # show failure count
sudo faillock --user jdoe --reset      # clear
```

## 6. Time-based restrictions with pam_time

Useful for contractor accounts that should only connect during business
hours. Add to `/etc/pam.d/common-account`:

```text
account  requisite  pam_time.so
```

`/etc/security/time.conf`:

```text
# <services>;<ttys>;<users>;<times>
sshd;*;contractor1|contractor2;Wk0800-1800
sshd;*;!ops;Al0600-2300         # everyone except ops: 06-23 daily
```

## 7. Resource limits with pam_limits

`/etc/pam.d/common-session` already includes:

```text
session  required  pam_limits.so
```

Define caps in `/etc/security/limits.conf` or drop-ins under
`/etc/security/limits.d/`:

```text
#<domain>   <type>  <item>     <value>
*           hard    nproc      4096
*           hard    nofile     65536
www-data    soft    nofile     4096
www-data    hard    nofile     16384
@devs       hard    core       0       # disable core dumps for a group
```

This is the right place to block fork-bombs and raise file descriptor
limits for database and web workers.

## 8. pam_wheel: restrict su to admins

By default, any user who knows the root password can `su`. Modern Debian
locks root, but if you re-enable it, restrict `su` to a named group:

```bash
sudo groupadd -f wheel
sudo usermod -aG wheel jdoe
```

`/etc/pam.d/su`:

```text
auth   required   pam_wheel.so use_uid group=wheel
```

Only members of `wheel` may now invoke `su`.

## 9. MFA on SSH with pam_google_authenticator

Add a TOTP second factor to SSH logins. Works with Google Authenticator,
Authy, 1Password, and any other TOTP app.

```bash
sudo apt install libpam-google-authenticator
```

Each user runs the setup tool once to generate a secret and enrol:

```bash
google-authenticator -t -d -f -r 3 -R 30 -W
# -t  time-based, -d no reuse, -f update file,
# -r/-R rate-limit, -W window tightened
```

Append to `/etc/pam.d/sshd` (above the `@include common-auth` line):

```text
auth   required   pam_google_authenticator.so nullok
```

`nullok` lets users who have not yet enrolled still log in — remove it
once everyone is set up.

In `/etc/ssh/sshd_config`:

```text
UsePAM                     yes
ChallengeResponseAuthentication  yes
KbdInteractiveAuthentication     yes
PasswordAuthentication     no
PubkeyAuthentication       yes
AuthenticationMethods      publickey,keyboard-interactive
```

`AuthenticationMethods publickey,keyboard-interactive` requires both an
SSH key *and* the TOTP code. This is the recommended production pattern:
the key proves who you are, the TOTP code proves you are still in
possession of the enrolled device. Apply the same approach to sudo by
adding the PAM line to `/etc/pam.d/sudo`.

```bash
sudo systemctl restart ssh
```

## 10. SSH and PAM interaction

When `UsePAM yes` is set in `sshd_config`, the sshd process runs the PAM
stack in `/etc/pam.d/sshd` for every login. The order of events:

1. TCP connection accepted.
2. Key exchange, host key verification.
3. Client presents a publickey (if `PubkeyAuthentication yes`).
4. sshd runs the PAM `auth` stack — this is where TOTP, faillock, and
   time restrictions run.
5. PAM `account` stack — expired? Locked? Allowed at this hour?
6. PAM `session` stack — apply limits, open PAM-managed mounts, log.
7. Shell or command starts.
8. At logout, PAM `session close` runs.

## 11. Debugging PAM

```bash
# Live authentication log
sudo tail -f /var/log/auth.log

# Enable verbose debug for one service
# Add 'debug' as an argument to the module:
# auth required pam_unix.so debug

# Test PAM stack without logging in
sudo apt install pamtester
sudo pamtester sshd jdoe authenticate
sudo pamtester sudo  jdoe authenticate
```

`pamtester` is invaluable: you can validate a new lockout or MFA config
on a second SSH session before you disconnect the primary.

## 12. Anti-patterns

- **Weak pwquality** (`minlen=8`, no class requirement). Modern attackers
  crack 8-char passwords in minutes.
- **No lockout.** Without `pam_faillock` the box is open to password spray.
- **MFA on SSH but not on sudo.** An attacker with a stolen key can still
  get root. Apply `pam_google_authenticator` to `/etc/pam.d/sudo` too.
- **`nullok` left in production.** Lets unenrolled users skip MFA forever.
- **Editing `/etc/pam.d/common-*` without `pam-auth-update`.** Upgrades
  may revert your changes silently.
- **Disabling PAM "temporarily"** in sshd during an incident. Never do
  this — you lose lockout, MFA, and every log record at once.
- **`pam_tally2`** on modern systems. Replace with `pam_faillock`.
- **Using the same PAM file for kiosk and admin** — restrict by service.

## Cross-references

- `references/users-groups-sudo.md` — account creation, locking, expiry
- `references/ssh-hardening.md` — full sshd_config and key management
- `references/selinux-apparmor.md` — AppArmor profile on `sshd`
- `network-security` skill — SSH fronted by a bastion and firewall rules
- `cicd-jenkins-debian` skill — Jenkins agent accounts and PAM constraints
