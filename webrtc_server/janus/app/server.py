#!/usr/bin/env python

import os
import sys
import traceback
import socket
import time
import queue
import logging
import fileinput
import subprocess
import psutil
import threading

from config import JanusServerConf
from modules import patchJanus
from modules import webrtcSessionLogger

class WebRTCServer:
    def __init__(self):
        self.APP_CONF_FILE_PATH = "/home/root/installation/config.ini"
        self.last_log_time_ms = 0
        self.LOG_INTERVAL = 10000 #in ms
        self.janus_conf = self.get_configs()
        patchJanus.patch_janus_conf(self.janus_conf)

        # for webrtc session logging
        self.last_session_log_time_ms = 0
        self.WEBRTC_SESSION_LOGS_INTERVAL_MS = 30000
        self.webrtc_session_logger = webrtcSessionLogger.WebrtcSessionLogger (int (self.janus_conf['admin_http_port']))

        self.start_server()

    def get_configs(self):
        cfg_file = self.APP_CONF_FILE_PATH
        server_conf = JanusServerConf(cfg_file)
        return server_conf.get_dict()

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
                # for webrtc session logging
                session_log_cur_time_ms = int(round(time.time() * 1000))
                if session_log_cur_time_ms - self.last_session_log_time_ms >= self.WEBRTC_SESSION_LOGS_INTERVAL_MS:
                    try:
                        self.webrtc_session_logger.log_webrtc_session_details ()
                    except:
                        print(traceback.format_exc().replace("\n", " "))
                    self.last_session_log_time_ms = session_log_cur_time_ms
                time.sleep(1)
            except:
                print(traceback.format_exc().replace("\n", " "))
                return -1
        if self.is_process_running() is False:
            return 0
        else:
            pass
            #force kill the process

    def start_server (self):
        ret = 0
        while ret == 0:
            ret = self.spawn_server_app()
            if ret == -1:
                break
            ret = self.monitor_app()
            if ret == -1:
                break
