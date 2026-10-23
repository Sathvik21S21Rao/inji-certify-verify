# source env.sh: puts a JDK 21+ (the api-test builds need it) and the repo's .venv on PATH.
# JDK, first match wins: $JAVA_HOME if it is 21+, macOS /usr/libexec/java_home -v 21+, the newest
# ~/.local/jdks/jdk-2x*, else the java already on PATH (with a warning if it is older than 21).
# Safe to source from scripts running under `set -euo pipefail`, and from zsh.
_jmajor() { [ -x "$1/bin/java" ] && "$1/bin/java" -version 2>&1 | sed -n '1s/.*version "\([0-9]*\).*/\1/p' || true; }
if ! [ "$(_jmajor "${JAVA_HOME:-/nonexistent}")" -ge 21 ] 2>/dev/null; then
  _jdk=$( { [ -x /usr/libexec/java_home ] && /usr/libexec/java_home -v 21+ 2>/dev/null; } || true)
  [ -n "$_jdk" ] || _jdk=$(ls -d "$HOME"/.local/jdks/jdk-2[1-9]* 2>/dev/null | sort -V | tail -n1 || true)
  if [ -n "$_jdk" ]; then export JAVA_HOME="$_jdk"; fi
  unset _jdk
fi
if [ -n "${JAVA_HOME:-}" ]; then export PATH="$JAVA_HOME/bin:$PATH"; fi
_jv=$(java -version 2>&1 | sed -n '1s/.*version "\([0-9]*\).*/\1/p' || true)
[ "${_jv:-0}" -ge 21 ] 2>/dev/null || echo "env.sh: warning: java on PATH is '${_jv:-none}', the api-test builds need JDK 21+ (set JAVA_HOME)" >&2
unset _jv
unset -f _jmajor
_root=$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)
export PATH="$_root/.venv/bin:$PATH"
unset _root
