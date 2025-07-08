#!/bin/bash

set -x

DIR="/home/root/installation"

### build tools ###
apt-get update && apt-get install -y \
	automake

### Install Janus related dependencies ###
apt-get update && apt-get install -y \
	libmicrohttpd-dev \
	libjansson-dev \
	libglib2.0-dev \
    libopus-dev \
    libogg-dev \
    libini-config-dev \
	libevent-dev \
	libtool \
	gengetopt \
	libssl-dev \
	openssl \
    libconfig-dev \
    gtk-doc-tools \
	libcurl4-openssl-dev

### Build libmicrohttpd ###
cd $DIR && git clone https://github.com/Karlson2k/libmicrohttpd.git && \
    cd libmicrohttpd && \
    git checkout v0.9.75 && \
    ./bootstrap && \
    ./configure --prefix=$DIR/usr && \
    make && \
    make install && \
    rm -rf $DIR/libmicrohttpd*
mkdir -p /usr/lib/x86_64-linux-gnu/pkgconfig
cp $DIR/usr/lib/pkgconfig/libmicrohttpd.pc /usr/lib/x86_64-linux-gnu/pkgconfig/libmicrohttpd.pc

### Build libnice ###
cd $DIR
export PATH=$PATH:/root/.local/bin
pipx install ninja
pipx install meson
cd $DIR && wget --no-check-certificate https://libnice.freedesktop.org/releases/libnice-0.1.19.tar.gz && \
	tar xvf libnice-0.1.19.tar.gz && \
    cd libnice-0.1.19 && \
    meson --prefix=$DIR/usr build && ninja -C build && ninja -C build install && \
	rm -rf $DIR/libnice-0.1.19*

### Build libwebsockets ###
cd $DIR && rm -rf libwebsockets | true && \
	git clone https://github.com/amagimedia-open/libwebsockets.git && \
	cd libwebsockets && \
	git checkout gy-increase_max_http_header_data && \
	mkdir build && \
	cd build && \
	cmake -DLWS_MAX_SMP=1 -DLWS_WITHOUT_TESTAPPS=ON -DCMAKE_INSTALL_PREFIX:PATH=$DIR/usr -DCMAKE_C_FLAGS="-fpic" .. && \
	make && \
	make install && \
	rm -rf $DIR/libwebsockets*

### Build libsrtp ###
cd $DIR && git clone https://github.com/cisco/libsrtp.git && \
	cd libsrtp && \
	git checkout v2.2.0 && \
	./configure --prefix=$DIR/usr --enable-openssl && \
	make shared_library && \
	make install && \
	rm -rf $DIR/libsrtp*

### Build sofia-sip ###
cd $DIR && git clone https://github.com/freeswitch/sofia-sip.git && \
	cd sofia-sip && git checkout v1.13.7 && \
	cp /home/root/installation/webrtc_build/webrtc_server/janus/build/0001-fix-undefined-behaviour.patch ./ && \
	bash autogen.sh && ./configure && make && make install && \
	rm -rf $DIR/sofia-sip*


### Copy libs to build janus ###
cd $DIR && cp -pvr $DIR/usr/* /usr/

### Build janus gateway ###
cd $DIR && git clone https://github.com/meetecho/janus-gateway.git && \
	cd janus-gateway && \
    git checkout v0.12.0 && \
	# Issue Janus, debug memory
	# https://github.com/meetecho/janus-gateway/issues/1808
	# sed -i 's|//~ #define REFCOUNT_DEBUG|#define REFCOUNT_DEBUG|g' refcount.h && \
	./autogen.sh && \
        # Enable code dump janus
        #export CFLAGS="-fsanitize=address -fno-omit-frame-pointer" && \
        #export LDFLAGS="-lasan" && \
	./configure \
		--prefix=/opt/janus \
		--disable-rabbitmq \
		--disable-mqtt && \
	make && \
	make install && \
	make configs && \
	rm -rf $DIR/janus-gateway*

### Cleaning ###
# cd $DIR && rm -rf usr && \
apt-get clean && apt-get autoclean && apt-get autoremove -y
