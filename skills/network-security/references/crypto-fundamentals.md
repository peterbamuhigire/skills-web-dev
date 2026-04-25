# Crypto Fundamentals — 2026 Quick Reference

Practical cryptographic primitive selection for application and infrastructure
engineers. No math — just what to use, what to avoid, and why.

## Purpose

Distilled guidance on which cryptographic primitives to use in 2026 and which
to never touch again. Covers symmetric, asymmetric, hashes, MACs, KDFs, key
exchange, and randomness.

## Symmetric encryption

Use AEAD (Authenticated Encryption with Associated Data). AEAD combines
confidentiality and integrity in one primitive — you cannot accidentally
forget the MAC and get the old "encrypt-then-not-authenticate" disaster.

| Algorithm | Key size | Nonce/IV | Status 2026 |
| --- | --- | --- | --- |
| AES-256-GCM | 256 bit | 96 bit, unique per key | Default |
| AES-128-GCM | 128 bit | 96 bit, unique per key | Default (faster) |
| ChaCha20-Poly1305 | 256 bit | 96 bit, unique per key | Default on mobile/software |
| XChaCha20-Poly1305 | 256 bit | 192 bit, random safe | Prefer when random nonces |
| AES-256-GCM-SIV | 256 bit | 96 bit, misuse-resistant | Use if nonce reuse is plausible |

Nonce rules for GCM:

- Never reuse a (key, nonce) pair. Doing so with GCM catastrophically leaks
  plaintext and forges MACs.
- Prefer a 96-bit counter that resets only when you rotate the key.
- If you cannot guarantee uniqueness (distributed workers, replays), use
  AES-GCM-SIV or XChaCha20-Poly1305 with random nonces.

Do NOT use in 2026:

- DES, 3DES — broken, removed from modern libraries.
- RC4 — biased, broken in TLS (RFC 7465).
- Blowfish — 64-bit block (SWEET32), too small for modern data volumes.
- AES-ECB — leaks plaintext structure (the famous penguin image).
- AES-CBC without an authenticated MAC — padding oracle attacks.
- "MAC-then-encrypt" or "encrypt-then-MAC" hand-rolled constructions. Use
  AEAD instead.

## Asymmetric encryption and signatures

| Algorithm | Purpose | Key size | Status |
| --- | --- | --- | --- |
| RSA-2048 | Legacy encryption, signing | 2048 bit | Minimum acceptable |
| RSA-3072 | Signing, key wrap | 3072 bit | Recommended where RSA is needed |
| RSA-4096 | Paranoid | 4096 bit | Slow, rarely necessary |
| Ed25519 | Signatures | 256 bit | Default for new work |
| Ed448 | Signatures, higher margin | 448 bit | Niche |
| X25519 | Key exchange (ECDHE) | 256 bit | Default for new work |
| ECDSA P-256 | Signatures (TLS cert) | 256 bit | Fine, needed for some CAs |
| ECDSA P-384 | Signatures (gov) | 384 bit | Fine, required by some compliance |

Ed25519 is faster, has a simpler API, and is immune to the bad-random-number
catastrophes that have broken ECDSA in practice (Sony PS3, many Bitcoin keys).
Use it for SSH keys, JWT signing, code signing, anything new.

Do NOT use:

- RSA-512, RSA-768, RSA-1024 — all factorable by well-funded attackers.
- DSA — weak, obsolete, same bad-random trap as old ECDSA.
- MD5 or SHA-1 signatures — collisions are practical.
- Textbook RSA (no padding, no OAEP) — trivially broken.
- RSA PKCS#1 v1.5 encryption (not signatures) — Bleichenbacher oracle.
  Use RSA-OAEP for encryption, or avoid RSA encryption entirely (use ECIES or
  hybrid KEM + AEAD).

## Hash functions

