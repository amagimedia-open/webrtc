#!/usr/bin/python3

#import logging
#import syslog
import datetime

class configDiscoveryLogger:

  def __init__(self,module):
    self.module = module

  def debug(self, log_message):
    self.log(log_message)

  def info(self, log_message):
    self.log(log_message)

  def warning(self, log_message):
    self.log(log_message)

  def error(self, log_message):
    self.log(log_message)

  def fatal(self, log_message):
    self.log(log_message)

  def log(self, log_message):

    #if priority == syslog.LOG_DEBUG:
    #    p_string = 'DEBUG'
    #end

    #if priority == syslog.LOG_INFO:
    #    p_string = 'INFO'
    #end

    #if priority == syslog.LOG_WARNING:
    #    p_string = 'WARN'
    #end

    #if priority == syslog.LOG_ERR:
    #    p_string = 'ERROR'
    #end

    #if priority == syslog.LOG_CRIT:
    #    p_string = 'FATAL'
    #end

    #syslog.openlog(ident=',', logoption=syslog.LOG_PID)
    p_string = 'INFO'
    module_log_message = ',' + p_string + ', com.amagi.configDiscovery, ' + self.module + ': ' + str(log_message)
    print(module_log_message)
#end
