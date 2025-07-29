# Docker support for Janus Gateway Server

This repo provides a containerized version of the Janus WebRTC Gateway server, built from source with all necessary dependencies.

## Janus Version & Dependencies

### Janus Gateway Version
- **Janus Gateway**: v0.12.0

### Base Image
- **Debian**: 12.8

### Dependencies Versions
- **libmicrohttpd**: v0.9.75
- **libnice**: 0.1.19
- **libwebsockets**: v4.3.0
- **libsrtp**: v2.2.0
- **Other dependencies**:
  - libjansson-dev
  - libglib2.0-dev
  - libevent-dev
  - libtool
  - gengetopt
  - libssl-dev
  - openssl
  - libconfig-dev
  - gtk-doc-tools
  - libcurl4-openssl-dev

## Usage

### 1. Pull Docker Image

```bash
docker pull <your-registry>/janus-gateway:<tag>
```

### 2. Run the Docker Image

You can run the Janus container in two ways:

#### Option A: Mount Configuration Files from Host

```bash
docker run -d --privileged --net=host --restart=unless-stopped \
  --name janus-gateway \
  -v /path/to/your/configs/janus.jcfg:/opt/janus/etc/janus/janus.jcfg \
  -v /path/to/your/configs/janus.plugin.streaming.jcfg:/opt/janus/etc/janus/janus.plugin.streaming.jcfg \
  -v /path/to/your/configs/janus.transport.http.jcfg:/opt/janus/etc/janus/janus.transport.http.jcfg \
  -v /path/to/your/configs/janus.transport.websockets.jcfg:/opt/janus/etc/janus/janus.transport.websockets.jcfg \
  <your-registry>/janus-gateway:<tag>
```

#### Option B: Edit Configuration Files Inside Running Container

1. **Start the container with default configurations:**
```bash
docker run -d --privileged --net=host --restart=unless-stopped \
  --name janus-gateway \
  <your-registry>/janus-gateway:<tag>
```

2. **Access the container to edit configuration files:**
```bash
docker exec -it janus-gateway /bin/bash
```

3. **Edit the configuration files as needed**

4. **Restart the container for changes to take effect:**
```bash
docker restart janus-gateway
```
