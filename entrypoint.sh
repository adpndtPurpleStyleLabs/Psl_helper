#!/bin/bash
set -e

export RUNNER_ALLOW_RUNASROOT=true
RUNNER_FILE="/tmp/runner-workdir/runner_name.txt"

if [[ -z "$RUNNER_NAME" ]]; then
    echo "Error: RUNNER_NAME is not set. Exiting."
    exit 1
fi

mkdir -p /tmp/runner-workdir

if [[ -f "$RUNNER_FILE" ]] && grep -q "$RUNNER_NAME" "$RUNNER_FILE"; then
    echo "Runner name already exists in $RUNNER_FILE. Proceeding..."
else
    echo "Runner name not found in $RUNNER_FILE. Configuring the runner..."
    ./config.sh remove --token "${RUNNER_TOKEN}" || true
    ./config.sh --url "${REPO_URL}" --token "${RUNNER_TOKEN}" --name "${RUNNER_NAME}" --work "${RUNNER_WORKDIR}" --unattended --replace

    echo "$RUNNER_NAME" > "$RUNNER_FILE"
fi


sleep 2000

./run.sh
