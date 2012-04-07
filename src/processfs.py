#!/usr/bin/python

import errno
import fuse
import os
import stat
import sys
from time import time

fuse.fuse_python_api = (0, 2)

class processfs(fuse.Fuse):
    def __init__(self, *args, **kw):
        fuse.Fuse.__init__(self, *args, **kw)

    ## NEED
    def getattr(self, path):
        st = fuse.Stat()
        st.st_mode = stat.S_IFDIR | 0755
        st.st_nlink = 2
        st.st_atime = int(time.time())
        st.st_mtime = st.st_atime
        st.st_ctime = st.st_atime

        if path == '/':
            pass
        else:
            return -errno.ENOENT
        return st

    def readdir(self, path, offset):
        for p in ['.', '..', 'a', 'b']:
            yield fuse.Direntry(p)

if __name__ == '__main__':
    fs = testfs()
    fs.parse()
    fs.flags = 0
    fs.multithreaded = 0
    fs.main()
