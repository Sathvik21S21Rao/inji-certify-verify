#!/bin/bash
# Postgres init script: the upstream DDL (mounted at /verify-ddl) uses unqualified table names, the service uses schema "verify".
set -euo pipefail
psql -v ON_ERROR_STOP=1 -U postgres -d inji_verify -c 'CREATE SCHEMA IF NOT EXISTS verify'
for f in /verify-ddl/*.sql; do
  PGOPTIONS='-c search_path=verify' psql -v ON_ERROR_STOP=1 -U postgres -d inji_verify -f "$f"
done
