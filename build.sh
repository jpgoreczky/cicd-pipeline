#!/bin/bash

# Terminate the script immediately if any command fails
set -e

# Define variables with default values using parameter expansion
IMAGE_NAME=${IMAGE_NAME:-"fastapi-project"}
TAG=${TAG:-"latest"}
DOCKERFILE="Dockerfile"

# Announce the build initiation to the standard output
echo "Initiating Docker build sequence for image: ${IMAGE_NAME}:${TAG}"

# Execute the Docker build command
docker build \
  --file $DOCKERFILE \
  --tag "${IMAGE_NAME}:${TAG}" \
 .

# Confirm successful execution
echo "Build sequence completed successfully. Image ${IMAGE_NAME}:${TAG} is ready for deployment."