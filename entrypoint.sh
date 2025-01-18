#!/bin/bash
set -e

# Configure the GitHub Actions Runner

sudo RUNNER_ALLOW_RUNASROOT=true 
./config.sh --url ${REPO_URL} --token ${RUNNER_TOKEN} --name $(hostname) --work ${RUNNER_WORKDIR} --unattended --replace

# Start the runner
./run.sh
