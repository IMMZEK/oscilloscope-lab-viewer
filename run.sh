#!/bin/bash

# Get the absolute path to the workspace root
WORKSPACE_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Ensure Bazel dependencies are up to date
bazel build //src:viewer

# Add Bazel's managed pip packages to PYTHONPATH
BAZEL_BIN="$(bazel info bazel-bin)"
export PYTHONPATH="$WORKSPACE_ROOT:$BAZEL_BIN:$PYTHONPATH"

# Use system Python to run the application
python3 "$WORKSPACE_ROOT/src/run_viewer.py"