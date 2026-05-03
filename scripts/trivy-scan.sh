#!/bin/bash
IMAGE=$1
SEVERITY=${2:-"HIGH,CRITICAL"}
OUTPUT_FILE=${3:-"trivy-report.json"}

echo "=== Trivy Security Scan ==="
echo "Image: $IMAGE"

trivy image \
  --severity $SEVERITY \
  --format json \
  --output $OUTPUT_FILE \
  $IMAGE

trivy image \
  --severity $SEVERITY \
  --format table \
  $IMAGE

CRITICAL=$(cat $OUTPUT_FILE | python3 -c \
  "import sys,json; r=json.load(sys.stdin); \
  vulns=[v for res in r.get('Results',[]) \
  for v in res.get('Vulnerabilities',[]) or [] \
  if v.get('Severity')=='CRITICAL']; print(len(vulns))" 2>/dev/null || echo "0")

echo "CRITICAL vulnerabilities: $CRITICAL"
if [ "$CRITICAL" -gt "0" ]; then
    echo "SCAN FAILED: Critical vulnerabilities!"
    exit 1
fi
echo "Trivy scan PASSED!"
exit 0
