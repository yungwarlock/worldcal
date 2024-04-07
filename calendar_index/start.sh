#!/bin/sh

# Check if it is running in fly.io

if [ -n "$FLY_APP_NAME" ]; then
  fallocate -l 512M /swapfile
  chmod 0600 /swapfile
  mkswap /swapfile
  echo 10 > /proc/sys/vm/swappiness
  swapon /swapfile

  /app/tailscaled --state=/var/lib/tailscale/tailscaled.state --socket=/var/run/tailscale/tailscaled.sock &>/dev/null &
  /app/tailscale up --authkey=${TAILSCALE_AUTHKEY} --hostname=fly-app
else
  echo "Not running in fly.io"
  /app/tailscaled --tun=userspace-networking --socks5-server=localhost:1055 &>/dev/null &
  /app/tailscale up --authkey=${TAILSCALE_AUTHKEY} --hostname=cloudrun-app
  echo Tailscale started
  export ALL_PROXY=socks5://localhost:1055
fi

$SHELL "$@"

if [ -n "$FLY_APP_NAME" ]; then
  # Turn off swap
  swapoff /swapfile
  rm /swapfile
fi