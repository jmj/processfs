#!/usr/bin/python

import errno
import fuse
import stat
import time

fuse.fuse_python_api = (0, 2)


class processfs(fuse.Fuse):
    def __init__(self, *args, **kw):
        fuse.Fuse.__init__(self, *args, **kw)

        self.files = list()

    ## NEED - returns dir and file stat struct
    def getattr(self, path):
        print 'getattr(%s)' % path

        if path not in self.files and path != '/':
            return -errno.ENOENT

        st = fuse.Stat()
        st.st_mode = stat.S_IFREG | 0444
        st.st_nlink = 1
        st.st_atime = int(time.time())
        st.st_mtime = st.st_atime
        st.st_ctime = st.st_atime

        if path == '/':
            st.st_nlink = 2
            st.st_mode = stat.S_IFDIR | 0755
        else:
            st.st_size = 100

        return st

    # returns the contents of a directory
    def readdir(self, path, offset):
        ## always return . and ..
        for p in ['.', '..']:
            yield fuse.Direntry(p)
        for p in self.files:
            yield fuse.Direntry(p[1:])

    # called when a write op causes a new file to exist
    def create(self, path, flag, mode):
        print 'create(%s)' % path
        self.files.append(path)

    # obvious - see the syscall
    def write(self, path, buf, offset):
        print 'write(%s, %s)' % (path, buf)
        return len(buf)

    # obvious - see the syscall
    def open(self, path, flags):
        print 'open(%s)' % path

    # called after create to set times
    def utime(self, path, times):
        print 'utime(%s)' % path

    # called after write to "commit" data to "disk"
    def flush(self, path):
        print 'flush(%s)' % path

