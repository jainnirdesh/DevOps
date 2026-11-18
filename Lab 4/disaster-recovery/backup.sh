#!/usr/bin/env bash
set -euo pipefail
LAB4_BACKUP_DIR="$(cd "$(dirname "$0")" && pwd)"
LAB4_VOLUME="${1:-lab4-dr-vol}"
LAB4_ARCHIVE="${2:-backup_snapshot.tar.gz}"
docker volume inspect "$LAB4_VOLUME" > /dev/null
docker run --rm --mount "type=volume,src=$LAB4_VOLUME,dst=/data,readonly" --mount "type=bind,src=$LAB4_BACKUP_DIR,dst=/backup" lab4-app:1.0 python -c 'import sys,tarfile; t=tarfile.open("/backup/"+sys.argv[1],"w:gz"); t.add("/data",arcname="."); t.close()' "$LAB4_ARCHIVE"
echo "Backup complete: $LAB4_ARCHIVE"
