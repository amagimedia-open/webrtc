#!/usr/bin/python3

import sys
from pathlib import Path
import os

sys.path.append(os.path.join(Path(__file__).parent.absolute(),'../'))

from configFileStoreClientFactory import configFileStoreClientFactory

def push (key, infile):
    factory = configFileStoreClientFactory ()

    client = factory.getClient()
    if not client:
        print (f"FATAL> Failed to get client")
        return False

    if not client.init():
        print (f"FATAL> Client init failed")
        return False

    if not client.push (key, infile):
        print (f"FATAL> push failed")
        return False

    return True

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print ("FATAL> Invalid usage.")
        print (f"INFO> Usage: python3 {sys.argv[0]} <key> <configfilepath>")
        print (f"INFO> Example: python3 {sys.argv[0]} \"player\" default_ops_config.ini")
        exit(1)
    key = sys.argv[1]
    infile = sys.argv[2]
    push (key, infile)

