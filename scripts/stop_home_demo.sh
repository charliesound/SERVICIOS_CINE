#!/usr/bin/env bash
set -euo pipefail

cd /opt/SERVICIOS_CINE
docker compose -f compose.base.yml -f compose.home.yml --env-file .env down
