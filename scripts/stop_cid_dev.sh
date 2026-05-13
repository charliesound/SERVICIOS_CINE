#!/usr/bin/env bash
set -euo pipefail

kill_port() {
  local port="$1"
  local name="$2"

  echo "===== stopping $name on port $port ====="

  local pids
  pids="$(ss -ltnp 2>/dev/null | awk -v port=":$port" '$0 ~ port {print $NF}' | sed -n 's/.*pid=\([0-9]\+\).*/\1/p' | sort -u)"

  if [ -z "$pids" ]; then
    echo "$name no está usando el puerto $port"
    return 0
  fi

  echo "PIDs: $pids"
  kill $pids 2>/dev/null || true
  sleep 1

  local still
  still="$(ss -ltnp 2>/dev/null | awk -v port=":$port" '$0 ~ port {print $NF}' | sed -n 's/.*pid=\([0-9]\+\).*/\1/p' | sort -u)"

  if [ -n "$still" ]; then
    echo "Forzando parada de PIDs: $still"
    kill -9 $still 2>/dev/null || true
  fi

  echo "$name parado."
}

kill_port 8010 "AILinkCinema backend"
kill_port 3001 "AILinkCinema frontend"

echo
echo "Estado final:"
ss -ltnp | grep -E ':8010|:3001' || echo "Puertos 8010 y 3001 libres."
