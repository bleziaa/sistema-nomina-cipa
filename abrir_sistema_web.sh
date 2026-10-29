#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$(readlink -f "$0")")"
URL='http://127.0.0.1:8765/index.html'
if ! curl -fsS http://127.0.0.1:8765/ >/dev/null 2>&1; then
  nohup python3 -m http.server 8765 --bind 127.0.0.1 >"${TMPDIR:-/tmp}/nomina-cipa-web.log" 2>&1 &
  for _ in {1..30}; do
    if curl -fsS http://127.0.0.1:8765/ >/dev/null 2>&1; then break; fi
    sleep 0.2
  done
fi
if ! curl -fsS "$URL" >/dev/null; then
  echo 'No se pudo iniciar el servidor local en el puerto 8765.' >&2
  exit 1
fi
xdg-open "$URL" >/dev/null 2>&1 &
echo "Sistema abierto en $URL"
