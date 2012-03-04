"""
Module for FS utils
"""
import time

from stat import S_IFDIR, S_IFLNK, S_IFREG

class FSobj(object):
    """
    Represents a file system object; not intended to be instantiated directly 
    """
    def __init__(self, path):
        self.path = path

    def get_attrs(self):
        """
        The attributes of this object
        """
        now = time.time()
        return ({
            'st_mode': None, # Set by the overridding class
            'st_ctime': now,
            'st_mtime': now,
            'st_atime': now,
            'st_nlink': None, # Set by the overridding class
        })

class File(FSobj):
    """
    Represents a file object
    """
    def __init__(self, path, data=None):
        super(File, self).__init__(path)
        self.mode = 0400 # read only
        self.attrs = self.get_attrs()
        self.data = data

    def get_attrs(self):
        attrs = super(File, self).get_attrs()
        attrs['st_mode'] = (S_IFREG | self.mode)
        attrs['st_nlink'] = 0
        return attrs


class Directory(FSobj):
    """
    Represents a directory
    """
    def __init__(self, path):
        super(Directory, self).__init__(path)
        self.mode = 0600 # u+rx
        self.attrs = self.get_attrs()

    def get_attrs(self):
        attrs = super(Directory, self).get_attrs()
        attrs['st_mode'] = (S_IFDIR | self.mode)
        # A directory has 2 links by default ('..' and '.')
        attrs['st_nlink'] = 2
        return attrs
