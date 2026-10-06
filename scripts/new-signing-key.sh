#!/usr/bin/env bash
# Creates a new Ed25519 manifest-signing key pair. Run it on your own machine.
#
#   - writes the public key to keys/manifest-signing.pub.pem (commit it)
#   - writes the private key to the path given (default ./manifest-signing.pem);
#     paste it into the CATALOG_SIGNING_KEY secret on the github-pages
#     environment, then delete the file
#   - prints the raw public key (base64) to add to the apps' trusted keys
#
# Usage: scripts/new-signing-key.sh [PRIVATE_KEY_PATH]
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PRIVATE_KEY="${1:-manifest-signing.pem}"
[ ! -e "$PRIVATE_KEY" ] || { echo "$PRIVATE_KEY already exists; refusing to overwrite it." >&2; exit 1; }
openssl version | grep -q '^OpenSSL 3' || { echo "Needs OpenSSL 3 (macOS: brew install openssl@3)." >&2; exit 1; }

umask 077
openssl genpkey -algorithm ed25519 -out "$PRIVATE_KEY"
openssl pkey -in "$PRIVATE_KEY" -pubout -out "$ROOT/keys/manifest-signing.pub.pem"

echo "Private key: $PRIVATE_KEY  -> CATALOG_SIGNING_KEY secret (github-pages environment), then delete it"
echo "Public key:  keys/manifest-signing.pub.pem  -> commit"
echo "App key (raw Ed25519, base64):"
openssl pkey -pubin -in "$ROOT/keys/manifest-signing.pub.pem" -outform DER | tail -c 32 | base64
