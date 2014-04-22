#!/usr/bin/env python3
# encoding: utf-8

import settings
from FtpInfo import FtpInfo
from Processor import ProcessorFactory
import os


class FTPFactory:
    def __init__(self, ftpInfo):
        if type(ftpInfo) is not FtpInfo:
            raise TypeError

        self.ftpInfo = ftpInfo

    def GetFTP(self):
        return LFTP(self.ftpInfo)


class FTP:
    """其实这应该是抽象类...WTF!!"""
    def __init__(self, ftpInfo):
        if type(ftpInfo) is not FtpInfo:
            raise TypeError

    def GetList(self):
        pass

    def GetFile(self, filename, fileSize, downloadDIR=settings.Download_Dir):
        for cfile in os.listdir(downloadDIR):
            if filename.lower() == cfile.lower():
                if os.path.getsize(os.path.join(downloadDIR, filename)) >= int(fileSize):
                    # 文件已存在，下载已完成
                    print("Download end.")
                    return 2
                else:
                    # 文件已存在，继续下载
                    print("Continue download...")
                    self.ftp.GetExistFile(filename) # 10线程 续传
                    return 0
        # 文件不存在，开始下载ts
        print("New download...")
        self.ftp.GetNewFile(filename)
        return 0


class LFTP(FTP):
    def __init__(self, ftpInfo):
        self.__init__(ftpInfo)

        self.processor = self.__SetProcessor(ftpInfo)

    def __SetProcessor(self,ftpInfo):
        loginCM = self.__GetLoginCM(ftpInfo)

        return ProcessorFactory(loginCM).GetProcessor()

    def __GetLoginCM(self, ftpInfo):
        loginCM = settings.CM_ftp_Login.format(
                host   = ftpInfo['host'],
                user   = ftpInfo['user'],
                passwd = ftpInfo['passwd']
            )
        if ftpInfo['ssh'] == "TLS_V1" or ftpInfo['ssh'] == "SSL_V3":
            loginCM += settings.CM_ftp_Login_TLS_V1

        return loginCM

    def GetList(self):
        print("Get list...")
        self.processor(settings.CM_ts_List)
        print("Got list.")

        try:
            with open(settings.LOG_Filename, encoding='utf-8') as logFile:
                return logFile.read()
        except FileNotFoundError:
            print("[IOError]: No such file or directory: {}".format(logFile))
            return ''

    def GetNewFile(self, filename, args='-n 10'):
        self.processor(settings.CM_ts_Get.format(args=args, filename=filename))

    def GetExistFile(self, filename, args='-n 10'):
        self.processor(settings.CM_ts_Get.format(args='-c ' + args, filename=filename))


class SelfFTP:
    def __init__(self):
        pass
