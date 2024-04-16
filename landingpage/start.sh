#!/usr/bin/env bash

if [ -n "$FLY_APP_NAME" ]; then
  fallocate -l 512M /swapfile
  chmod 0600 /swapfile
  mkswap /swapfile
  echo 10 > /proc/sys/vm/swappiness
  swapon /swapfile
else
  echo "Not running in fly.io"
fi

cleanup() {
  kill ${!}
  echo "Cleaning up"

  if [ -n "$FLY_APP_NAME" ]; then
    # Turn off swap
    swapoff /swapfile
    rm /swapfile
  fi
}

trap cleanup INT
trap cleanup TERM

"$@" & wait ${!}
