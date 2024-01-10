#!/usr/bin/python3

import os
import time
import hashlib
import subprocess

from config_discovery.configDiscoveryLogger import configDiscoveryLogger
from config_discovery.utils import *
from config_discovery.discoverConfigs import *
from config_discovery.utils import pullFromConfigFileStore
from config_discovery.dependencies.ndiSwitcherConfigUpdater.ndiSwitcherConfigUpdater import (
    NDISwitcherUpdater,
    NDISwitcherUpdaterErrorCode
)

CHECK_CONFIG_CHANGE_INTERVAL = 1
MAX_RETRY_COUNT = 3
CHECK_CONFIG_CHANGE_INTERVAL_NDI_SWITCHER = 5

logger = configDiscoveryLogger("tardis")

def monitorConfigChange(key, curMd5Sum) -> (str, bool):
    md5key = f"{key}_MD5SUM"
    md5File = getTempFile("md5val_", "/tmp")
    if not md5File:
        logger.error("Failed to create temp file to download md5 value")
        return (None, False)

    if not pullFromConfigFileStore(md5key, md5File):
        logger.error(f"Failed to fetch {md5key} from config store. Check sdc version")
        os.remove(md5File)
        return (None, False)

    with open(md5File, "r") as fh:
        newMd5Sum = fh.read().rstrip()

    os.remove(md5File)
    if (curMd5Sum):
        if (curMd5Sum != newMd5Sum):
            return (newMd5Sum, True)
    # First time
    return (newMd5Sum, False)

def tardisConfigWatcher(orkyMode:str, key:str) -> None:
    """ Checks for tardis configs in config store.
    - Args:
        - key: Name of the configs key
    - Returns:
        - None
    """
    curMd5Sum = None
    while True:
        (newMd5Sum, md5SumChanged) = monitorConfigChange(key, curMd5Sum)

        if (md5SumChanged):
            logger.info(f"Configs Changed....current md5sum {curMd5Sum} new md5sum {newMd5Sum} reconfiguring the tardis")
            ret = discoverConfigs(orkyMode)
            if not ret:
                logger.error("Config discovery Failed")
            else:
                logger.info("Reconfigure successful. Restarting tardis_app.service")
                retryCount = 0
                while retryCount <= MAX_RETRY_COUNT:
                    cmd = "systemctl restart tardis_app"
                    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    output, error = p.communicate()
                    if str(p.returncode) != "0":
                        logger.error(f"Restarting tardis service failed with error {error.decode()}")
                        retryCount += 1
                    else:
                        break
                    time.sleep(1)

        curMd5Sum = newMd5Sum
        time.sleep(CHECK_CONFIG_CHANGE_INTERVAL)

def getCurrentNDISwitcherConfigs():
    """ Returns the current NDI Switcher configs.
    - Args:
        - None
    - Returns:
        - NDI Switcher configs dict
    """
    tardisCfgFile = os.environ.get('CONFIG_FILE')
    if tardisCfgFile is None:
        logger.error('Falied to get tardis configs file.')
        return {}

    fullCurrentCfg = parseINIFile(tardisCfgFile)
    if not fullCurrentCfg:
        logger.error (f'Failed to parse INI file : {tardisCfgFile}')
        return {}

    currentCfg = {
        'common_params': fullCurrentCfg.get('common_params', {}),
        'ndi_switcher': fullCurrentCfg.get('ndi_switcher', {})
    }

    return currentCfg

def getNewTardisConfigs(key:str) -> dict:
    """ Returns new or patch Tardis configs.
    - Args:
        - key: Name of the configs key
    - Returns:
        - Tardis configs to patch
    """
    patchCfgFile = getTempFile('discoveryConfigs_patchCfg_', '/tmp')
    if not patchCfgFile:
        logger.error("Failed to create temp file to download patch config file")
        return {}

    if not pullFromConfigFileStore (key, patchCfgFile):
        logger.error(f"Failed to pull the config from file store, key: {key}")
        os.remove(patchCfgFile)
        return {}

    patchCfg = parseINIFile (patchCfgFile)
    if not patchCfg:
        logger.error (f'Failed to parse INI file : {patchCfgFile}')
        os.remove(patchCfgFile)
        return {}
    os.remove(patchCfgFile)

    return patchCfg

