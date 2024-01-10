#!/usr/bin/python3

from abc import ABC, abstractmethod

from configFileStoreClientLogger import configFileStoreClientLogger

class configFileStoreClient(ABC):
    def __init__(self):
        self.logger = configFileStoreClientLogger ("abstract")

    @abstractmethod
    def init (self, host:str, port:int) -> bool:
        pass

    @abstractmethod
    def deinit (self) -> None:
        pass

    @abstractmethod
    def push (self, key:str, cfgfile:str) -> bool:
        pass

    @abstractmethod
    def pull (self, key:str, cfgfile:str) -> bool:
        pass

    def __del__(self):
        self.deinit()
