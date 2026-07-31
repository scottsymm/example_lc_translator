#!/usr/bin/env bash
set -euo pipefail

# Start the API in the background
uv run --package lc-translator-api uvicorn lc_translator_api.main:app --reload &
API_PID=$!

# Start the web dev server
pnpm --filter web dev

# Clean up the API on exit
trap "kill $API_PID" EXIT
