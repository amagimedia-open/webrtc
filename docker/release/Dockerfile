# Release Stage Dockerfile

ARG BASE_IMAGE

FROM public.ecr.aws/amagi-media-labs-sec/secure-container-base/python:3.13

ARG WORKDIR=/home/root/installation
WORKDIR $WORKDIR

COPY --from=${BASE_IMAGE} /opt/janus /opt/janus/
COPY --from=${BASE_IMAGE} /home/root/installation/webrtc_build/webrtc_server/ $WORKDIR/webrtc_server
# TODO
COPY --from=${BASE_IMAGE} /home/root/installation/webrtc_build/config_discovery/ $WORKDIR/config_discovery
COPY --from=${BASE_IMAGE} /home/root/installation/webrtc_build/docker/entrypoint.py $WORKDIR/entrypoint.py
COPY --from=${BASE_IMAGE} $WORKDIR/packages/ $WORKDIR/
COPY --from=${BASE_IMAGE} /tmp/janus/* /lib/x86_64-linux-gnu/
COPY --from=${BASE_IMAGE} /lib/libsrtp2.so.1 /lib/libsrtp2.so.1

# Set PYTHONPATH to include the packages directory
ENV PYTHONPATH $WORKDIR

ENTRYPOINT ["python3","/home/root/installation/entrypoint.py"]
