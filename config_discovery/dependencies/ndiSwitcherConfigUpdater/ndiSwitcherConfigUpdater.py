""" NDI Switcher configs updater.
Check for configs update
"""

import traceback
from enum import Enum

import grpc

import ndi_switcher_pb2
import ndi_switcher_pb2_grpc

class NDISwitcherUpdaterErrorCode(Enum):
    """ Error codes for NDI Switcher updater
    """
    OK                               = 0
    CONFIG_ERROR                     = 1
    NO_INPUT_STREAM_CONFIG_UPDATE    = 2
    PARTIAL_INPUT_STREAM_CONFIG_INFO = 3
    REQUEST_GENERATION_FAILED        = 4
    STREAM_CONFIG_VALIDATION_FAILED  = 5
    STREAM_CONFIGURATION_TIMEOUT     = 6
    STREAM_CONFIGURATION_FAILED      = 7
    UNHANDLED_ERROR                  = 8
    CHANGE_IN_CONFIG_DETECTED        = 9

    @staticmethod
    def description(code):
        """ Returns description of the error code
        """
        if code == NDISwitcherUpdaterErrorCode.OK:
            ret = "Success"
        elif code == NDISwitcherUpdaterErrorCode.CONFIG_ERROR:
            ret = "Error in the input configs"
        elif code == NDISwitcherUpdaterErrorCode.NO_INPUT_STREAM_CONFIG_UPDATE:
            ret = "Input stream configs are not updated"
        elif code == NDISwitcherUpdaterErrorCode.PARTIAL_INPUT_STREAM_CONFIG_INFO:
            ret = "Partial input stream configs returned"
        elif code == NDISwitcherUpdaterErrorCode.REQUEST_GENERATION_FAILED:
            ret = "Failed to generate request"
        elif code == NDISwitcherUpdaterErrorCode.STREAM_CONFIG_VALIDATION_FAILED:
            ret = "Input stream config validation failed"
        elif code == NDISwitcherUpdaterErrorCode.STREAM_CONFIGURATION_TIMEOUT:
            ret = "Input stream configuration timed out"
        elif code == NDISwitcherUpdaterErrorCode.STREAM_CONFIGURATION_FAILED:
            ret = "Input stream configuration failed"
        elif code == NDISwitcherUpdaterErrorCode.UNHANDLED_ERROR:
            ret = "Unhandled error"
        elif code == NDISwitcherUpdaterErrorCode.PARTIAL_INPUT_STREAM_CONFIG_INFO:
            ret = "Input stream configuration failed for some streams"
        elif code == NDISwitcherUpdaterErrorCode.CHANGE_IN_CONFIG_DETECTED:
            ret = "Input stream configs updated"
        else:
            ret = f"Unknown error code, error_code: {code}"

        return ret

class DummyLogger:
    """ Dummy logger module.
    """
    def info(self, msg):
        """ Log info message
        """
        print(f'INFO - {msg}')

    def warn(self, msg):
        """ Log warn message
        """
        print(f'WARN - {msg}')

    def error(self, msg):
        """ Log error message
        """
        print(f'ERROR - {msg}')

    def debug(self, msg):
        """ Log debug message
        """
        print(f'DEBUG - {msg}')

