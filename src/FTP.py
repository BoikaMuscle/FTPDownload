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
        self.ftpInfo = ftpInfo

    def GetList(self):
        raise NotImplementedError

    def GetFile(self, filename, filesize, downloadDIR):
        raise NotImplementedError


class LFTP(FTP):
    r"""使用processor来处理各种lftp命令"""
    def __init__(self, ftpInfo):
        super(LFTP, self).__init__(ftpInfo)

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
            loginCM += settings.CM_ftp_Login_TLS_V1  # 添加TLS_V1验证设置。。。

        return loginCM

    def GetList(self):
        print("Get list...")
        self.processor(settings.CM_ts_List)
        print("Got list.")

        try:
            with open(settings.LOG_Filename, encoding='utf-8') as logFile:
                return logFile.read()
        except FileNotFoundError:
            print("[IOError]: No such file or directory: {}".format(settings.LOG_Filename))
            return ''

    def __GetNewFile(self, filename):
        args = settings.ARGS_New_ts_Get
        self.processor(settings.CM_LFTP_Get_File.format(args=args, filename=filename))

    def __GetExistFile(self, filename):
        args = settings.ARGS_Continue_ts_Get
        self.processor(settings.CM_LFTP_Get_File.format(args=args, filename=filename))

    def GetFile(self, filename, filesize, downloadDIR=settings.Download_Dir):
        for cfile in os.listdir(downloadDIR):
            if filename.lower() == cfile.lower():
                if os.path.getsize(os.path.join(downloadDIR, filename)) >= int(filesize):
                    # 文件已存在，下载已完成
                    print("Download end.")
                    return 2
                else:
                    # 文件已存在，继续下载
                    print("Continue download...")
                    self.__GetExistFile(filename) # 10线程 续传
                    return 0
        # 文件不存在，开始下载ts
        print("New download...")
        self.__GetNewFile(filename)
        return 0


class SelfFTP(FTP):
    def __init__(self, ftpInfo):
        super(SelfFTP, self).__init__(ftpInfo)