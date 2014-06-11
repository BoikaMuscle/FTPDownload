#!/usr/bin/env python
# encoding: utf-8

from __future__ import print_function
from Observer import Observer
import settings
from FTP import FTP
from Select import Selector
#import os
from os.path import split
from os.path import join
#from os.path import normpath
import sys
#from time import sleep
import support2
try:
    import threading as _threading
except ImportError:
    import dummy_threading as _threading


class Getor(Observer):
    def __init__(self, ftp, match, remoteDir, localDir=settings.Download_Dir):
        if not isinstance(ftp, FTP):
            raise TypeError

        super(Getor, self).__init__()

        self._ftp = ftp
        self._localDir = localDir
        self._remoteDir = remoteDir
        self._selector = Selector(r"^\s*(\d+) ({filename})$".format(filename=match))

    def _Download(self, filename, size, remoteDir=''):
        if not remoteDir:
            remoteDir = self._remoteDir
        if support2.Version() == 2:
            filename.encode('utf-8')
        flag = 0
        print("[Fileinfo]: {filename} {filesize}".format(filename=filename, filesize=size))
        while flag != 2:
            flag = self._ftp.GetFile(filename, size, self._localDir, remoteDir)

        return flag

    def Update(self, info):
        try:
            for apple in self._selector.Findall(info):
                size, filename = apple[:2]
                self._Download(filename.strip(), int(size))
                #print(filename, size)
        except:
            print("[Error]: has some error in Getor.")
            self._KillSelf() # 自杀( 其实只是逃离工作而已

    #@property
    #def FTP(self):
    #    return self._ftp

    #@FTP.setter
    #def FTP(self, value):
    #    if not isinstance(value, FTP):
    #        raise TypeError

    #    self._ftp = value

    @property
    def DownloadDir(self):
        return self._localDir

    @DownloadDir.setter
    def DownloadDir(self, value):
        self._localDir = value

    @property
    def FTPDir(self):
        return self._remoteDir

    @FTPDir.setter
    def FTPDir(self, value):
        self._remoteDir = value

def ThreadFunc(func, block=0.5):
        t = _threading.Thread()
        t.run = func
        t.start()
        t.join(block) # 阻塞


class Thread(_threading.Thread):
    def __init__(self, name, func, *args, **kwargs):
        super(Thread, self).__init__()
        if support2.Version() == 2:
            name = name.encode('utf-8')
        self.name = name
        self.setName = name
        self.func = lambda :func(*args, **kwargs)

    def getResult(self):
        return self.res

    def run(self):
        self.res = self.func()
        print(self.name, 'completed!')


class NewGetor(Getor):
    def __init__(self, ftp, match, localDir=settings.Download_Dir):
        super(NewGetor, self).__init__(ftp, match, '/', localDir)
        # replace r'\\' to '/' for support r'\\' directory split symbol.
        match = match.replace('\\\\', '/')
        #print(match)
        self._selector = Selector(join('/', match), log=sys.stdout)
        #print(match)

    def Update(self, info):
        for filename, size in info:
            if self._selector.Match(filename):
                remoteDir, filename = split(filename)
                ThreadFunc(lambda : self._Download(filename, int(size), remoteDir))
                #self._Download(filename, int(size), remoteDir)

