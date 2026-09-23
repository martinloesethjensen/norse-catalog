"""generate.py → validate → site/v1 (content-hashed files + manifest).

Idempotent: unchanged content leaves site/ byte-for-byte untouched, which is
what lets CI re-run the build and fail on any diff. manifest.json is written
last, so an interrupted build never points at files that don't exist.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from catalog.validate import MAX_FILE_BYTES, validate

SCHEMA_VERSION = 1
KEEP_VERSIONS = 3
REPO = Path(__file__).resolve().parent.parent
HASHED_FILE = re.compile(r"^(taxonomy|recipes)\.[0-9a-f]{8}\.json$")


class BuildError(Exception):
    pass


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_json(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


def publish(taxonomy_bytes: bytes, recipes_bytes: bytes, site_v1: Path, now: datetime) -> bool:
    for name, data in (("taxonomy", taxonomy_bytes), ("recipes", recipes_bytes)):
        if len(data) > MAX_FILE_BYTES:
            raise BuildError(f"{name}.json is {len(data)} bytes; the limit is {MAX_FILE_BYTES}")
    try:
        taxonomy = json.loads(taxonomy_bytes)
        recipes = json.loads(recipes_bytes)
    except ValueError as exc:
        raise BuildError(f"catalog is not valid JSON: {exc}") from exc
    errors = validate(taxonomy, recipes)
    if errors:
        raise BuildError("validation failed:\n" + "\n".join(errors))

    tax_sha, rec_sha = _sha256(taxonomy_bytes), _sha256(recipes_bytes)
    content_version = _sha256((tax_sha + rec_sha).encode("ascii"))[:8]

    # Check manifest.json (source of truth) instead of history.json.
    # If a build is interrupted between writing history.json and manifest.json,
    # manifest.json remains the authoritative record of what's actually published.
    manifest_path = site_v1 / "manifest.json"
    if manifest_path.exists():
        existing_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if existing_manifest["contentVersion"] == content_version:
            return False

    manifest = {
        "schemaVersion": SCHEMA_VERSION,
        "contentVersion": content_version,
        "generatedAt": now.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "taxonomy": {"path": f"taxonomy.{tax_sha[:8]}.json", "sha256": tax_sha, "bytes": len(taxonomy_bytes)},
        "recipes": {"path": f"recipes.{rec_sha[:8]}.json", "sha256": rec_sha, "bytes": len(recipes_bytes)},
    }

    site_v1.mkdir(parents=True, exist_ok=True)
    (site_v1 / manifest["taxonomy"]["path"]).write_bytes(taxonomy_bytes)
    (site_v1 / manifest["recipes"]["path"]).write_bytes(recipes_bytes)

    # Load and deduplicate history before prepending new manifest.
    # This ensures interrupted builds don't create duplicate entries.
    history_path = site_v1 / "history.json"
    history = json.loads(history_path.read_text(encoding="utf-8")) if history_path.exists() else []
    history = [m for m in history if m["contentVersion"] != content_version]
    history = [manifest] + history[: KEEP_VERSIONS - 1]
    keep = {m[k]["path"] for m in history for k in ("taxonomy", "recipes")}
    for path in site_v1.iterdir():
        if HASHED_FILE.match(path.name) and path.name not in keep:
            path.unlink()

    _write_json(history_path, history)
    _write_json(site_v1 / "manifest.json", manifest)
    return True


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run([sys.executable, str(REPO / "generate.py"), tmp], check=True)
        taxonomy_bytes = (Path(tmp) / "taxonomy.json").read_bytes()
        recipes_bytes = (Path(tmp) / "recipes.json").read_bytes()
    try:
        changed = publish(taxonomy_bytes, recipes_bytes, REPO / "site" / "v1", datetime.now(timezone.utc))
    except BuildError as exc:
        print(exc, file=sys.stderr)
        return 1
    print("Published a new catalog version." if changed else "Catalog unchanged; site/ untouched.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
