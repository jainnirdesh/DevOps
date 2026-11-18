#!/usr/bin/env bash
set -euo pipefail
LAB4_BACKUP_DIR="$(cd "$(dirname "$0")" && pwd)"
LAB4_ARCHIVE="${1:-backup_snapshot.tar.gz}"
LAB4_VOLUME="${2:-lab4-dr-vol-restored}"
test -f "$LAB4_BACKUP_DIR/$LAB4_ARCHIVE"
docker volume create --label lab=lab4 "$LAB4_VOLUME"
docker run --rm --mount "type=volume,src=$LAB4_VOLUME,dst=/data" --mount "type=bind,src=$LAB4_BACKUP_DIR,dst=/backup,readonly" lab4-app:1.0 python -c 'import sys,tarfile; t=tarfile.open("/backup/"+sys.argv[1]); t.extractall("/data",filter="data"); t.close()' "$LAB4_ARCHIVE"
echo "Restore complete: $LAB4_VOLUME"
