#!/usr/bin/python3

import redis

from configFileStoreClient import configFileStoreClient

from configFileStoreClientLogger import configFileStoreClientLogger

class configFileStoreRedisClient (configFileStoreClient):
    def __init__(self):
        self.logger = configFileStoreClientLogger ("redis")

    def init (self, host:str=None, port:int=None) -> bool:
        if host is None:
            host = "127.0.0.1"
        if port is None:
            port = 6379

        self.__host = host
        self.__port = port
        self.__r = None

        self.logger.info (f"Init params. host:{host}, port={port}")
        return True

    def deinit (self) -> None:
        self.logger.info ("Deinit params")

    def __getConn (self) -> redis.Redis:
        self.__delConn()

        self.__r = redis.Redis(host=self.__host, port=self.__port, db=0, decode_responses=True)
        if not self.__r:
            return None
        return self.__r

    def __delConn (self) -> None:
        if self.__r:
            del self.__r
        self.__r = None

    def __execute (self, fun, *args) -> 'None/True/str':
        r = self.__getConn()
        if not r:
            self.logger.error ("Failed to connect to redis server.")
            return None

        response = None
        try:
            response = getattr(r,fun)(*args)
        except redis.AuthenticationError as e:
            self.logger.error (f"AuthenticationError: {e}")
        except redis.ConnectionError as e:
            self.logger.error (f"ConnectionError: {e}")
        except redis.TimeoutError as e:
            self.logger.error (f"TimeoutError: {e}")
        except Exception as e:
            self.logger.error ("Unhandled exception")

        self.__delConn()
        return response

    def push (self, key:str, cfgfile:str) -> bool:
        with open(cfgfile, "r") as f:
            d = f.read()

        response = self.__execute("set", key, d)
        # response : None/True
        if response:
            return True
        return False

    def pull (self, key:str, cfgfile:str) -> bool:
        response = self.__execute("get", key)
        # response : None/str
        if not response:
            return False

        with open(cfgfile, "w") as f:
            f.write(response)
        return True


