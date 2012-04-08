#!/usr/bin/python

import errno
import fuse
import stat
import time
from functools import wraps

fuse.fuse_python_api = (0, 2)

def has_ent (func):
    @wraps(func)
    def wrapper(self, path, *args,**kwargs):
        if path not in self.files.keys() and path != '/':
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
        st.st_mode = stat.S_IFREG | 0600
        st.st_nlink = 1
        st.st_atime = int(time.time())
        st.st_mtime = st.st_atime
        st.st_ctime = st.st_atime

        # we don't do subdirs.  Is there a need?
        ## Should each proc be a dir?  May have interesting possibilities
        ##  with files like cmd line/stdin/stdout/etc
        if path == '/':
            st.st_nlink = 2
            st.st_mode = stat.S_IFDIR | 0777
        else:
            # return the current length of the ring buffer??
            # how to deal with thing like tail which expect the file
            # to actually change?
            st.st_size = 100

        return st

    # returns the contents of a directory
    def readdir(self, path, offset):
        ## always return . and ..
        for p in ['.', '..']:
            yield fuse.Direntry(p)
        for p in self.files.keys():
            yield fuse.Direntry(p[1:])

    # called when a write op causes a new file to exist
    def create(self, path, flag, mode):
        print 'create(%s)' % path
        self.files[path] = dict()

    # obvious - see the syscall
    # Note, offset is always ignored. There'll be no appending here
    ## if we are not creating a new file, buf should be sent to proc
    ## stdin
    @has_ent
    def write(self, path, buf, offset):
        print 'write(%s, %s)' % (path, buf)

        # do basic exec and perm checks - return EINVAL if user would
        # no be able to exec buf

        # Until pipes are worked out, retuen EACCES if a proc is already
        # associated with the file
        if self.files[path].has_key('process'):
            return -errno.EACCES
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

