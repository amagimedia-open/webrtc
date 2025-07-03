# Build Stage Dockerfile

# syntax=docker/dockerfile:1
###############################################################################
# Author: Manish Sharma <manish.sharma@amagi.com>
#
###############################################################################

# Use lightweight alpine image as base image to build the server and the worker
FROM python:3 AS build

# Specify labels
LABEL author=manish.sharma@amagi.com
LABEL maintainer=manish.sharma@amagi.com

WORKDIR /home/root/installation

# Copy the repository to build
COPY ["workspace.tgz",\
      "/home/root/installation/"]

# Install network analysis tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    tcpdump \
    net-tools \
    dnsutils

RUN mkdir -p webrtc_build \
    && tar -zxvf workspace.tgz -C webrtc_build \
    && cp webrtc_build/requirements.txt /home/root/installation \
    && cd webrtc_build/webrtc_server/janus/build/ && ./build_janus.sh \
    && cd /home/root/installation/webrtc_build/webrtc_server/janus/build/ && ./copy_janus_libs.sh

# TODO: Cleanup requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt -t ./packages/

RUN cd /home/root/installation/ \
    && rm *.tgz
