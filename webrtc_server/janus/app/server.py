#!/usr/bin/env python

import sys
import traceback
import time
import subprocess
import threading

class WebRTCServer:
    def __init__(self):
        print("Webrtc server initialised")

    def log_output(self, process):
        while True:
            output_line = process.stdout.readline()
            if not output_line:
                break
            print(output_line, end="")

    def spawn_server_app (self):
        try:
            cmd = ['/opt/janus/bin/janus']
            self.proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=False)
            # Create a separate thread for logging the output
            log_thread = threading.Thread(target=self.log_output, args=(self.proc,), daemon=True)
            log_thread.start()
            print("----New Process Spawned----")
            print("Spawning command: %s"%str(cmd))
            return 0
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print("failed to spawn janus webrtc gateway: %s"
                    %str(traceback.format_exception(exc_type, exc_value, exc_traceback)))
            return -1

    def is_process_running (self):
        if self.proc == None:
            return False
        ret = self.proc.poll()
        if ret == None:
            return True
        else:
            return False

    def monitor_app (self):
        while True:
            try:
                if self.is_process_running() is False:
                    print("Webrtc server process is not running...")
                    return 1
                time.sleep(1)
            except:
                print(traceback.format_exc().replace("\n", " "))
                return -1

    def start_server (self):
        ret = 0
        while ret == 0:
            ret = self.spawn_server_app()
            if ret == -1:
                return ret
            ret = self.monitor_app()
            if ret == -1:
                return ret
        return ret
