#!/bin/bash

# stage-in.sh
# Description: Runs the Stars copy command inside the Docker container to stage in Sentinel-2 data.

# Exit immediately on error
set -e

# Create output directory if it doesn't exist


# Run the Docker container and execute the Stars command
docker run --rm \
  -v "$PWD:/mounted_dir" \
  --workdir /mounted_dir \
  ghcr.io/terradue/stars \
  Stars copy --harvest \
             -conf=usersettings.json \
             -v \
             -rel \
             -r '4' \
             -si CDS1 \
             -o /mounted_dir/stars_out \
             'https://catalogue.dataspace.copernicus.eu/stac/collections/SENTINEL-2/items/S2A_MSIL1C_20250318T101751_N0511_R065_T32UPE_20250318T140212.SAFE'