class NDISwitcherUpdater:
    """ Update the configs of NDI Switcher.
    """
    def __init__(self, logger=None):
        if logger:
            self._logger = logger
        else:
            self._logger = DummyLogger()

    def _get_config_value(self, cfg_dict, section, option):
        """ Returns the value of option in configs.
        - Args:
            - cfg_dict: NDI Switcher configs in dict
            - section: Name of the section
            - option: Name of the config
        - Return:
            - Value of the option requested (string)
        """
        try:
            value = cfg_dict.get(
                section, {}).get(
                option, ''
                )
        except Exception as err:
            self._logger.error(f"Failed to get option ({option}) in " \
                               f"section ({section}) from configs."\
                               f"cfg_dict: {cfg_dict}, error: {err}")
            value = ''

        return value

    def _get_access_ip_list(self, cfg_dict):
        """ Returns the list of access ip of NDI Senders to connect.
        - Args:
            - cfg_dict: NDI Switcher configs in dict
        - Returns:
            - List of access IPs of NDI Senders
        """
        access_ip = self._get_config_value(
                        cfg_dict,
                        'ndi_switcher',
                        'ndi_switcher_access_ip_list'
                        )

        return access_ip.split(',') if access_ip else []

    def _get_hostname_list(self, cfg_dict):
        """ Returns the list of hostname of NDI Senders to connect.
        - Args:
            - cfg_dict: NDI Switcher configs in dict
        - Returns:
            - List of hostname of NDI Senders
        """
        hostname = self._get_config_value(
                        cfg_dict,
                        'ndi_switcher',
                        'ndi_switcher_in_hostname'
                        )

        return hostname.split(',') if hostname else []

    def _get_streamname_list(self, cfg_dict):
        """ Returns the list of stream name of NDI Senders to connect.
        - Args:
            - cfg_dict: NDI Switcher configs in dict
        - Returns:
            - List of stream name of NDI Senders
        """
        stream_name = self._get_config_value(
                            cfg_dict,
                            'ndi_switcher',
                            'ndi_switcher_in_streamname'
                            )

        return stream_name.split(',') if stream_name else []

    def _validate_input_stream_configs(self, cfg_dict):
        """ Validate input stream configs
        - Args:
            - cfg_dict: Input stream configs
        - Returns:
            - True (if valid) / False (not valid)
        """
        configs_needed = [
            'stream_id',
            'hostname',
            'stream_name',
            'access_ip'
        ]

        for cfg in configs_needed:
            if cfg not in cfg_dict:
                return False

        return True

    def _generate_configure_input_stream_request(self, cfg_dict):
        """ Generated configure input stream gRPC request.
        - Args:
            - cfg_dict: Input stream configs.
        - Returns:
            - Error code.
        """
        try:
            access_ip_str = cfg_dict.get('access_ip', '')

            if access_ip_str:
                access_ip_list = access_ip_str.split(',')
            else:
                access_ip_list = []

            access_ip = \
                ndi_switcher_pb2.ConfigureInputStreamRequest.DiscoveryModemDNSConfigs(
                    access_ip_list = access_ip_list
                )

            request = ndi_switcher_pb2.ConfigureInputStreamRequest(
                stream_id = int(cfg_dict.get('stream_id', -1)),
                hostname = str(cfg_dict.get('hostname', '')),
                stream_name = str(cfg_dict.get('stream_name', '')),
                mdns_configs = access_ip
            )
        except Exception as err:
            self._logger.error(f"Failed to generate request. " \
                               f"cfg_dict: {cfg_dict}, err: {err}")
            request = None

        return request

    def _get_tardis_grpc_server_url(self, grpc_port):
        """ Generates Tardis gRPC Server URL.
        - Args:
            - grpc_port: Tardis gRPC port
        - Returns:
            - gRPC URL for tardis
        """
        if grpc_port == -1:
            self._logger.error(f"Invalid gRPC port. port: {grpc_port}")
            return ''

        return f'localhost:{grpc_port}'

    def _send_configure_input_request(self, grpc_server_url, cfg_dict):
        """ Send a gRPC request to configure input stream
        - Args:
            - grpc_server_url: URL of NDI Switcher gRPC server
            - cfg_dict: NDI Switcher stream configs
        - Returns:
            - Error code
        """
        with grpc.insecure_channel(grpc_server_url) as channel:
            stub = ndi_switcher_pb2_grpc.NDISwitcherStub(channel)

            request = self._generate_configure_input_stream_request(cfg_dict)

            ret_code = NDISwitcherUpdaterErrorCode.OK
            if request:
                try:
                    response = stub.ConfigureInputStream(
                        request,
                        timeout = 10
                    )
                except grpc.RpcError as err:
                    self._logger.error(f"Error in sending the request. " \
                                       f"error: {err.code()}, msg: {err.details()}")
                    if err.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
                        ret_code = NDISwitcherUpdaterErrorCode.STREAM_CONFIGURATION_TIMEOUT
                    else:
                        ret_code = NDISwitcherUpdaterErrorCode.STREAM_CONFIGURATION_FAILED
            else:
                self._logger.error(f"Failed to generate request with provided " \
                                   f"configs. cfg_dict: {cfg_dict}")
                ret_code = NDISwitcherUpdaterErrorCode.REQUEST_GENERATION_FAILED

            if ret_code == NDISwitcherUpdaterErrorCode.OK:
                res_msg = response.WhichOneof('ConfigureInputStreamResponseMessages')
                if res_msg == 'error_response':
                    ret_code = NDISwitcherUpdaterErrorCode.STREAM_CONFIGURATION_FAILED

            return ret_code

    def _configure_input_stream(self, cfg_dict, common_params):
        """ configure input stream
        - Args:
            - cfg_dict: Input stream configs
        - Returns:
            - Error code.
        """

        if not self._validate_input_stream_configs(cfg_dict):
            return NDISwitcherUpdaterErrorCode.STREAM_CONFIG_VALIDATION_FAILED

        grpc_port = common_params.get('grpc_server_port', -1)
        grpc_server = self._get_tardis_grpc_server_url(grpc_port)

        if not grpc_server:
            return NDISwitcherUpdaterErrorCode.CONFIG_ERROR

        try:
            ret_code = self._send_configure_input_request(grpc_server, cfg_dict)
        except Exception as _:
            self._logger.error(traceback.format_exc().replace("\n"," "))
            ret_code = NDISwitcherUpdaterErrorCode.UNHANDLED_ERROR

        return ret_code

    def get_config_updated_stream_id(self, current_cfg_dict, new_cfg_dict):
        """ Returns stream IDs of updated configs.
            Below configs will be checked to decide configs updated:
                access IP of input stream

        - Args:
            - cfg_dict: Configs dict
        - Return:
            - Error code and list of stream ID whose configs are changed.
        """
        current_access_ip_list = self._get_access_ip_list(current_cfg_dict)
        new_access_ip_list = self._get_access_ip_list(new_cfg_dict)

        if len(current_access_ip_list) != len(new_access_ip_list):
            self._logger.error(f"Mismatch in access ip list length in " \
                               f"current and old configs. " \
                               f"current_access_ip_list: {current_access_ip_list}" \
                               f"new_access_ip_list: {new_access_ip_list}")
            return NDISwitcherUpdaterErrorCode.CONFIG_ERROR, []

        updated_streams_list = []
        for stream_id, (current_access_ip, new_access_ip) in enumerate(zip( \
                                                    current_access_ip_list, \
                                                    new_access_ip_list), start=1):
            if current_access_ip != new_access_ip:
                updated_streams_list.append(stream_id)

        if updated_streams_list:
            err_code = NDISwitcherUpdaterErrorCode.CHANGE_IN_CONFIG_DETECTED
        else:
            err_code = NDISwitcherUpdaterErrorCode.NO_INPUT_STREAM_CONFIG_UPDATE

        return err_code, updated_streams_list

    def get_streams_configs(self, stream_id_list, cfg_dict):
        """ Returns the input stream configs.
        - Args:
            - stream_id_list: List of stream IDs for which configs are needed
            - cfg_dict: NDI Switcher configs in dict
        - Returns:
            - Error Code
            - List of input stream configs
        """
        hostname_list = self._get_hostname_list(cfg_dict)
        streamname_list = self._get_streamname_list(cfg_dict)

        if len(hostname_list) != len(streamname_list):
            error = "hostname's and stream name's length are different"
            self._logger.error(f"Error in configuration, error: {error}, " \
                               f"hostname_list: {hostname_list}, " \
                               f"streamname_list: {streamname_list}")

            return NDISwitcherUpdaterErrorCode.CONFIG_ERROR, []

        num_streams = len(hostname_list)
        access_ip_list = self._get_access_ip_list(cfg_dict)

        if len(access_ip_list) == 0:
            error = "Atleast one access IP should be configured"
            self._logger.error(f"Error in configuration, error: {error}, " \
                               f"access_ip_list: {access_ip_list}")
            return NDISwitcherUpdaterErrorCode.CONFIG_ERROR, []

        if len(access_ip_list) > num_streams:
            access_ip_list = access_ip_list[:num_streams]
        elif len(access_ip_list) < num_streams:
            extra_values = [access_ip_list[-1]] * (num_streams-len(access_ip_list))
            access_ip_list = access_ip_list + extra_values

        stream_cfg_list = []
        for stream_id in stream_id_list:
            if stream_id <= num_streams:
                conv_stream_id = stream_id - 1
                stream_cfg_list.append({
                    'stream_id': conv_stream_id,
                    'hostname': hostname_list[conv_stream_id],
                    'stream_name': streamname_list[conv_stream_id],
                    'access_ip': access_ip_list[conv_stream_id]
                })
            else:
                self._logger.error(f"Configs for stream ID {stream_id}" \
                                   f" is not found, "\
                                   f"num_streams: {num_streams}, " \
                                   f"hostname_list: {hostname_list}, " \
                                   f"streamname_list: {streamname_list}, " \
                                   f"access_ip_list: {access_ip_list}")

        if len(stream_cfg_list) == 0:
            code = NDISwitcherUpdaterErrorCode.CONFIG_ERROR
        elif len(stream_cfg_list) < len(stream_id_list):
            code = NDISwitcherUpdaterErrorCode.PARTIAL_INPUT_STREAM_CONFIG_INFO
        else:
            code = NDISwitcherUpdaterErrorCode.OK

        return code, stream_cfg_list

    def configure_input(self, stream_info_list, common_params):
        """ Configure input stream.
        - Args:
            - stream_info_list: List of stream info that needs to be updated.
            - common_params: Tardis common configurations.
        - Return:
            - List of stream ID and error code.
        """
        ret_list = []
        for stream_info in stream_info_list:
            ret = self._configure_input_stream(stream_info, common_params)
            ret_list.append((stream_info.get('stream_id', -1), ret))

        return ret_list
