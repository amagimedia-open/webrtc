#!/usr/bin/python3

import os
import time
from configobj import ConfigObj

from config_discovery.configDiscoveryLogger import configDiscoveryLogger
from config_discovery.utils import *


RETRY_INTERVAL_SEC = 1
CONFIG_FILEPATH = "/home/root/configs/config.ini"

G_SwitcherCfgGenScriptPath = "/home/root/docker_mgmt/configure_tardis.py"
G_SwitcherCfgGenMapPath = "/home/root/docker_mgmt/config_mapping.csv"
G_SwitcherDefaultCfgFilePath = "/home/root/docker_mgmt/config.ini"
G_TardisDefaultCfgFilePath = "/home/root/docker_mgmt/config.ini"

# Test paths
#CONFIG_FILEPATH = "/tmp/config.ini"
#G_SwitcherCfgGenScriptPath = "/home/suren/p/tardis/sdm/docker_mgmt/configure_tardis.py"
#G_SwitcherCfgGenMapPath = "/home/suren/p/tardis/sdm/docker_mgmt/config_mapping.csv"
#G_SwitcherDefaultCfgFilePath = "/home/suren/p/tardis/sdm/docker_mgmt/config.ini"
#G_TardisDefaultCfgFilePath = "/home/suren/p/tardis/sdm/docker_mgmt/config.ini"

logger = configDiscoveryLogger("tardis")


def genSwitcherConfigFile (switcherCfgFile:str, playerCfgFiles:list, switcherType:str) -> bool:
    cmd = f"python3 {G_SwitcherCfgGenScriptPath} {switcherType} {G_SwitcherCfgGenMapPath} {G_SwitcherDefaultCfgFilePath} {switcherCfgFile} "
    for playerCfg in playerCfgFiles:
        cmd += f"{playerCfg} "
    if not runShellCommand (cmd):
        return False

    return os.path.isfile(switcherCfgFile)

def removeFiles(filesList):
    for file in filesList:
        os.remove(file)

#The function constructs a ristin_url using the configurations.
def createRistinUrl(ristin_configs):
    url = "rist://{dns}:{port}?mode={mode}&latency={latency}&passphrase={passphrase}&encryption_type={encryption_type}&iface={iface}&output_ip={output_ip}&output_port={output_port}&profile_num={profile_num}&output_protocol={ristin_output_type}"
    ristin_configs.setdefault("ristin_input_ip", "")
    ristin_configs.setdefault("ristin_input_port", "")
    ristin_configs.setdefault("ristin_mode", "")
    ristin_configs.setdefault("ristin_output_type", "")
    ristin_configs.setdefault("ristin_output_iface", "")
    ristin_configs.setdefault("ristin_output_ip", "")
    ristin_configs.setdefault("ristin_output_port", "")
    ristin_configs.setdefault("ristin_latency_ms", "")
    ristin_configs.setdefault("ristin_encryption_type", "")
    ristin_configs.setdefault("ristin_passphrase", "")
    ristin_configs.setdefault("ristin_profile_num", "")
    url = url.format(
        dns = ristin_configs["ristin_input_ip"],
        port = ristin_configs["ristin_input_port"],
        mode = ristin_configs["ristin_mode"],
        ristin_output_type = ristin_configs["ristin_output_type"],
        iface = ristin_configs["ristin_output_iface"],
        output_ip = ristin_configs["ristin_output_ip"] ,
        output_port = ristin_configs["ristin_output_port"],
        latency = ristin_configs["ristin_latency_ms"],
        passphrase = ristin_configs["ristin_passphrase"],
        encryption_type = ristin_configs["ristin_encryption_type"],
        profile_num = ristin_configs["ristin_profile_num"]        
    )
    return url
  
#The function constructs a ristout_url using the configurations.
def createRistoutUrl(ristout_configs):
    url = "rist://{dns}:{port}?mode={mode}&latency={latency}&passphrase={passphrase}&encryption_type={encryption_type}&iface={iface}&output_ip={output_ip}&output_port={output_port}&profile_num={profile_num}&input_protocol={ristout_input_type}"
    ristout_configs.setdefault("ristout_input_ip", "")
    ristout_configs.setdefault("ristout_input_port", "")
    ristout_configs.setdefault("ristout_mode", "")
    ristout_configs.setdefault("ristout_input_type", "")
    ristout_configs.setdefault("ristout_input_iface", "")
    ristout_configs.setdefault("ristout_output_ip", "")
    ristout_configs.setdefault("ristout_output_port", "")
    ristout_configs.setdefault("ristout_latency_ms", "")
    ristout_configs.setdefault("ristout_encryption_type", "")
    ristout_configs.setdefault("ristout_passphrase", "")
    ristout_configs.setdefault("ristout_profile_num", "")
    url = url.format(
        dns = ristout_configs["ristout_input_ip"],
        port = ristout_configs["ristout_input_port"],
        mode = ristout_configs["ristout_mode"],
        ristout_input_type = ristout_configs["ristout_input_type"],
        iface = ristout_configs["ristout_input_iface"],
        output_ip = ristout_configs["ristout_output_ip"] ,
        output_port = ristout_configs["ristout_output_port"],
        latency = ristout_configs["ristout_latency_ms"],
        passphrase = ristout_configs["ristout_passphrase"],
        encryption_type = ristout_configs["ristout_encryption_type"],
        profile_num = ristout_configs["ristout_profile_num"]
    )
    return url

