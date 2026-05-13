# Evidence Pack Format

The pack is the auditor's primary artefact. This document is the canonical spec.

---

## 1. File Layout

```
evp-{control_id}-{window_start}-{window_end}-{run_id}.tar.gz
├── manifest.json                       # canonical metadata + sha256s
├── manifest.signature                  # detached HSM signature over manifest.json
├── public-key.pem                      # platform verification public key
├── README.md                           # human-readable summary + verify steps
├── verify.py                           # auditor-runnable verification script
└── artefacts/
    ├── {artefact-1}.{ext}
    ├── {artefact-2}.{ext}
    └── ...
```

Pack ids are `{control_id}-{window}-{run_id}` where `run_id` is a ULID. A control may have multiple packs over the same window (e.g., monthly + ad-hoc); each gets a unique pack id.

## 2. Manifest Schema

```json
{
  "$schema": "https://compliance.example.com/schemas/evidence-pack-manifest.schema.json",
  "pack_id": "evp-CC7.2-2026-04-27-2026-05-04-01HXYZ",
  "control_id": "CC7.2",
  "control_framework": "SOC2",
  "control_name": "Agent runtime monitoring and anomaly response",
  "window_start": "2026-04-27T00:00:00Z",
  "window_end":   "2026-05-04T00:00:00Z",
  "produced_at":  "2026-05-04T02:00:14Z",
  "produced_by":  "scheduler-prod-eu-west-1",
  "collector_version": "1.4.2",
  "owner":  "sre-lead@example.com",
  "retention_class": "soc2_iso_7y",
  "retention_until": "2033-05-04T00:00:00Z",
  "artefacts": [
    {
      "path": "artefacts/task_volume_by_state.json",
      "sha256": "5e8b...",
      "size_bytes": 12834,
      "description": "Agent task volume counted by state (PLANNING/ACTING/.../COMPLETED)"
    },
    {
      "path": "artefacts/slo_burn_rates.jsonl",
      "sha256": "a1c2...",
      "size_bytes": 90211,
      "description": "Per-day SLO burn rates for hallucination/refusal/abstain"
    },
    ...
  ],
  "related_packs": [
    "evp-CC7.2-2026-04-20-2026-04-27-01HXYW"
  ],
  "signing_key_id": "evidence-pack-key-2026",
  "platform_pub_key_fingerprint": "SHA256:abc...",
  "schema_version": "1.0"
}
```

## 3. Signature

```python
# compliance/evidence_pack.py
import hashlib, json, tarfile, io
from pathlib import Path

class EvidencePack:
    def __init__(self, control_id, control_framework, window, owner, **meta):
        self.control_id = control_id
        self.control_framework = control_framework
        self.window_start, self.window_end = window
        self.owner = owner
        self.meta = meta
        self.artefacts = {}  # path -> bytes
        self.pack_id = f"evp-{control_id}-{self.window_start.date()}-{self.window_end.date()}-{ulid()}"

    def add(self, path: str, content):
        if isinstance(content, (dict, list)):
            content = json.dumps(content, indent=2, default=str).encode()
        elif isinstance(content, str):
            content = content.encode()
        elif isinstance(content, bytes):
            pass
        else:
            content = json.dumps(content, default=str).encode()
        self.artefacts[f"artefacts/{path}"] = content

    def _manifest(self) -> dict:
        return {
            "pack_id": self.pack_id,
            "control_id": self.control_id,
            "control_framework": self.control_framework,
            "control_name": self.meta.get("control_name"),
            "window_start": self.window_start.isoformat() + "Z",
            "window_end":   self.window_end.isoformat() + "Z",
            "produced_at":  datetime.utcnow().isoformat() + "Z",
            "produced_by":  HOSTNAME,
            "collector_version": COLLECTOR_VERSION,
            "owner": self.owner,
            "retention_class": self.meta.get("retention_class", "soc2_baseline_3y"),
            "retention_until": compute_retention_until(
                self.window_end, self.meta.get("retention_class", "soc2_baseline_3y")
            ).isoformat() + "Z",
            "artefacts": [
                {
                    "path": p,
                    "sha256": hashlib.sha256(c).hexdigest(),
                    "size_bytes": len(c),
                    "description": self.meta.get("descriptions", {}).get(p, ""),
                }
                for p, c in sorted(self.artefacts.items())
            ],
            "signing_key_id": "evidence-pack-key-2026",
            "platform_pub_key_fingerprint": HSM.pubkey_fingerprint("evidence-pack-key-2026"),
            "schema_version": "1.0",
        }

    def sign_and_upload(self) -> str:
        manifest = self._manifest()
        manifest_bytes = json.dumps(manifest, sort_keys=True, indent=2).encode()
        manifest_sig = HSM.sign("evidence-pack-key-2026",
                                  hashlib.sha256(manifest_bytes).digest())

        buf = io.BytesIO()
        with tarfile.open(fileobj=buf, mode="w:gz") as tf:
            _add(tf, "manifest.json", manifest_bytes)
            _add(tf, "manifest.signature", manifest_sig)
            _add(tf, "public-key.pem", HSM.pubkey_pem("evidence-pack-key-2026"))
            _add(tf, "README.md", _render_readme(manifest))
            _add(tf, "verify.py", _verify_script_template())
            for path, content in self.artefacts.items():
                _add(tf, path, content)

        pack_bytes = buf.getvalue()
        vault_key = f"packs/{self.control_framework}/{self.control_id}/{self.pack_id}.tar.gz"
        url = EvidenceVault.put(
            key=vault_key,
            body=pack_bytes,
            retention_until=manifest["retention_until"],
            content_type="application/gzip",
        )
        AuditorPortalIndex.register(self.pack_id, manifest, url)
        return url

def _add(tf, name, content):
    info = tarfile.TarInfo(name=name)
    info.size = len(content)
    info.mtime = 0  # deterministic
    info.mode = 0o644
    tf.addfile(info, io.BytesIO(content))
```

