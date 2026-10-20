#!/usr/bin/env bash
# Test-only certs under data/certs/. Idempotent: existing files are kept; --force regenerates.
set -euo pipefail
ROOT="${CONFORMANCE_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
C="$ROOT/data/certs"
[ "${1:-}" = "--force" ] && rm -rf "$C"
mkdir -p "$C"/{tls,ca,verify}
have() { [ -s "$C/$1" ]; }

have tls/tls.crt && have tls/tls.key || openssl req -x509 -newkey rsa:2048 -nodes -days 825 \
  -subj "/CN=certify-tls" -addext "subjectAltName=DNS:certify-tls,DNS:verify-tls,DNS:localhost" \
  -keyout "$C/tls/tls.key" -out "$C/tls/tls.crt" 2>/dev/null

have ca/ca.pem && have ca/ca.key || {
  openssl ecparam -name prime256v1 -genkey -noout -out "$C/ca/ca.key"
  openssl req -x509 -new -key "$C/ca/ca.key" -days 825 -subj "/CN=Conformance Harness Test CA" \
    -addext "basicConstraints=critical,CA:TRUE" -addext "keyUsage=critical,keyCertSign,cRLSign" -out "$C/ca/ca.pem"
}

have verify/leaf.pem && have verify/leaf.key || {
  openssl genpkey -algorithm ED25519 -out "$C/verify/leaf.key"
  openssl req -new -key "$C/verify/leaf.key" -subj "/CN=test.example.com" -out "$C/verify/leaf.csr"
  printf 'subjectAltName=DNS:test.example.com\nbasicConstraints=critical,CA:FALSE\nkeyUsage=critical,digitalSignature\n' > "$C/verify/leaf.ext"
  openssl x509 -req -in "$C/verify/leaf.csr" -CA "$C/ca/ca.pem" -CAkey "$C/ca/ca.key" -CAcreateserial \
    -days 365 -extfile "$C/verify/leaf.ext" -out "$C/verify/leaf.pem" 2>/dev/null
  rm -f "$C/verify/leaf.csr" "$C/verify/leaf.ext"
}

# leaf only, no -certfile: the suite rejects an x5c chain that contains the trust anchor
have verify/verify-signing.p12 || openssl pkcs12 -export -inkey "$C/verify/leaf.key" -in "$C/verify/leaf.pem" \
  -name verify-signing -passout pass:mosip -out "$C/verify/verify-signing.p12"

have verify-ca.pem || cp "$C/ca/ca.pem" "$C/verify-ca.pem"

# test-only keys: readable by container users
find "$C" -type d -exec chmod 0755 {} + ; find "$C" -type f -exec chmod 0644 {} +

# no `tee /dev/stderr`: it reopens a redirected log at offset 0 and overwrites it (seen in evidence/sp1/SP1.4)
out=$(openssl verify -CAfile "$C/ca/ca.pem" "$C/verify/leaf.pem"); echo "$out" >&2
[[ $out == *": OK" ]]
