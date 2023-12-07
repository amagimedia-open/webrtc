import requests
import string
import random
import json
import sys
from datetime import datetime

class WebrtcSessionLogger:
    def __init__ (self, janus_admin_http_port):
        self._log_strings = []

        # Create base url for communication
        self._janus_admin_url = "http://127.0.0.1:" + str (janus_admin_http_port) + "/admin"
        print ("HTTP janus admin url to get session details = %s"%self._janus_admin_url)

    def _req_post_with_timeout (self, url, payload, timeout=10):
        req = ""
        try:
            req = requests.post (url, data=payload, timeout=timeout)
        except requests.Timeout:
            print ("Timeout error occured while performing %s POST request."%str (url))
        except requests.ConnectionError:
            print ("Connection error occured while performing %s POST request."%str (url))
        except requests.HTTPError:
            print ("Unsuccessful status code returned while performing %s POST request."%str (url))
        except requests.TooManyRedirects:
            print ("Configured number of redirections exceeded while performing %s POST request."%str (url))
        return req

    def _get_post_req_response (self, url, data):
        res = self._req_post_with_timeout (url, json.dumps (data))
        if not res:
            return False, None
        else:
            res_dict = json.loads (res.text)
            return True, res_dict

    def _get_handle_info (self, transaction_id, session, handle):
        handle_url = f"{self._janus_admin_url}/{session}/{handle}"
        data = {"janus": "handle_info", "transaction": transaction_id, "admin_secret": "janusoverlord"}
        ret, res_dict = self._get_post_req_response (handle_url, data)
        if not ret:
            print ("Not able to fetch each handle detail. Failed %s POST"%handle_url)
            return False
        # Perform the filtering to get necessary details only
        for stream in res_dict['info']['streams']:
            for component in stream['components']:
                del component['dtls']
                del component['in_stats']
                del component['out_stats']
                res_string = str (json.dumps (component))
                handle_log_res_string = "Required info for handle id = " + str (res_dict['handle_id']) + ", session id = " + str (res_dict['session_id']) + " = " + res_string
                self._log_strings.append (handle_log_res_string)

        return True

    def _get_session_info (self, transaction_id, session):
        session_url = f"{self._janus_admin_url}/{session}"
        data = {"janus": "list_handles", "transaction": transaction_id, "admin_secret": "janusoverlord"}
        ret, res_dict = self._get_post_req_response (session_url, data)
        if not ret:
            print ("Not able to fetch each session detail. Failed %s POST"%session_url)
            return False
        res_string = str (json.dumps (res_dict))
        session_res_log_string = "Session info for session id = " + str (res_dict['session_id']) + " = " + res_string
        self._log_strings.append (session_res_log_string)

        # Get the detail of components in every handle that have streams section as non empty
        handles = res_dict["handles"]
        ## Iterate through all handles
        for handle in handles:
            ret = self._get_handle_info (transaction_id, session, handle)

        return ret

    def _get_all_sessions_info (self, transaction_id, dt_string):
        # Get the overall session details
        data = {"janus": "list_sessions", "transaction": transaction_id, "admin_secret": "janusoverlord"}
        ret, res_dict = self._get_post_req_response (self._janus_admin_url, data)
        if not ret:
            print ("Not able to fetch session details. Failed %s POST"%self._janus_admin_url)
            return False
        res_string = str (json.dumps (res_dict))
        res_log_string = "Time = " + dt_string + " Sessions detail = " + res_string
        self._log_strings.append (res_log_string)

        # Get total number of sessions
        number_of_sessions_log_string = "Total number of sessions = " + str (len (res_dict["sessions"]))
        self._log_strings.append (number_of_sessions_log_string)

        # Get the detail of every session
        sessions = res_dict["sessions"]
        ## Iterate through all sessions
        for session in sessions:
            ret = self._get_session_info (transaction_id, session)

        return ret

    def _get_webrtc_session_details (self):
        # Create random transaction string for HTTP Post Request
        all_chars = string.ascii_letters + string.digits + string.punctuation
        transaction_id = ''.join (random.SystemRandom().choices (all_chars, k=10))

        # Get the current time
        now = datetime.now ()
        dt_string = now.strftime ("%d/%m/%Y %H:%M:%S")

        ret = self._get_all_sessions_info (transaction_id, dt_string)

        return ret

    def log_webrtc_session_details (self):
        # Get the all data to log
        ret = self._get_webrtc_session_details ()
        if not ret:
            print ("Error occured while getting details of webrtc sessions")

        # log each line
        for log_string in self._log_strings:
            self._session_logger.info (log_string)

        # Reset log string list
        self._log_strings = []

# Unit Testing
if __name__ == '__main__':
    http_port = 7088
    webrtc_session_logger = WebrtcSessionLogger (http_port)
    webrtc_session_logger.log_webrtc_session_details ()
