#!/usr/bin/env bashio
set -e

bashio::log.info "🔹 Welcome to OMROM 2JCIE-BU Exporter"

SENSOR_SERIAL_DEVICE="$(bashio::config 'SENSOR_SERIAL_DEVICE')"
SERVER_HTTP_PORT=$(bashio::config 'SERVER_HTTP_PORT')

bashio::log.info "✅ Configuration Loaded:"
bashio::log.info "  SENSOR_SERIAL_DEVICE=$SENSOR_SERIAL_DEVICE"
bashio::log.info "  SERVER_HTTP_PORT=$SERVER_HTTP_PORT"

while true; do
    bashio::log.info "🔹 Starting 2JCIE-BU Exporter..."
    # Custom variables are already exported above
    export SENSOR_SERIAL_DEVICE="$SENSOR_SERIAL_DEVICE"
    export SERVER_HTTP_PORT=$SERVER_HTTP_PORT
    /usr/bin/python3 -u /app/main.py

    bashio::log.warning "Exporter stopped! Waiting 5 second before reconnecting..."
    sleep 5;
done
