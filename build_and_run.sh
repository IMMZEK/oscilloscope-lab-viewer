#!/bin/bash

# Ensure we exit on any error
set -e

echo "Cleaning Bazel workspace..."
bazel clean

echo "Building project with Bazel..."
bazel build //src:viewer

# Get Bazel binary directory for dependencies
BAZEL_BIN="$(bazel info bazel-bin)"

# Set up Python environment with Bazel-managed dependencies
export PYTHONPATH="$PWD:$BAZEL_BIN:$PYTHONPATH"

echo "Running application with system Python..."
python3 src/run_viewer.py