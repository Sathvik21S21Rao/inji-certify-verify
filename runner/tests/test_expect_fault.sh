#!/usr/bin/env bash
# Run from anywhere: bash runner/tests/test_expect_fault.sh
cd "$(dirname "$0")/../.." || exit 1
S=scripts/expect-fault.sh
A=evidence/sp5/ci/art-39751732547      # fault=strip-credential-endpoint, shim off
G=evidence/sp5/ci/art-39751717857      # known good
N=evidence/sp4/SP4.4/fault-certify-shim-on
W=$(mktemp -d)
mkdir "$W/certify-shim-off"
echo '| oid4vci-1_0-issuer-metadata-test | a | b | OK |' > "$W/certify-shim-off/gate.md"
fail=0
t() { # expected_exit description args...
  want=$1 desc=$2; shift 2
  out=$(bash "$S" "$@"); got=$?
  if [ "$got" = "$want" ]; then echo "ok   $desc"; else echo "FAIL $desc (want $want got $got)"; fail=1; fi
  echo "     $out"
}
t 0 "certify caught"          certify  strip-credential-endpoint false false 1 $A/conformance-certify
t 0 "combined caught"         combined strip-credential-endpoint false false 1 $A/conformance-combined
t 0 "verify green"            verify   strip-credential-endpoint false false 0 $A/conformance-verify
t 1 "fault not caught"        certify  strip-credential-endpoint false false 0 $G/conformance-certify
t 1 "wrong reason"            certify  strip-credential-endpoint false false 1 "$W"
t 2 "rc2 passthrough"         certify  strip-credential-endpoint false false 2 $A/conformance-certify
t 4 "rc4 passthrough"         certify  strip-nonce-endpoint true false 4 $N
t 1 "none rc1"                certify  none false false 1 $A/conformance-certify
t 0 "none rc0"                certify  none false false 0 $G/conformance-certify
t 0 "nonce shim-on caught"    certify  strip-nonce-endpoint true false 1 $N
t 0 "nonce shim-off green"    certify  strip-nonce-endpoint false false 0 $G/conformance-certify
t 1 "no expectation (shim)"   certify  strip-credential-endpoint true false 1 $A/conformance-certify
t 1 "no expectation (strict)" certify  strip-credential-endpoint false true 1 $A/conformance-certify
cp -r $A/conformance-combined "$W/comb"
sed -i 's/^\(### Gate verify-x509:\) GREEN/\1 RED/' "$W/comb/verify-x509/gate.md"
t 1 "other config red"        combined strip-credential-endpoint false false 1 "$W/comb"
rm -rf "$W"
exit $fail
