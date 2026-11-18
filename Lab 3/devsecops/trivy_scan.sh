#!/usr/bin/env bash
# trivy_scan.sh — Run a Trivy vulnerability scan on a Docker image
# Usage: bash trivy_scan.sh [image_name] [tag]

IMAGE="${1:-python:3.12-slim}"
TAG="${2:-}"
TARGET="${IMAGE}${TAG:+:$TAG}"

echo "============================================"
echo " Trivy Security Scan"
echo " Target : $TARGET"
echo " Date   : $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "============================================"

docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v lab3-trivy-cache:/root/.cache/ aquasec/trivy:latest image \
  --no-progress \
  --severity CRITICAL --exit-code 1 \
  --format table \
  "$TARGET"

EXIT=$?
if [ "$EXIT" -eq 0 ]; then
  echo "[PASS] Trivy scan completed — no CRITICAL vulnerabilities found"
else
  echo "[FAIL] Critical vulnerabilities found or scan failed (exit $EXIT)"
fi
exit $EXIT
