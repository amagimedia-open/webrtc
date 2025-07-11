#!/bin/bash

set -x

# Define the path vars
declare -r SCRIPT_DIR=$(dirname ${BASH_SOURCE[0]})
declare -r PROJROOT=$(realpath $SCRIPT_DIR/../)
declare -r DOCKER_BUILD_DIR="${PROJROOT}/docker/"

pushd $PROJROOT

tar -cvzf ${DOCKER_BUILD_DIR}/workspace.tgz $(git ls-files)
tar tvf ${DOCKER_BUILD_DIR}/workspace.tgz

pushd ${DOCKER_BUILD_DIR}

docker build --no-cache -t amagidevops/tardis:test_webrtc_02 . --platform linux/amd64 --progress=plain -f Dockerfile.janus

popd #DOCKER_BUILD_DIR
popd #PROJROOT
