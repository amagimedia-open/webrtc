#!/bin/bash

Usage() {
    echo "Usage: $0 <Tardis repo path>"
    exit 1
}

[ $# -ne 1 ] && Usage

TARDIS_HOME=$1
PROTO_DIR=${TARDIS_HOME}/protos/
NDI_SWITCHER_DIR=${TARDIS_HOME}/ndi_switcher/

if [ ! -d $TARDIS_HOME ]; then
    echo "Tardis repo path given not found. path: ${TARDIS_HOME}"
    exit 1
fi

if [ ! -d $PROTO_DIR ]; then
    echo "Proto directory not found. path: ${PROTO_DIR}"
    exit 1
fi

if [ ! -d $NDI_SWITCHER_DIR ]; then
    echo "NDI Switcher App directory not found. path: ${NDI_SWITCHER_DIR}"
    exit 1
fi

# build the proto files
python3 -m grpc_tools.protoc -I ${PROTO_DIR} --python_out=. --grpc_python_out=. ndi_switcher.proto

# copy NDI Switcher gRPC server to current directory
cp ${NDI_SWITCHER_DIR}/ndi_switcher_grpc.py .

# run the ndiSwitcherConfigUpdaterTest.py
python3 -m unittest ndiSwitcherConfigUpdaterTest.py

# Remove proto files
rm ndi_switcher_pb2* | true

# Remove copied NDI Switcher gRPC server in current directory
rm ndi_switcher_grpc.py | true
