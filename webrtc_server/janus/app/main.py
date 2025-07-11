#!/usr/bin/env python

import sys
import traceback

from server import WebRTCServer

def run_forever():
    try:
        server = WebRTCServer()
        ret = server.start_server()
        print("Webrtc server exited with code ", ret)
    except Exception as e:
        print(traceback.format_exc().replace("\n", " "))
        sys.exit(-1)

def main():
    run_forever()

if __name__ == '__main__':
    main()