| Algorithm | Output | Status | Use |
| --- | --- | --- | --- |
| SHA-256 | 256 bit | Default | HMAC, signing, fingerprints, file integrity |
| SHA-384 | 384 bit | Default | When matching P-384 curves |
| SHA-512 | 512 bit | Default | Faster on 64-bit CPUs than SHA-256 |
| SHA-3 (Keccak) | 224-512 bit | Alternative to SHA-2 | When you want a different design family |
| BLAKE2b / BLAKE2s | 256-512 bit | Default for speed | When speed matters and you control both ends |
| BLAKE3 | 256 bit | Fastest | Non-security speed uses, streaming, merkle trees |

Do NOT use for any security purpose:

- MD5 — collisions since 2004, preimages weakened.
- SHA-1 — collisions demonstrated (Google SHAttered 2017). Removed from
  browser cert chains.
- RIPEMD-160 — legacy, weak by modern standards.

MD5 and SHA-1 are still acceptable for non-security checksums (cache keys,
ETags, deduplication where collision is not an attack) but avoid them even
there to prevent confusion.

## Message Authentication Codes (MACs)

| Primitive | Based on | Use |
| --- | --- | --- |
| HMAC-SHA256 | SHA-256 | Default MAC for new work |
| HMAC-SHA512 | SHA-512 | Default on 64-bit workloads |
| Poly1305 | One-time polynomial | Inside ChaCha20-Poly1305 — do not use standalone |
| KMAC | SHA-3 | When using SHA-3 family |
| GMAC | AES | Inside AES-GCM — do not use standalone |

Always use a MAC to authenticate ciphertext if your chosen symmetric primitive
is not AEAD (but you should be using AEAD).

Do NOT use:

- CBC-MAC on variable-length messages (length extension attack).
- Hand-rolled "hash(key || message)" constructions (length extension against
  Merkle-Damgård hashes like SHA-256). Use HMAC.
- CRC32 / Adler32 as authentication. They are error-detection codes, not
  cryptographic MACs.

## Key derivation functions (KDFs)

Two very different categories — do not confuse them.

### Deriving keys from shared secrets or master keys

| KDF | Use case |
| --- | --- |
| HKDF-SHA256 | Derive sub-keys from a TLS handshake secret, master key, or output of a KEM |
| HKDF-SHA512 | Same, 64-bit hot path |

HKDF is cheap and deterministic. Example: TLS 1.3 uses HKDF to derive
handshake keys, application keys, and exporter secrets all from one master
secret.

### Hashing passwords

These are DELIBERATELY slow and memory-hard, to resist GPU and ASIC attacks.

| Algorithm | Status | Notes |
| --- | --- | --- |
| Argon2id | Default (winner of PHC) | Tune: t=3, m=64MB, p=4 for login servers |
| scrypt | Acceptable | Use if Argon2 is not available |
| bcrypt | Acceptable legacy | cost >= 12 in 2026 |
| PBKDF2-HMAC-SHA256 | Last resort | >= 600k iterations (OWASP 2023 baseline). Not memory-hard, GPU-friendly — avoid for new work |

Do NOT use for passwords:

- `md5($password)`
- `sha1($password)`
- `sha256($password)` (without a slow KDF)
- Unsalted hashes
- Home-made "pepper + hash + salt" constructions

## Key exchange

| Algorithm | Use |
| --- | --- |
| ECDHE with X25519 | Default for TLS 1.3, SSH, Signal, WireGuard |
| ECDHE with P-256 / P-384 | When compliance requires NIST curves |
| ML-KEM-768 (Kyber) | Post-quantum KEM, 2026 hybrid rollout |
| X25519+ML-KEM-768 hybrid | Safest current choice — classical + PQ in parallel |

Plain (static, non-ephemeral) DH is dead. Everything uses Ephemeral DH so a
stolen long-term key does not retroactively decrypt old sessions — this is
Perfect Forward Secrecy and it is non-negotiable.

Post-quantum state in 2026: major browsers, Cloudflare, Google and AWS have
rolled out X25519+ML-KEM-768 hybrid key exchange in TLS 1.3. Enable it where
your TLS stack supports it (nginx via BoringSSL builds, recent OpenSSL). Do
not ship pure PQ yet — hybrids give you classical-security as a fallback.

