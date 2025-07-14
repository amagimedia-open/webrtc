#!/bin/bash

set -x

# Input validation
if [[ $# -ne 1 ]]
then
    echo "USAGE: $0 <tag_name>"
    exit 1
fi

# Get the release tag
TAG=$1

# Define the path vars
declare -r SCRIPT_DIR=$(dirname ${BASH_SOURCE[0]})
declare -r PROJROOT=$(realpath $SCRIPT_DIR/../)
declare -r DOCKER_BUILD_DIR="${PROJROOT}/docker/"

pushd $PROJROOT

tar -cvzf ${DOCKER_BUILD_DIR}/workspace.tgz $(git ls-files)
tar tvf ${DOCKER_BUILD_DIR}/workspace.tgz

pushd ${DOCKER_BUILD_DIR}

docker build --no-cache -t $TAG . --platform linux/amd64 --progress=plain -f Dockerfile.janus

popd #DOCKER_BUILD_DIR
popd #PROJROOT
