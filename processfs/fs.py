#!/usr/bin/python

import errno
import fuse
import stat
import time
#from multiprocessing import Queue
from functools import wraps

from processfs.svcmanager import Manager
import processfs.svcmanager as svcmanager

fuse.fuse_python_api = (0, 2)

_vfiles = ['stdin', 'stdout', 'stderr', 'cmdline', 'control', 'status']

def has_ent (func):
    @wraps(func)
    def wrapper(self, path, *args,**kwargs):
        print 'called %s %s %s' % (func, path, args)
        print self._svcmanager.procs.keys()
        vpaths = ['%s/%s' % (x,z) for x in self._svcmanager.procs.keys() \
                for z in _vfiles]
        vpaths.append('/')
        vpaths.extend(self._svcmanager.procs.keys())
        if path not in vpaths:
            return -errno.ENOENT
        return func(self, path, *args,**kwargs)
    return wrapper

class processfs(fuse.Fuse):
    def __init__(self, *args, **kw):
        fuse.Fuse.__init__(self, *args, **kw)

        self._svcmanager = Manager()
        self._svc_queue = self._svcmanager.queue

        print type(self._svc_queue)

        # start the process manager thread
        print 'starting svc manager'
        self._svcmanager.start()

    ## NEED - returns dir and file stat struct
    @has_ent
    def getattr(self, path):
        print 'getattr(%s)' % path

        st = fuse.Stat()

        if path in self._svcmanager.procs.keys() or path == '/':
            st.st_nlink = 2
            st.st_mode = stat.S_IFDIR | 0777
        else:
            st.st_mode = stat.S_IFREG | 0600
            st.st_nlink = 1

        st.st_atime = int(time.time())
        st.st_mtime = st.st_atime
        st.st_ctime = st.st_atime
        st.st_size = 100

        return st

    # returns the contents of a directory
    def readdir(self, path, offset):
        ## always return . and ..
        for p in ['.', '..']:
            yield fuse.Direntry(p)
        procs = self._svcmanager.procs.keys()
        if path == '/':
            for p in procs:
                yield fuse.Direntry(p[1:])
        elif path in procs:
            for p in _vfiles:
                yield fuse.Direntry(p)

    # obvious - see the syscall
    # Note, offset is always ignored. There'll be no appending here
    ## if we are not creating a new file, buf should be sent to proc
    ## stdin
    @has_ent
    def write(self, path, buf, offset):
        print 'write(%s, %s)' % (path, buf.strip())

        if path not in ['%s/%s' % (x,z) \
                for x in self._svcmanager.procs.keys() \
                for z in _vfiles]:
            return -errno.EOPNOTSUPP

        else:
            # Implement later
            return -errno.EACCES

    # obvious - see the syscall
    @has_ent
    def open(self, path, flags):
        print 'open(%s)' % path
        return 0

    # called after create to set times
    @has_ent
    def utime(self, path, times):
        print 'utime(%s)' % path

    # called after write to "commit" data to "disk"
    @has_ent
    def flush(self, path):
        print 'flush(%s)' % path

    # should connect to proc ring buffer
    @has_ent
    def read(self, path, len, offset):

        return self.files[path]['process'][offset:offset+len]

    @has_ent
    def unlink(self, path):
        print 'unlink(%s)' % path

    # another noop - makes some file writes happy
    @has_ent
    def truncate(self, path, size):
        print 'truncate(%s)' % path
        return 0

    def mkdir(self, path, mode):
        print 'mkdir(%s, %s)' % (path, mode)
        self._svc_queue.put([svcmanager.MKPROC, path])
        self._svc_queue.join()
        return 0

    def fsdestroy(self, *args, **kw):
        self._svcmanager.stop()