def updateNDISwitcherConfigs(orkyMode:str, key:str, currentCfg:dict, patchCfg:dict) -> bool:
    """ Update the NDI Switcher configs.
    - Args:
        - key: Name of the configs key
        - currentCfg: Current running NDI Switcher configs.
        - patchCfg: New configs to patch
    - Returns:
        - True (on successful config update) / False (on failure)
    """
    retValue = False

    ndiSwitcherUpdater = NDISwitcherUpdater(logger)

    retCode, streamIDList = ndiSwitcherUpdater.get_config_updated_stream_id(
                    currentCfg,
                    patchCfg
                    )

    if retCode == NDISwitcherUpdaterErrorCode.CHANGE_IN_CONFIG_DETECTED:
        retCode, streamInfoList = ndiSwitcherUpdater.get_streams_configs(
                                        streamIDList,
                                        patchCfg
                                        )

        expected_error_codes = [
            NDISwitcherUpdaterErrorCode.OK,
            NDISwitcherUpdaterErrorCode.PARTIAL_INPUT_STREAM_CONFIG_INFO
        ]

        if retCode in expected_error_codes:
            logger.info(f"Configure NDI Switcher, configs: {streamInfoList}")

            retCodeList = ndiSwitcherUpdater.configure_input(
                                        streamInfoList,
                                        patchCfg.get('common_params', {})
                                        )

            retValue = True
            for (streamID, errorCode) in retCodeList:
                logger.info(f"Configs update status, streamID: {streamID}, " \
                            f"ret: {NDISwitcherUpdaterErrorCode.description(errorCode)}")
                # If all the configuration is not done, there will be retry
                # until it is configured.
                if errorCode != NDISwitcherUpdaterErrorCode.OK:
                    retValue = False

            ret = discoverConfigs(orkyMode)
            if not ret:
                logger.error("Config file patch failed")
            else:
                logger.info("Config file patch successful")

    elif retCode == NDISwitcherUpdaterErrorCode.NO_INPUT_STREAM_CONFIG_UPDATE:
        # No input configs update.
        logger.info("Input streams not updated.")
        retValue = True
    elif retCode == NDISwitcherUpdaterErrorCode.CONFIG_ERROR:
        # Error in configs
        # No point in retrying configuration until
        # configs are updated again.
        logger.info(f"Error in configs. currentCfg: {currentCfg},"\
                    f"patchCfg: {patchCfg}")
        retValue = True
    else:
        logger.error(f"Failed to check config update. key: {key}, " \
                     f"currentCfg: {currentCfg}, patchCfg: {patchCfg}, "\
                     f"error: {NDISwitcherUpdaterErrorCode.description(retCode)}")
        retValue = False

    return retValue

def ndiSwitcherConfigWatcher(orkyMode:str, key:str) -> None:
    """ Checks for NDI Switcher configs in config store.
    - Args:
        - key: Name of the configs key
    - Returns:
        - None
    """
    curMd5Sum = None
    while True:
        (newMd5Sum, md5SumChanged) = monitorConfigChange(key, curMd5Sum)

        if md5SumChanged:
            logger.info(f"Configs Changed....current md5sum {curMd5Sum} new " \
                f"md5sum {newMd5Sum} reconfiguring the tardis")

            patchCfg = getNewTardisConfigs(key)
            if patchCfg:
                currentCfg = getCurrentNDISwitcherConfigs()
                if currentCfg:
                    ret = updateNDISwitcherConfigs(
                            orkyMode,
                            key,
                            currentCfg,
                            patchCfg
                            )
                    if ret:
                        logger.info("Successfully updated the configs.")
                        curMd5Sum = newMd5Sum
                    else:
                        logger.error("Failed to update the configs")
                else:
                    logger.error("Failed to get current NDI Switcher configs.")
            else:
                logger.error("Failed to get patch or new NDI Switcher configs.")

        # First run
        if curMd5Sum is None:
            curMd5Sum = newMd5Sum

        time.sleep(CHECK_CONFIG_CHANGE_INTERVAL_NDI_SWITCHER)

def getAppName(key:str) -> bool:
    """ Returns the app name of the tarids.
    - Args:
        - key: Name of the config key
    - Returns:
        - App Name of the tardis [String]
    """
    patchCfg = getNewTardisConfigs(key)

    try:
        appName = patchCfg.get('common_params', {}).get('app_name', '').strip()
    except Exception as err:
        logger.error(f"Failed to get app name from configs. key: {key}, " \
                     f"patchCfg: {patchCfg}, error: {err}")
        appName = ''

    return appName

def configWatcher() -> bool:
    key = os.environ.get ('CONFIG_KEY')
    if not key:
        logger.fatal ("Environ variable CONFIG_KEY not found")
        return False
    logger.debug ("key : " + key)
    orkyMode = os.environ.get ('ORKY_MODE')
    if not orkyMode:
        logger.fatal ("Environ variable ORKY_MODE not found")
        return False
    else:
        logger.debug("ORKY_MODE : " + orkyMode)
    if orkyMode == 'K8S':
        if (key.endswith('PEER_INPUT') or key.endswith('PEER_OUTPUT')):
            tardisConfigWatcher(orkyMode, key)
        elif (key.startswith('SWITCHER')):
            if getAppName(key) == "ndi_switcher":
                ndiSwitcherConfigWatcher(orkyMode, key)
    return True

if __name__ == '__main__':
    orkyMode = os.environ.get ('ORKY_MODE')
    if orkyMode:
        logger.info ("ORKY_MODE : " + orkyMode)
        if not configWatcher(orkyMode):
            exit(1)
        logger.info ("Config discovery successful")
    else:
        logger.debug ("ORKY_MODE disabled")
    exit(0)
