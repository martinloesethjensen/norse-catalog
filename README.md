# norse-catalog

Public ingredient taxonomy and recipe catalog for the Norse Mixology apps, published to
`https://martinloesethjensen.github.io/norse-catalog/v1/manifest.json`.

## Changing the catalog

1. Edit `generate.py`.
2. `python3 -m unittest discover -s tests -t . -v`
3. `python3 -m catalog.build` — validates and writes `site/v1/` (hashed files + `manifest.json`).
4. Commit `generate.py` **and** `site/`, open a PR. CI fails if `site/` is stale or invalid.
5. Merge → the `publish` workflow deploys to Pages. Apps pick it up on their next cold launch
   and apply it on the launch after that.

## Incident: bad content was published

Content that passes validation but is wrong (typo, bad recipe):

1. `git revert <bad commit>` on a branch, run `python3 -m catalog.build`, commit `site/`, PR, merge.
2. The build publishes a new manifest (new `generatedAt`) pointing at the reverted content;
   clients replace the bad catalog on their next refresh.

Never delete files from `site/v1/` by hand — the build retains the last 3 versions so a
CDN-cached manifest never points at a missing file.

## Manifest signing

The publish workflow signs `manifest.json` with an Ed25519 key and publishes
`manifest.json.sig` next to it (base64 of the signature over the exact manifest bytes).
The apps reject any manifest whose signature doesn't verify against a public key they
ship with, so controlling the host or the domain is not enough to change the catalog.

- Private key: the `CATALOG_SIGNING_KEY` secret on the `github-pages` environment.
  Keep that environment's deployment branches limited to `main`.
- Public key: `keys/manifest-signing.pub.pem`. The publish job refuses to deploy if the
  secret doesn't match it.
- The signature is created in CI only and never committed (`site/v1/manifest.json.sig`
  is gitignored).

**Rotating the key:** run `scripts/new-signing-key.sh` (needs OpenSSL 3). Add the printed
app key to the apps' trusted keys and ship a release **before** switching the secret and
committing the new `.pub.pem`. Remove the old key from the apps a release later.

## Guarantees the apps rely on

- `manifest.json` schema is fixed for `/v1/`; breaking changes go to `/v2/`.
- Hashed files are immutable once published.
- Everything published has passed `catalog/validate.py`.
- Every published `manifest.json` has a `manifest.json.sig` from the signing key.
