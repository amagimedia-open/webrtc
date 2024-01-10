#!/usr/bin/python3

import tempfile
import os
import configparser
import subprocess
import shutil
import sys
from pathlib import Path

sys.path.append(os.path.join(Path(__file__).parent.absolute(),'dependencies/configFileStoreClient'))

from config_discovery.dependencies.configFileStoreClient.configFileStoreClientFactory import configFileStoreClientFactory
from config_discovery.configDiscoveryLogger import configDiscoveryLogger

logger = configDiscoveryLogger("tardis")

def getTempFile(prefix, dir_) -> str:
    try:
        fd,filepath = tempfile.mkstemp(prefix=prefix, dir=dir_)
        os.close(fd)
    except Exception as e:
        logger.error("Failed to create temp file. " + str(e))
        return ''
    return filepath

def pullFromConfigFileStore (key:str, filepath:str) -> bool:
    factory = configFileStoreClientFactory ()

    client = factory.getClient()
    if not client:
        logger.warning ("Failed to get configFileStoreClient")
        return False

    if not client.init():
        logger.warning ("configFileStoreClient init failed")
        return False

    if not client.pull (key, filepath):
        logger.warning (f"configFileStoreClient pull failed for key:{key}")
        return False

    client.deinit()
    return True

def parseINIFile (filepath:str) -> dict:
    #TODO: Warning: Experimental code.
    # - check if filepath is present
    # - Handle exceptions

    parser = configparser.ConfigParser()
    parser.optionxform = str
    parser.read(filepath)

    d = {}
    for section in parser.sections():
        d[section] = {}
        for key in parser.options(section):
            d[section][key] = parser.get (section,key)
    return d

def runShellCommand(cmd:str, verbose:int=0) -> bool:
    if verbose >= 2:
        logger.info (f"CMD : {cmd}")

    #TODO: Handle exceptions
    #TODO: Improve implementation. Capture stdout and stderr
    result = subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL)
    if result.returncode != 0:
        return False
    return True

def copyFile (src:str, dst:str) -> bool:
    #TODO: Handle exceptions
    shutil.copy2(src,dst)
    return True
