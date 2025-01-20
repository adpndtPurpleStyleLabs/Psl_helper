#!/bin/bash
set -e

export RUNNER_ALLOW_RUNASROOT=1

# Define persistent work directory
RUNNER_WORKDIR="/tmp/runner-workdir"
RUNNER_FILE="/tmp/runner-workdir/runner_name.txt"

# Ensure environment variables are set
if [[ -z "$RUNNER_NAME" || -z "$RUNNER_TOKEN" || -z "$REPO_URL" ]]; then
    echo "Error: RUNNER_NAME, RUNNER_TOKEN, or REPO_URL is not set."
    exit 1
fi

# Ensure workdir exists
mkdir -p "$RUNNER_WORKDIR"

# Check if the runner is already configured
if [[ -f "$RUNNER_FILE" ]] && grep -q "$RUNNER_NAME" "$RUNNER_FILE"; then
    echo "Runner already configured. Proceeding to start."
else
    echo "Configuring the runner..."
    ./config.sh remove --token "${RUNNER_TOKEN}" || true
    ./config.sh --url "${REPO_URL}" --token "${RUNNER_TOKEN}" --name "${RUNNER_NAME}" --work "${RUNNER_WORKDIR}" --unattended --replace
    echo "$RUNNER_NAME" > "$RUNNER_FILE"
fi

# Start the runner
./run.sh
