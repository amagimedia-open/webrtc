import sys
import os
import pkg_resources
from jinja2 import Template

def patch_janus_config_file(input_file, output_file, args):
    script_dir = os.path.dirname(__file__) #absolute dir the script is in
    abs_input_file_path = os.path.join(script_dir, input_file)
    with open(abs_input_file_path, mode='r') as inp_f:
        inp_f_str = inp_f.read()
    tm = Template(inp_f_str)
    msg = tm.render(args=args)
    with open(output_file, 'w') as op_f:
        op_f.write(msg+"\n")

def patch_janus_main_conf(cfg_dict):
    args = {}
    input_file = "../templates/janus.jcfg.template"
    output_file = "/opt/etc/janus/janus.jcfg"

    args["debug_level"] = "5"
    args["rtp_port_range"] = "\"%s\""%cfg_dict["rtp_port_range"]
    if cfg_dict["enable_nat_1_to_1_mapping"] == 1:
        args["enable_nat_1_to_1_mapping"] = 1
        args["nat_1_1_mapping"] = "\"%s\""%cfg_dict["public_ip"]
    else:
        args["enable_nat_1_to_1_mapping"] = 0
    if cfg_dict["stun_enable"] == 1:
        args["stun_enable"] = cfg_dict["stun_enable"]
        args["stun_server"] = "\"%s\""%cfg_dict["stun_server"]
        args["stun_port"] = cfg_dict["stun_port"]
        args["nice_debug"] = "false"
        args["full_trickle"] = "true"
        args["ice_interface"] = "\"%s\""%cfg_dict["ice_interface"]
    else:
        args["stun_enable"] = 0
    if cfg_dict["turn_enable"] == 1:
        args["turn_enable"] = cfg_dict["turn_enable"]
        args["turn_server"] = "\"%s\""%cfg_dict["turn_server"]
        args["turn_port"] = cfg_dict["turn_port"]
        args["turn_type"] = "\"udp\""
        args["turn_user"] = "\"%s\""%cfg_dict["turn_username"]
        args["turn_pwd"] = "\"%s\""%cfg_dict["turn_password"]
    else:
        args["turn_enable"] = 0

    patch_janus_config_file(input_file, output_file, args)

def patch_janus_plugin_streaming_conf(cfg_dict):
    args = {}
    input_file = "../templates/janus.plugin.streaming.jcfg.template"
    output_file = "/opt/etc/janus/janus.plugin.streaming.jcfg"
    args["type"] = "\"rtp\""
    args["id"] = 1
    args["description"] = "\"Opus/H264 live stream coming from gstreamer\""
    args["audio"] = "true"
    args["video"] = "true"
    args["audioport"] = cfg_dict["audioport"]
    args["audiopt"] = 111
    args["audiortpmap"] = "\"opus/48000/2\""
    args["videoport"] = cfg_dict["videoport"]
    args["videopt"] = 126
    args["videortpmap"] = "\"H264/90000\""
    patch_janus_config_file(input_file, output_file, args)

def patch_janus_transport_http_conf(cfg_dict):
    args = {}
    input_file = "../templates/janus.transport.http.jcfg.template"
    output_file = "/opt/etc/janus/janus.transport.http.jcfg"
    args["http"] = "true"
    args["http_port"] = cfg_dict["http_port"]
    args["admin_http_port"] = cfg_dict["admin_http_port"]
    patch_janus_config_file(input_file, output_file, args)

def patch_janus_transport_websockets_conf(cfg_dict):
    args = {}
    input_file = "../templates/janus.transport.websockets.jcfg.template"
    output_file = "/opt/etc/janus/janus.transport.websockets.jcfg"
    args["ws"] = "true"
    args["ws_port"] = cfg_dict["websocket_port"]
    args["admin_ws_port"] = cfg_dict["admin_websocket_port"]
    patch_janus_config_file(input_file, output_file, args)

def patch_janus_conf(cfg_dict):
    patch_janus_main_conf(cfg_dict)
    patch_janus_plugin_streaming_conf(cfg_dict)
    patch_janus_transport_http_conf(cfg_dict)
    patch_janus_transport_websockets_conf(cfg_dict)
