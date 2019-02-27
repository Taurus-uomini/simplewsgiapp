# -*- coding: utf-8 -*-

import logging
from safeLogging import SafeTimedRotatingFileHandler

'''
初始化日志
'''


def loadLogging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    filehandler = SafeTimedRotatingFileHandler('log/tran_', 'D', 1, 0)
    # filehandler.suffix = "%Y%m%d.log"
    filehandler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    filehandler.setFormatter(formatter)
    logger.addHandler(filehandler)
    return logger


'''
记录日志
logger 日志对象
message 记录内容
'''


def writeLogging(logger, message):
    logger.info(message)
