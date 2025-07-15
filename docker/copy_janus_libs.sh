#!/bin/bash

set -x

binary="/opt/janus/bin/janus"
destination="/opt/lib/"

# Create destination directory if it doesn't exist
if [ ! -d "$destination" ]; then
    mkdir -p "$destination"
fi

# Run ldd and extract library paths
libraries=$(ldd "$binary" | grep '=>' | awk '{print $3}')

# Copy files to the destination
for file in $libraries; do
    cp "$file" "$destination"
done

# the below libraries do not show up when doing ldd on the janus binary.
# so, copying them manually instead.
cp /usr/lib/x86_64-linux-gnu/libmicrohttpd.so.12 $destination