## 4. Auditor Verification Script

`verify.py` shipped in every pack:

```python
#!/usr/bin/env python3
"""Verify this evidence pack offline.

No network calls; no production access; uses only files in this pack.
"""
import json, hashlib, sys
from pathlib import Path

def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def verify():
    base = Path(__file__).parent
    manifest = json.loads((base / "manifest.json").read_bytes())
    manifest_bytes = (base / "manifest.json").read_bytes()
    sig = (base / "manifest.signature").read_bytes()
    pub_pem = (base / "public-key.pem").read_bytes()

    # 1. Verify manifest signature against included public key
    if not verify_signature(pub_pem, hashlib.sha256(manifest_bytes).digest(), sig):
        print("FAIL: manifest signature invalid"); sys.exit(2)

    # 2. Verify each artefact sha256
    for a in manifest["artefacts"]:
        p = base / a["path"]
        if not p.exists():
            print(f"FAIL: missing {a['path']}"); sys.exit(2)
        if sha256_file(p) != a["sha256"]:
            print(f"FAIL: sha256 mismatch {a['path']}"); sys.exit(2)
        if p.stat().st_size != a["size_bytes"]:
            print(f"FAIL: size mismatch {a['path']}"); sys.exit(2)

    print(f"OK: pack {manifest['pack_id']} verified.")
    print(f"     control: {manifest['control_id']} ({manifest['control_framework']})")
    print(f"     window:  {manifest['window_start']} to {manifest['window_end']}")
    print(f"     artefacts: {len(manifest['artefacts'])}")

def verify_signature(pub_pem: bytes, payload: bytes, signature: bytes) -> bool:
    # Implementation depends on the signing algorithm (Ed25519, ECDSA P-256, etc.)
    from cryptography.hazmat.primitives.serialization import load_pem_public_key
    from cryptography.hazmat.primitives.asymmetric import ed25519
    key = load_pem_public_key(pub_pem)
    try:
        key.verify(signature, payload)
        return True
    except Exception:
        return False

if __name__ == "__main__":
    verify()
```

## 5. README Template

```markdown
# Evidence Pack — {control_id}

**Framework:** {control_framework}
**Control:** {control_name}
**Window:** {window_start} – {window_end}
**Produced:** {produced_at}
**Owner:** {owner}
**Pack ID:** {pack_id}
**Retention until:** {retention_until}

## Contents

{artefact_table}

## Verify

```sh
python3 verify.py
```

Expected output: `OK: pack {pack_id} verified.`

## Provenance

Pack signed by platform evidence key (id `{signing_key_id}`). Public key embedded in `public-key.pem`. Fingerprint `{pub_key_fingerprint}` matches the platform's published key registry at https://trust.example.com/keys.

## Questions

Contact: {owner}, fallback: compliance@example.com.
```

## 6. Pack Immutability

Once `sign_and_upload` returns, the pack is final:

- Object-lock retention prevents deletion until `retention_until`.
- The pack id is content-addressed (manifest signature commits to all sha256s).
- A subsequent run produces a new pack id; the old pack is preserved.

The compliance console shows pack history (all runs of a control × window) so the auditor can see which pack is current and which are historical.

## 7. Pack-of-Packs (Attestation Pack)

For annual attestation, an outer pack collects references to constituent packs:

```json
{
  "pack_id": "evp-attestation-2026-SOC2T2-01HXYZ",
  "control_framework": "SOC2",
  "audit_window": ["2025-06-01", "2026-05-31"],
  "constituent_packs": [
    {"pack_id": "evp-CC7.2-2026-04-27-2026-05-04-...", "sha256": "..."},
    {"pack_id": "evp-PI1.1-2026-04-01-2026-04-30-...", "sha256": "..."},
    ...
  ]
}
```

The attestation pack does not duplicate contents; it references and signs the manifest sha256s. Auditor pulls the referenced packs individually.
