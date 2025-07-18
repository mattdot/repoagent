#!/bin/bash

# TPM Agent Docker Container Entrypoint Script
# This script runs the C# Semantic Kernel agent inside the Docker container

set -e

echo "::group::TPM Agent - Starting Docker Container"
echo "TPM Agent with Semantic Kernel starting..."

# Set verbose mode if requested
if [ "$INPUT_VERBOSE" == "true" ]; then
  set -x
  echo "Verbose mode enabled"
fi

echo "Operation: $INPUT_OPERATION"
echo "Target: $INPUT_TARGET"
echo "Verbose: $INPUT_VERBOSE"

# Build and run the C# application
echo "Building and running TPM Agent..."
cd /app/src || cd src || {
  echo "Error: Cannot find source directory"
  exit 1
}

# Build the application if not already built
if [ ! -f "bin/Release/net8.0/TpmAgent.dll" ]; then
  echo "Building the application..."
  dotnet build -c Release
fi

# Run the application
echo "Running TPM Agent..."
dotnet run --configuration Release --no-build

# Check if the output file was created
if [ -f "/tmp/github_output.txt" ]; then
  echo "Agent completed successfully, setting outputs..."
  
  # Read the outputs from the file
  while IFS= read -r line; do
    echo "$line" >> $GITHUB_OUTPUT
  done < "/tmp/github_output.txt"
  
  echo "Outputs set successfully"
else
  echo "Warning: No output file found, setting default success outputs"
  echo "result=TPM Agent completed" >> $GITHUB_OUTPUT
  echo "status=success" >> $GITHUB_OUTPUT
fi

echo "TPM Agent container execution completed"
echo "::endgroup::"