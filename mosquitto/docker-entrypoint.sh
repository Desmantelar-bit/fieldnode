#!/bin/sh
# Start only with credentials provisioned out of band by scripts/provision_*.py.
set -eu

password_file=${MQTT_PASSWORD_FILE:-/mosquitto/secrets/passwordfile}
test -s "$password_file" || {
    echo "Mosquitto password file is missing or empty; provision accounts before startup." >&2
    exit 1
}
test -s /mosquitto/config/acl.conf || {
    echo "Mosquitto ACL file is missing or empty." >&2
    exit 1
}

# Copy the read-only host-managed file into Mosquitto's private data volume.
# The image entrypoint prepares /mosquitto/data for uid/gid 1883 before this runs.
install -m 600 "$password_file" /mosquitto/data/passwordfile
chown mosquitto:mosquitto /mosquitto/data/passwordfile

exec mosquitto -c /mosquitto/config/mosquitto.conf
