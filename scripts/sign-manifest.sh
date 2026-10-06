#!/usr/bin/env bash
# Signs site/v1/manifest.json with the catalog's Ed25519 key and writes
# site/v1/manifest.json.sig (base64 of the 64-byte signature over the exact
# manifest bytes). The apps refuse any manifest without a valid signature.
#
# The private key (PEM) comes from $CATALOG_SIGNING_KEY — a secret on the
# github-pages environment, so only the publish job on main can read it. The
# signature is checked against the committed public key before anything ships.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MANIFEST="$ROOT/site/v1/manifest.json"
PUBLIC_KEY="$ROOT/keys/manifest-signing.pub.pem"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

[ -n "${CATALOG_SIGNING_KEY:-}" ] || { echo "::error::CATALOG_SIGNING_KEY is not set." >&2; exit 1; }
[ -f "$PUBLIC_KEY" ] || { echo "::error::$PUBLIC_KEY is missing. Run scripts/new-signing-key.sh." >&2; exit 1; }

umask 077
printf '%s\n' "$CATALOG_SIGNING_KEY" > "$TMP/key.pem"
openssl pkeyutl -sign -inkey "$TMP/key.pem" -rawin -in "$MANIFEST" -out "$TMP/sig.bin"
openssl pkeyutl -verify -pubin -inkey "$PUBLIC_KEY" -rawin -in "$MANIFEST" -sigfile "$TMP/sig.bin" >/dev/null \
  || { echo "::error::The signing key does not match keys/manifest-signing.pub.pem." >&2; exit 1; }
base64 < "$TMP/sig.bin" | tr -d '\n' > "$MANIFEST.sig"
echo >> "$MANIFEST.sig"
echo "Signed $(basename "$MANIFEST")"
