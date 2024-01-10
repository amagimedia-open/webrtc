""" Tests for NDISwitcherUpdater
--

"""

import socket
import unittest
from concurrent import futures
from contextlib import closing

import grpc

import ndi_switcher_pb2_grpc

from ndiSwitcherConfigUpdater import (
    NDISwitcherUpdater,
    NDISwitcherUpdaterErrorCode
    )

from ndi_switcher_grpc import NDISwitcherGrpc

class DummyNDISwitcher:
    """ Dummy NDI Switcher class
    """
    def __init__(self):
        pass

    def get_helper_obj(self):
        return self

    def get_source_len(self):
        return 4

    def get_dynamic_configuration_status(self, stream_id):
        return 0

    def set_dynamic_configuration_status(self, stream_id, status):
        pass

    def configure_input_stream(self, params):
        return True, ""

class DummyTardis:
    """ Dummy Tardis class
    """
    def __init__(self):
        self._ndi_switcher = DummyNDISwitcher()

    def get_current_sub_process(self):
        return self._ndi_switcher

class NDISwitcherUpdaterTest(unittest.TestCase):
    """ Test cases for NDISwitcherUpdater
    """
    def get_tapp_obj(self):
        return self._tapp_obj

    def _get_free_port(self):
        with closing(socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)) as s:
            s.bind(('127.0.0.1', 0))
            _, port = s.getsockname()
        return port

    def setUp(self):
        self._tapp_obj = DummyTardis()
        self._grpc_port = self._get_free_port()
        self._grpc_url = f'[::]:{self._grpc_port}'

        self._grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        ndi_switcher_pb2_grpc.add_NDISwitcherServicer_to_server(
            NDISwitcherGrpc(self),
            self._grpc_server
        )
        self._grpc_server.add_insecure_port(self._grpc_url)
        self._grpc_server.start()

    def tearDown(self):
        self._grpc_server.stop(None)

    def test_1(self):
        """ Mismatch in the access IP list length
        """
        ndi_switcher_updater = NDISwitcherUpdater()

        current_cfg_dict = {
            'ndi_switcher': {
                'ndi_switcher_access_ip_list': 'localhost'
            }
        }

        new_cfg_dict = {
            'ndi_switcher': {
                'ndi_switcher_access_ip_list': 'localhost,localhost'
            }
        }

        error_code, stream_id_list = \
            ndi_switcher_updater.get_config_updated_stream_id(current_cfg_dict, new_cfg_dict)

        assert error_code == NDISwitcherUpdaterErrorCode.CONFIG_ERROR
        assert stream_id_list == []

    def test_2(self):
        """ No input configs changes
        """
        ndi_switcher_updater = NDISwitcherUpdater()

        current_cfg_dict = {
            'ndi_switcher': {
                'ndi_switcher_access_ip_list': 'localhost,localhost'
            }
        }

        new_cfg_dict = {
            'ndi_switcher': {
                'ndi_switcher_access_ip_list': 'localhost,localhost'
            }
        }

        error_code, stream_id_list = \
            ndi_switcher_updater.get_config_updated_stream_id(current_cfg_dict, new_cfg_dict)
        assert error_code == NDISwitcherUpdaterErrorCode.NO_INPUT_STREAM_CONFIG_UPDATE
        assert stream_id_list == []

    def test_3(self):
        """ input stream 2 configs changes
        """
        ndi_switcher_updater = NDISwitcherUpdater()

        current_cfg_dict = {
            'ndi_switcher': {
                'ndi_switcher_access_ip_list': 'localhost,localhost'
            }
        }

        new_cfg_dict = {
            'ndi_switcher': {
                'ndi_switcher_access_ip_list': 'localhost,playerhost'
            }
        }

        error_code, stream_id_list = \
            ndi_switcher_updater.get_config_updated_stream_id(current_cfg_dict, new_cfg_dict)
        assert error_code == NDISwitcherUpdaterErrorCode.CHANGE_IN_CONFIG_DETECTED
        assert stream_id_list == [2]

    def test_4(self):
        """ input stream 1 configs changes
        """
        ndi_switcher_updater = NDISwitcherUpdater()

        current_cfg_dict = {
            'ndi_switcher': {
                'ndi_switcher_access_ip_list': 'localhost,localhost'
            }
        }

        new_cfg_dict = {
            'ndi_switcher': {
                'ndi_switcher_access_ip_list': 'playerhost,localhost'
            }
        }

        error_code, stream_id_list = \
            ndi_switcher_updater.get_config_updated_stream_id(current_cfg_dict, new_cfg_dict)
        assert error_code == NDISwitcherUpdaterErrorCode.CHANGE_IN_CONFIG_DETECTED
        assert stream_id_list == [1]

    def test_5(self):
        """ input stream 1 and 2 configs changes
        """
        ndi_switcher_updater = NDISwitcherUpdater()

        current_cfg_dict = {
            'ndi_switcher': {
                'ndi_switcher_access_ip_list': 'localhost,localhost'
            }
        }

        new_cfg_dict = {
            'ndi_switcher': {
                'ndi_switcher_access_ip_list': 'playerhost,playerhost'
            }
        }

        error_code, stream_id_list = \
            ndi_switcher_updater.get_config_updated_stream_id(current_cfg_dict, new_cfg_dict)
        assert error_code == NDISwitcherUpdaterErrorCode.CHANGE_IN_CONFIG_DETECTED
        assert stream_id_list == [1, 2]

    def test_6(self):
        """ Get configs details
        Error case where hostname and stream name are different length
        """
        ndi_switcher_updater = NDISwitcherUpdater()

        cfg_dict = {
            'ndi_switcher': {
                'ndi_switcher_in_hostname': 'TEST_1,TEST_2',
                'ndi_switcher_in_streamname': 'stream_1',
                'ndi_switcher_access_ip_list': 'localhost,localhost'
            }
        }

        stream_id_list = [1]

        error_code, stream_info_list  = \
            ndi_switcher_updater.get_streams_configs(stream_id_list, cfg_dict)

        assert error_code == NDISwitcherUpdaterErrorCode.CONFIG_ERROR
        assert stream_info_list == []

    def test_7(self):
        """ Get configs details of stream 1
        """
        ndi_switcher_updater = NDISwitcherUpdater()

        cfg_dict = {
            'ndi_switcher': {
                'ndi_switcher_in_hostname': 'TEST_1,TEST_2',
                'ndi_switcher_in_streamname': 'stream_1,stream_2',
                'ndi_switcher_access_ip_list': 'localhost,localhost'
            }
        }

        stream_id_list = [1]

        output = [
            {
                'stream_id': 0,
                'hostname': 'TEST_1',
                'stream_name': 'stream_1',
                'access_ip': 'localhost'
            }
        ]

        error_code, stream_info_list  = \
            ndi_switcher_updater.get_streams_configs(stream_id_list, cfg_dict)

        assert error_code == NDISwitcherUpdaterErrorCode.OK
        assert stream_info_list == output

    def test_8(self):
        """ Get configs details of stream 2
        """
        ndi_switcher_updater = NDISwitcherUpdater()

        cfg_dict = {
            'ndi_switcher': {
                'ndi_switcher_in_hostname': 'TEST_1,TEST_2',
                'ndi_switcher_in_streamname': 'stream_1,stream_2',
                'ndi_switcher_access_ip_list': 'localhost,localhost'
            }
        }

        stream_id_list = [2]

        output = [
            {
                'stream_id': 1,
                'hostname': 'TEST_2',
                'stream_name': 'stream_2',
                'access_ip': 'localhost'
            }
        ]

        error_code, stream_info_list  = \
            ndi_switcher_updater.get_streams_configs(stream_id_list, cfg_dict)

        assert error_code == NDISwitcherUpdaterErrorCode.OK
        assert stream_info_list == output

    def test_9(self):
        """ Get configs details of stream 1 and 2
        """
        ndi_switcher_updater = NDISwitcherUpdater()

        cfg_dict = {
            'ndi_switcher': {
                'ndi_switcher_in_hostname': 'TEST_1,TEST_2',
                'ndi_switcher_in_streamname': 'stream_1,stream_2',
                'ndi_switcher_access_ip_list': 'localhost,localhost'
            }
        }

        stream_id_list = [1, 2]

        output = [
            {
                'stream_id': 0,
                'hostname': 'TEST_1',
                'stream_name': 'stream_1',
                'access_ip': 'localhost'
            },
            {
                'stream_id': 1,
                'hostname': 'TEST_2',
                'stream_name': 'stream_2',
                'access_ip': 'localhost'
            }
        ]

        error_code, stream_info_list  = \
            ndi_switcher_updater.get_streams_configs(stream_id_list, cfg_dict)

        assert error_code == NDISwitcherUpdaterErrorCode.OK
        assert stream_info_list == output

    def test_10(self):
        """ Get configs details with mismatch in hostname and access ip
        """
        ndi_switcher_updater = NDISwitcherUpdater()

        cfg_dict = {
            'ndi_switcher': {
                'ndi_switcher_in_hostname': 'TEST_1,TEST_2',
                'ndi_switcher_in_streamname': 'stream_1,stream_2',
                'ndi_switcher_access_ip_list': 'localhost'
            }
        }

        stream_id_list = [1, 2]

        output = [
            {
                'stream_id': 0,
                'hostname': 'TEST_1',
                'stream_name': 'stream_1',
                'access_ip': 'localhost'
            },
            {
                'stream_id': 1,
                'hostname': 'TEST_2',
                'stream_name': 'stream_2',
                'access_ip': 'localhost'
            }
        ]

        error_code, stream_info_list  = \
            ndi_switcher_updater.get_streams_configs(stream_id_list, cfg_dict)

        assert error_code == NDISwitcherUpdaterErrorCode.OK
        assert stream_info_list == output

    def test_11(self):
        """ Get configs details with no access ip
        """
        ndi_switcher_updater = NDISwitcherUpdater()

        cfg_dict = {
            'ndi_switcher': {
                'ndi_switcher_in_hostname': 'TEST_1,TEST_2',
                'ndi_switcher_in_streamname': 'stream_1,stream_2',
                'ndi_switcher_access_ip_list': ''
            }
        }

        stream_id_list = [1, 2]

        output = []

        error_code, stream_info_list  = \
            ndi_switcher_updater.get_streams_configs(stream_id_list, cfg_dict)

        assert error_code == NDISwitcherUpdaterErrorCode.CONFIG_ERROR
        assert stream_info_list == output

    def test_12(self):
        """ Get configs details with wrong stream id
        """
        ndi_switcher_updater = NDISwitcherUpdater()

        cfg_dict = {
            'ndi_switcher': {
                'ndi_switcher_in_hostname': 'TEST_1,TEST_2',
                'ndi_switcher_in_streamname': 'stream_1,stream_2',
                'ndi_switcher_access_ip_list': 'localhost'
            }
        }

        stream_id_list = [3]

        output = []

        error_code, stream_info_list  = \
            ndi_switcher_updater.get_streams_configs(stream_id_list, cfg_dict)

        assert error_code == NDISwitcherUpdaterErrorCode.CONFIG_ERROR
        assert stream_info_list == output

    def test_13(self):
        """ Configure input stream, success case
        """
        ndi_switcher_updater = NDISwitcherUpdater()

        stream_info_list = [
            {
                'stream_id': 0,
                'hostname': 'TEST_1',
                'stream_name': 'stream_1',
                'access_ip': 'localhost'
            }
        ]

        common_params = {
            'grpc_server_port': str(self._grpc_port)
        }

        output = [(0, NDISwitcherUpdaterErrorCode.OK)]

        ret = ndi_switcher_updater.configure_input(stream_info_list, common_params)

        assert ret == output

    def test_14(self):
        """ Configure input stream, error in stream id
        """
        ndi_switcher_updater = NDISwitcherUpdater()

        stream_info_list = [
            {
                'stream_id': 4,
                'hostname': 'TEST_1',
                'stream_name': 'stream_1',
                'access_ip': 'localhost'
            }
        ]

        common_params = {
            'grpc_server_port': str(self._grpc_port)
        }

        output = [(4, NDISwitcherUpdaterErrorCode.STREAM_CONFIGURATION_FAILED)]

        ret = ndi_switcher_updater.configure_input(stream_info_list, common_params)

        # TODO: Fix in NDI Switcher gRPC
        # configure input stream should fail for stream id equal to num of streams
        # as stream id start with 0

        assert ret == output

    def test_15(self):
        """ Configure input stream, error in some configuration
        """
        ndi_switcher_updater = NDISwitcherUpdater()

        stream_info_list = [
            {
                'stream_id': 0,
                'hostname': 'TEST_1',
                'stream_name': 'stream_1',
                'access_ip': 'localhost'
            },
            {
                'stream_id': 5,
                'hostname': 'TEST_1',
                'stream_name': 'stream_1',
                'access_ip': 'localhost'
            }
        ]

        common_params = {
            'grpc_server_port': str(self._grpc_port)
        }

        output = [
            (0, NDISwitcherUpdaterErrorCode.OK),
            (5, NDISwitcherUpdaterErrorCode.STREAM_CONFIGURATION_FAILED)
        ]

        ret = ndi_switcher_updater.configure_input(stream_info_list, common_params)

        assert ret == output

if __name__ == '__main__':
    unittest.main()
