#!/usr/bin/env bash
set -euo pipefail

# Deliberately does not create credentials or change networking implicitly.
# Configure the host hotspot with the platform's approved network tooling, then
# use this script only as an explicit nmcli action when nmcli is available.
: "${NODE_ID:?NODE_ID must be set}"
: "${FIELDNODE_HOTSPOT_PASSWORD:?FIELDNODE_HOTSPOT_PASSWORD must be set in the host environment}"
WIFI_IFACE="${WIFI_IFACE:-wlan0}"
SSID="${FIELDNODE_HOTSPOT_SSID:-FieldNode-${NODE_ID}}"

command -v nmcli >/dev/null || { echo "nmcli not found; configure hotspot using the host-approved tool" >&2; exit 1; }
nmcli device wifi hotspot ifname "$WIFI_IFACE" ssid "$SSID" password "$FIELDNODE_HOTSPOT_PASSWORD"
