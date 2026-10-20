#!/usr/bin/env bash
# seed-certify.sh [--api URL]: idempotently create the SD-JWT credential configuration
# (Certify's DB has no volume, so it is lost on every recreate).
set -euo pipefail

CONFIG_ID=ConformanceSdJwt
ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
CONFIG_FILE=$ROOT/compose/seed/certify-sdjwt-config.json
API=http://localhost:8091/v1/certify
if [ "${1:-}" = "--api" ]; then API=${2:?--api needs a URL}; elif [ $# -gt 0 ]; then echo "usage: $0 [--api URL]" >&2; exit 2; fi

present() {
  curl -fs "$API/.well-known/openid-credential-issuer" | python3 -c '
import json,sys; sys.exit(0 if sys.argv[1] in json.load(sys.stdin).get("credential_configurations_supported",{}) else 1)' "$CONFIG_ID"
}

if present; then echo "seed-certify: $CONFIG_ID already present"; exit 0; fi

resp=$(curl -fsS -X POST -H 'Content-Type: application/json' --data @"$CONFIG_FILE" "$API/credential-configurations")
echo "$resp"
echo "$resp" | python3 -c 'import json,sys; sys.exit(0 if json.load(sys.stdin).get("status")=="active" else 1)' \
  || { echo "seed-certify: response status is not active" >&2; exit 1; }

# metadata may be cached; retry up to 30 s
for _ in $(seq 1 15); do
  if present; then echo "seed-certify: $CONFIG_ID seeded"; exit 0; fi
  sleep 2
done
echo "seed-certify: $CONFIG_ID missing from issuer metadata after POST" >&2
exit 1
