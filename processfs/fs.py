#!/usr/bin/python

import errno
import fuse
import stat
import time
import os

import shlex
from functools import wraps

fuse.fuse_python_api = (0, 2)

_vfiles = ['stdin', 'stdout', 'stderr', 'cmdline', 'control', 'status']

def has_ent (func):
    @wraps(func)
    def wrapper(self, path, *args,**kwargs):
        if path not in self.files.keys() and path != '/' and  \
                path not in ['%s/%s' % (x,z) for x in self.files.keys() \
                for z in _vfiles]:
            return -errno.ENOENT
        return func(self, path, *args,**kwargs)
    return wrapper

class processfs(fuse.Fuse):
    def __init__(self, *args, **kw):
        fuse.Fuse.__init__(self, *args, **kw)

        self.files = dict()

    ## NEED - returns dir and file stat struct
    @has_ent
    def getattr(self, path):
        print 'getattr(%s)' % path

        st = fuse.Stat()

        if path in self.files.keys() or path == '/':
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
        if path == '/':
            for p in self.files.keys():
                yield fuse.Direntry(p[1:])
        elif path in self.files.keys():
            for p in _vfiles:
                yield fuse.Direntry(p)

    # called when a write op causes a new file to exist
    #def create(self, path, flag, mode):
    #    print 'create(%s)' % path
    #    self.files[path] = dict()

    # obvious - see the syscall
    # Note, offset is always ignored. There'll be no appending here
    ## if we are not creating a new file, buf should be sent to proc
    ## stdin
    @has_ent
    def write(self, path, buf, offset):
        print 'write(%s, %s)' % (path, buf.strip())

        # Until pipes are worked out, return EACCES if a proc is already
        # associated with the file
        if self.files[path].has_key('process'):
            return -errno.EACCES

        ## tokenize (space) the buffer
        self.files[path]['process'] = shlex.split(buf)

        # do basic exec and perm checks - return EINVAL if user would
        # no be able to exec buf.
        # These may need to be seperated once chown/chgrp work
        if offset > 0 or \
            not os.access(self.files[path]['process'][0], os.X_OK):
            ## offset should always be 0 and must be able to exe the path
            return -errno.EINVAL


        self.files[path]['process'] = buf
        return len(buf)

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
        self.files.pop(path)

    # another noop - makes some file writes happy
    @has_ent
    def truncate(self, path, size):
        print 'truncate(%s)' % path
        return 0

    def mkdir(self, path, mode):
        self.files[path] = dict()
