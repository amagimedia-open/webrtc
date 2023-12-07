import sys

class ConfigParser:
  def __init__(self):
    # private properties.
    self.__configfile = ''
    self.__config = {}

  def __del__(self):
    print("destroying configParser object")


  def parse(self, configfile):
    self.__configfile = configfile

    try:
      with open(self.__configfile) as fd:
        for line in fd:
          line = line.strip()

          # ignore blank lines
          if not line:
            continue

          # ignore comments
          if line[0] == '#':
            continue

          name, val = line.partition("=")[::2]
          name = name.strip()
          val = val.strip()

          if name:
            self.__config[name] = val
    except:
      print ("failed to parse file %s\n"%self.__configfile)
      return False

    return True


  def get_janus_input_video_port(self):
    if "input_video_port" in self.__config:
      return (str(self.__config['input_video_port']))
    else:
      return ""

  def get_janus_input_audio_port(self):
    if "input_audio_port" in self.__config:
      return (str(self.__config['input_audio_port']))
    else:
      return ""

  def get_janus_ice_interface(self):
    if "interface" in self.__config:
      return (str(self.__config['interface']))
    else:
      return ""

  def get_janus_enable_stun(self):
    if "enable_stun" in self.__config:
      return (int(self.__config['enable_stun']))
    else:
      return -1

  def get_janus_stun_server(self):
    if "stun_server" in self.__config:
      return (str(self.__config['stun_server']))
    else:
      return ""

  def get_janus_stun_port(self):
    if "stun_port" in self.__config:
      return (str(self.__config['stun_port']))
    else:
      return ""

  def get_janus_enable_turn(self):
    if "enable_turn" in self.__config:
      return (int(self.__config['enable_turn']))
    else:
      return -1

  def get_janus_turn_server(self):
    if "turn_server" in self.__config:
      return (str(self.__config['turn_server']))
    else:
      return ""

  def get_janus_turn_port(self):
    if "turn_port" in self.__config:
      return (str(self.__config['turn_port']))
    else:
      return ""

  def get_janus_turn_username(self):
    if "turn_username" in self.__config:
      return (str(self.__config['turn_username']))
    else:
      return ""

  def get_janus_turn_password(self):
    if "turn_password" in self.__config:
      return (str(self.__config['turn_password']))
    else:
      return ""

  def get_janus_http_port(self):
    if "http_port" in self.__config:
      return (str(self.__config['http_port']))
    else:
      return ""

  def get_janus_websocket_port(self):
    if "websocket_port" in self.__config:
      return (str(self.__config['websocket_port']))
    else:
      return ""

  def get_janus_rtp_port_range(self):
    if "rtp_port_range" in self.__config:
      return (str(self.__config['rtp_port_range']))
    else:
      return ""

  def get_janus_enable_nat_1_to_1_mapping(self):
    if "enable_nat_1_to_1_mapping" in self.__config:
      return (int(self.__config['enable_nat_1_to_1_mapping']))
    else:
      return -1

  def get_janus_public_ip(self):
    if "public_ip" in self.__config:
      return (str(self.__config['public_ip']))
    else:
      return ""

  def get_janus_admin_http_port(self):
      if "admin_http_port" in self.__config:
        return (int(self.__config['admin_http_port']))
      else:
        return -1

  def get_janus_admin_websocket_port(self):
      if "admin_websocket_port" in self.__config:
        return (int(self.__config['admin_websocket_port']))
      else:
        return -1
###############################################################################
# TEST SECTION
###############################################################################

def test ():
  p = ConfigParser ()

  config_file_name = "config_manager/default_config.ini"
  if p.parse(config_file_name):
    print(p.get_doordarshan_enable())
    print(p.get_device_id())
  else:
    print("parse failed for %s"%(config_file_name))

if __name__ == '__main__':
  test ()
