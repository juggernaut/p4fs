#!/usr/bin/env python

import argparse
from collections import defaultdict
from errno import ENOENT
import sys
import time

from fuse import FUSE, FuseOSError, Operations, LoggingMixIn
from fsutils import Directory
import p4utils

to_p4_path = lambda x: '/' + x


class P4fs(LoggingMixIn, Operations):
    """
    A simple read-only perforce filesystem
    """
    
    def __init__(self, port, user):
        """
        Init method
        """
        self.files = {}
        self.fd = 0
        self.files['/'] = Directory('/')
        self.p4 = p4utils.P4utils(port, user)
        
    def chmod(self, path, mode):
        # XXX: Not implemented
        return 0

    def chown(self, path, uid, gid):
        # XXX: Not implemented
        return
    
    def create(self, path, mode):
        # XXX: Not implemented
        return 0
    
    def getattr(self, path, fh=None):
        if path == '/':
            return self.files[path].attrs
        result = self.p4.get_attrs(to_p4_path(path))
        if not result:
            raise FuseOSError(ENOENT)
        return result
    
    def getxattr(self, path, name, position=0):
        # Extended attributes not supported
        return '' # should return ENOATTR, but it's not in errno
    
    def listxattr(self, path):
        return []
    
    def mkdir(self, path, mode):
        # XXX: Not implemented
        return
    
    def open(self, path, flags):
        self.fd += 1
        return self.fd
    
    def read(self, path, size, offset, fh):
        # XXX: SHOULD be implemented
        # Naive implementation; no caching
        data = self.p4.get_file(to_p4_path(path))
        return data[offset:offset + size]
    
    def readdir(self, path, fh):
        # XXX: SHOULD be implemented
        #return ['.', '..'] + [x[1:] for x in self.files if x != '/']
        dirents = ['..', '..']
        dirents.extend(self.p4.listdir(to_p4_path(path)))
        return dirents
    
    def readlink(self, path):
        return
    
    def removexattr(self, path, name):
        attrs = self.files[path].get('attrs', {})
        try:
            del attrs[name]
        except KeyError:
            pass        # Should return ENOATTR
    
    def rename(self, old, new):
        # XXX: Not implemented
        self.files[new] = self.files.pop(old)
    
    def rmdir(self, path):
        # XXX: Not implemented
        self.files.pop(path)
        self.files['/']['st_nlink'] -= 1
    
    def setxattr(self, path, name, value, options, position=0):
        # Ignore options
        attrs = self.files[path].setdefault('attrs', {})
        attrs[name] = value
    
    def statfs(self, path):
        # XXX: Should be implemented
        return dict(f_bsize=512, f_blocks=4096, f_bavail=2048)
    
    def symlink(self, target, source):
        # Not implemented
        return 0
    
    def truncate(self, path, length, fh=None):
        # Not implemented
        return 0
    
    def unlink(self, path):
        # Not implemented
        return 0
    
    def utimens(self, path, times=None):
        now = time()
        atime, mtime = times if times else (now, now)
        self.files[path]['st_atime'] = atime
        self.files[path]['st_mtime'] = mtime
    
    def write(self, path, data, offset, fh):
        # XXX: Not implemented
        return 0

def parse_opts(opts):
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', '-p', help='port to connect to')
    parser.add_argument('--user', '-u', help='user to connect as')
    parser.add_argument('--debug', '-d', help='show debug info (runs in'
                        ' foreground)', action='store_true', default=False)
    parser.add_argument('mountpoint')

    return parser.parse_args(opts)

if __name__ == "__main__":
    opts = parse_opts(sys.argv[1:])
    p4fs = P4fs(opts.port, opts.user)
    fuse = FUSE(p4fs, opts.mountpoint, foreground=opts.debug)
