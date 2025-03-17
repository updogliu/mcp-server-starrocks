#!/usr/bin/env bash
set -e

# Usage:
#
# Build image locally. Recommend using OrbStack instead of Docker when building on Mac OS.
# $ ./build.sh
#
# Build image and push it to image registry (won't update the local image). Need to docker login at first.
# $ ./build.sh --push


# Set the current working directory to the directory of this script.
cd "$(dirname "$0")"

VERSION=0.1.0
IMAGE=updogliu/mcp-server-starrocks

if [[ $1 == '--push' ]]; then
  # See this doc for how to create a multiple platforms builder:
  #   https://docs.orbstack.dev/docker/images#multiplatform
  echo "Build and push image $IMAGE ..."
  docker build --platform linux/amd64,linux/arm64 --push -t $IMAGE:$VERSION -t $IMAGE:latest -f ./Dockerfile .
else
  echo "Build locally $IMAGE ..."
  docker build -t $IMAGE:$VERSION -t $IMAGE:latest --load -f ./Dockerfile .
fi
