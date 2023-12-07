import sys

from modules.configParser import ConfigParser

#Maybe send the google protocol buffer directly here in case
#of GRPC, not sure right now.
class JanusServerConf:
    def __init__(self, cfg_file_path):
        self.__cfg_file_path         = cfg_file_path
        self.__config_dict           = dict()
        self.__config_dict           = self.__get_config_file_dict()
    #end __init__

    def get_dict(self):
        return self.__config_dict

    #end get_dict

    def __get_grpc_dict(self):
        pass

    def __get_config_file_dict(self):
        cfg_dict = dict()
        self.parser = ConfigParser()
        ret = self.parser.parse(self.__cfg_file_path)
        if ret == False:
            print(f'Failed to parse {self.__cfg_file_path}, exiting')
            #Maybe raise an exception and handle it in main app
            sys.exit(-1)

        cfg_dict['videoport']      = self.parser.get_janus_input_video_port()
        cfg_dict['audioport']      = self.parser.get_janus_input_audio_port()
        cfg_dict['ice_interface']  = self.parser.get_janus_ice_interface()
        cfg_dict['stun_enable']    = self.parser.get_janus_enable_stun()
        cfg_dict['stun_server']    = self.parser.get_janus_stun_server()
        cfg_dict['stun_port']      = self.parser.get_janus_stun_port()
        cfg_dict['turn_enable']    = self.parser.get_janus_enable_turn()
        cfg_dict['turn_server']    = self.parser.get_janus_turn_server()
        cfg_dict['turn_port']      = self.parser.get_janus_turn_port()
        cfg_dict['turn_username']  = self.parser.get_janus_turn_username()
        cfg_dict['turn_password']  = self.parser.get_janus_turn_password()
        cfg_dict["http_port"]      = self.parser.get_janus_http_port()
        cfg_dict["websocket_port"] = self.parser.get_janus_websocket_port()
        cfg_dict["rtp_port_range"] = self.parser.get_janus_rtp_port_range()
        cfg_dict["enable_nat_1_to_1_mapping"] = self.parser.get_janus_enable_nat_1_to_1_mapping()
        cfg_dict["public_ip"]      = self.parser.get_janus_public_ip()
        cfg_dict["admin_http_port"] = self.parser.get_janus_admin_http_port()
        cfg_dict["admin_websocket_port"] = self.parser.get_janus_admin_websocket_port()

        return cfg_dict

    #end __get_config_file_dict
