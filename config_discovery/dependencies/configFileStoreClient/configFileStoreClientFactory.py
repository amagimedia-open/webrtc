#!/usr/bin/python3

from configFileStoreClient import configFileStoreClient
from configFileStoreRedisClient import configFileStoreRedisClient

from configFileStoreClientLogger import configFileStoreClientLogger

class configFileStoreClientFactory():
    def __init__(self):
        self.logger = configFileStoreClientLogger ("factory")
        pass

    def getClient (self, id:str=None) -> configFileStoreClient:
        if id is None:
            id = "redis"

        if id == "redis":
            self.logger.info ("Producing redis client")
            return configFileStoreRedisClient()
        return None

