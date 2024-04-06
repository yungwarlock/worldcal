#!/bin/sh

# Check if it is running in fly.io

if [ -n "$FLY_APP_NAME" ]; then
  fallocate -l 512M /swapfile
  chmod 0600 /swapfile
  mkswap /swapfile
  echo 10 > /proc/sys/vm/swappiness
  swapon /swapfile
else
  echo "Not running in fly.io"
fi

/app/tailscaled --state=/var/lib/tailscale/tailscaled.state --socket=/var/run/tailscale/tailscaled.sock &
/app/tailscale up --authkey=${TAILSCALE_AUTHKEY} --hostname=fly-app

$SHELL "$@"

if [ -n "$FLY_APP_NAME" ]; then
  # Turn off swap
  swapoff /swapfile
  rm /swapfile
fi