Do NOT use:

- Static DH without ephemerality.
- RSA key transport (TLS 1.2 and earlier) — no forward secrecy. Disabled in
  TLS 1.3.
- Small DH groups (<2048 bit) — Logjam attack.

## 2026 recommendations table

| Job | Use | Avoid |
| --- | --- | --- |
| Encrypt data at rest | AES-256-GCM or ChaCha20-Poly1305 | AES-CBC, AES-ECB, 3DES |
| Encrypt API tokens in DB | AES-256-GCM with envelope encryption (KMS) | Reversible XOR, ECB |
| Sign a JWT | EdDSA (Ed25519) or RS256 / ES256 if required | HS256 with short secret, none |
| Hash a file | SHA-256 or BLAKE3 | MD5, SHA-1 |
| Hash a password | Argon2id | SHA-256, MD5, PBKDF2 with few iters |
| TLS key exchange | X25519 (+ ML-KEM hybrid) | Static DH, RSA key transport |
| SSH host/user key | Ed25519 | DSA, ssh-rsa (SHA-1) |
| VPN | WireGuard (ChaCha20-Poly1305 + X25519) | PPTP, L2TP bare |

## Random numbers

Cryptographic RNG must come from the OS, not from `rand()`.

Linux:

- `getrandom(2)` syscall — blocks until pool seeded, non-blocking after.
- `/dev/urandom` — equivalent to getrandom after early boot. Use this.
- `/dev/random` — do not use; it blocks unnecessarily on modern kernels.

Language-specific:

| Language | Use | Avoid |
| --- | --- | --- |
| PHP | `random_bytes()`, `random_int()` | `rand()`, `mt_rand()`, `uniqid()` |
| Python | `secrets.token_bytes()`, `secrets.token_hex()` | `random.*` module |
| Node.js | `crypto.randomBytes()`, `crypto.randomUUID()` | `Math.random()` |
| Go | `crypto/rand` | `math/rand` |
| Java | `SecureRandom` | `Random`, `Math.random()` |
| Rust | `rand::rngs::OsRng` | `rand::thread_rng()` for crypto |
| Kotlin (JVM) | `SecureRandom` | `Random`, `kotlin.random` |
| Swift | `SecRandomCopyBytes` | `arc4random` (OK on Apple, but prefer the Sec API for clarity) |

Session IDs, CSRF tokens, password reset tokens, API keys, nonces, salts — all
MUST come from the crypto RNG. A predictable session ID is an account
takeover.

## Common crypto anti-patterns

- Rolling your own crypto. You will get it wrong. Use libsodium, OpenSSL,
  Web Crypto, Go `crypto/*`, or the equivalent in your language. Review-grade
  libraries exist — use them.
- Copy-pasting crypto code from Stack Overflow. The top answer is often 10
  years out of date and uses ECB mode.
- Hardcoded keys or IVs in source code. Every key leaks the day the repo goes
  public or an employee leaves.
- Reusing nonces with GCM. Catastrophic.
- Using the same key for signing and encryption.
- Using a password as a raw AES key. Run it through Argon2id or HKDF first.
- Truncating MACs aggressively (e.g. "first 32 bits of HMAC"). Reduces
  security.
- Trusting client-computed HMACs without a server-side secret.
- Storing private keys in the database next to the data they protect. Use
  a KMS, or at least encrypt them with a separate master key held elsewhere.
- "We'll add encryption later." You will not.
- "It's inside our VPC so we don't need to encrypt it." Defense in depth —
  the VPC is not a trust boundary against insiders or a compromised peer.

## Cross-references

- `references/tls-pki.md` for cipher suites in practice
- `references/vpn.md` for WireGuard's fixed crypto suite rationale
- `php-security` skill for `random_bytes()` and `password_hash()` usage
- `vibe-security-skill` for the broader secure coding baseline
- `llm-security` skill for AI-specific trust-boundary concerns
