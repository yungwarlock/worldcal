#!/usr/bin/env bash

if [ -n "$FLY_APP_NAME" ]; then
  echo "Running in fly.io"
else
  echo "Not running in fly.io"
fi

cleanup() {
  kill ${!}
  echo "Cleaning up"

  if [ -n "$FLY_APP_NAME" ]; then
    # Turn off swap
    echo "Cleanup... Turn off swap"
  fi
}

trap cleanup INT
trap cleanup TERM

"$@" & wait ${!}
