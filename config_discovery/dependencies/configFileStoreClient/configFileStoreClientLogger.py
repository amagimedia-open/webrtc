#!/usr/bin/python3

#import logging
import syslog
import datetime

class configFileStoreClientLogger:

  def __init__(self,module):
    self.module = module

  def debug(self, log_message):
    self.log(syslog.LOG_DEBUG, log_message)

  def info(self, log_message):
    self.log(syslog.LOG_INFO, log_message)

  def warning(self, log_message):
    self.log(syslog.LOG_WARNING, log_message)

  def error(self, log_message):
    self.log(syslog.LOG_ERR, log_message)

  def fatal(self, log_message):
    self.log(syslog.LOG_CRIT, log_message)

  def log(self, priority, log_message):

    if priority == syslog.LOG_DEBUG:
        p_string = 'DEBUG'
    #end

    if priority == syslog.LOG_INFO:
        p_string = 'INFO'
    #end

    if priority == syslog.LOG_WARNING:
        p_string = 'WARN'
    #end

    if priority == syslog.LOG_ERR:
        p_string = 'ERROR'
    #end

    if priority == syslog.LOG_CRIT:
        p_string = 'FATAL'
    #end

    syslog.openlog(ident=',', logoption=syslog.LOG_PID)
    module_log_message = ',' + p_string + ', com.amagi.configFileStoreClient, ' + self.module + ': ' + str(log_message)
    syslog.syslog(priority, module_log_message)
#end
