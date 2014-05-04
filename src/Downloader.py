#!/usr/bin/env python
#encoding: utf-8

from __future__ import print_function
from Listen import Listener
from FTP import FTPFactory
from Getor import Getor
from os.path import basename, dirname, normpath
import settings


class Downloader:
    def __init__(self, ftp, lock, *filenameList):

        self.listenerDict = dict()
        self.getorList = list()
        self.lock = lock

        for filename in filenameList:
            # 获取基本文件名和路径名
            DIR = normpath(dirname(filename))  # [default: '.']
            baseFilename = basename(filename)
            # 一个路径名对应一个listener，一个文件名对应一个getor
            # 一个listener对应同一路径名的多个getor
            try:
                self.listenerDict[DIR]
            except KeyError:
                # 创建一个新的listener
                self.listenerDict[DIR] = Listener(ftp, DIR, self.lock)
            finally:
                # 创建一个新的getor，并使之注册同一路径的listener
                self.getorList.append(Getor(ftp, baseFilename, DIR, settings.Download_Dir))
                self.listenerDict[DIR].Attach(self.getorList[-1])

    def Run(self):
        for listener in self.listenerDict.values():
            listener.start()

        for listener in self.listenerDict.values():
            listener.join()

    @property
    def DownloadDIR(self):
        raise NotImplementedError

    @DownloadDIR.setter
    def DwonloadDIR(self, value):
        # 设置下载目录
        for getor in self.getorList:
            getor.DownloadDir = value