# patchConfigs is added to support backward compatibility. 
def patchConfigs(patchCfg, baseCfg):
    if patchCfg["common_params"]["app_name"] == "rist_in":
        if "ristin_url" not in patchCfg["rist_in"]:
            ristin_url = createRistinUrl(patchCfg["rist_in"])
            patchCfg["rist_in"]["ristin_url"] = ristin_url
            
    if patchCfg["common_params"]["app_name"] == "rist_out":
        if "ristoutg_url" not in patchCfg["rist_out"]:
            ristout_url = createRistoutUrl(patchCfg["rist_out"])
            patchCfg["rist_out"]["ristout_url"] = ristout_url
    for s in patchCfg:
        if s in baseCfg:
            for k in patchCfg[s]:
                if k in baseCfg[s]:
                    baseCfg[s][k] = patchCfg[s][k]

    baseCfg.write_empty_values = True
    baseCfg.write()

def discoverConfigsK8S (key) -> bool:
    # Download patch config file
    patchCfgFile = getTempFile('discoveryConfigs_patchCfg_', '/tmp')
    if not patchCfgFile:
        logger.error("Failed to create temp file to download patch config file")
        return False

    if not pullFromConfigFileStore (key, patchCfgFile):
        os.remove(patchCfgFile)
        return False

    patchCfg = parseINIFile (patchCfgFile)
    if not patchCfg:
        logger.error (f'Failed to parse INI file : {patchCfgFile}')
        os.remove(patchCfgFile)
        return False
    os.remove(patchCfgFile)

    if "common_params" not in patchCfg or \
            "app_name" not in patchCfg["common_params"]:
        logger.error (f'Invalid patchCfg')
        return False

    # Create base config file
    baseCfgFile = None
    if patchCfg["common_params"]["app_name"] == "amagi_switcher" or patchCfg["common_params"]["app_name"] == "ndi_switcher":
        if patchCfg["common_params"]["app_name"] == "amagi_switcher":
            # Switcher
            switcherType = "ts_switcher"
            if "ts_switcher" in patchCfg and "tsss_udpin_ip" in patchCfg["ts_switcher"]:
                numInputStreams = len([k.strip() for k in \
                    patchCfg["ts_switcher"]["tsss_udpin_ip"].split(',')])
            else:
                logger.error (f'Missing ts_switcher params. Invalid patchCfg')
                return False
            logger.info(f"Number of input streams: {numInputStreams}")
        else:
            # NDI Switcher
            switcherType = "ndi_switcher"
            if "ndi_switcher" in patchCfg and "ndi_switcher_in_hostname" in patchCfg["ndi_switcher"]:
                numInputStreams = len([k.strip() for k in \
                    patchCfg["ndi_switcher"]["ndi_switcher_in_hostname"].split(',')])
            else:
                logger.error (f'Missing ndi_switcher params. Invalid patchCfg')
                return False
            logger.info(f"Number of input streams: {numInputStreams}")

        # append only primary player (player1) config to playerCfgFiles
        # so that switcher generates its config only from this primary player.
        playerCfgFiles = []
        tempFilePrefix = 'discoveryConfigs_player1' + 'Cfg_'
        playerCfgFile = getTempFile(tempFilePrefix, '/tmp')
        if not playerCfgFile:
            logger.error(f"Failed to create temp file to download player1 config file")
            return False
        if not pullFromConfigFileStore (f"{key}_PLAYER1_CONFIG_INI", playerCfgFile):
            logger.error(f"Failed to pull {key}_PLAYER1_CONFIG_INI for config file store")
            os.remove(playerCfgFile)
            return False
        for _ in range(1, numInputStreams+1):
            playerCfgFiles.append(playerCfgFile)

        switcherCfgFile = getTempFile('discoveryConfigs_switcherCfg_', '/tmp')
        if not switcherCfgFile:
            logger.error("Failed to create temp file to generate switcher config file")
            os.remove(playerCfgFile)
            return False

        if not genSwitcherConfigFile (switcherCfgFile, playerCfgFiles, switcherType):
            logger.error ("Failed to generate Switcher configurations using Player configurations")
            os.remove(switcherCfgFile)
            os.remove(playerCfgFile)
            return False
        os.remove(playerCfgFile)

        baseCfgFile = switcherCfgFile
    else:
        # Tardis
        tardisCfgFile = getTempFile('discoveryConfigs_tardisCfg_', '/tmp')
        if not tardisCfgFile:
            logger.error("Failed to create temp file for tardis config file")
            return False

        if not copyFile(G_TardisDefaultCfgFilePath, tardisCfgFile):
            logger.error("Failed to copy tardis default config file")
            os.remove(tardisCfgFile)
            return False

        baseCfgFile = tardisCfgFile

    # Apply patch configs on base configs
    baseCfg = ConfigObj(baseCfgFile, list_values=False)

    patchConfigs(patchCfg, baseCfg)

    # Create Tardis/Switcher config file
    if not copyFile(baseCfgFile, CONFIG_FILEPATH):
        logger.error("Failed to copy config file to {CONFIG_FILEPATH}")
        os.remove(baseCfgFile)
        return False

    os.remove(baseCfgFile)
    return True

def discoverConfigs (orkyMode:'str') -> bool:
    if orkyMode == 'K8S':
        key = os.environ.get ('CONFIG_KEY')
        if not key:
            logger.fatal ("Environ variable CONFIG_KEY not found")
            return False
        logger.debug ("key : " + key)
        while not discoverConfigsK8S(key):
            logger.info (f"Retrying to discovery configs in {RETRY_INTERVAL_SEC} seconds")
            time.sleep (RETRY_INTERVAL_SEC)
        return True
    else:
        logger.fatal("Unsupported orkyMode")
        return False

if __name__ == '__main__':
    orkyMode = os.environ.get ('ORKY_MODE')
    if orkyMode:
        logger.info ("ORKY_MODE : " + orkyMode)
        if not discoverConfigs(orkyMode):
            exit(1)
        logger.info ("Config discovery successful")
    else:
        logger.debug ("ORKY_MODE disabled")
    exit(0)
