#!/bin/bash
set -e

# Configure the GitHub Actions Runner



export RUNNER_ALLOW_RUNASROOT=true
./config.sh remove --token ${RUNNER_TOKEN}
./config.sh --url ${REPO_URL} --token ${RUNNER_TOKEN} --name ${RUNNER_NAME} --work ${RUNNER_WORKDIR} --unattended --replace

# Start the runner
./run.sh
