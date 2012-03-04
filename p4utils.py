"""
A module to handle p4 operations
"""
import P4

from fsutils import Directory, File

class P4utils(object):
    """
    Encapsulates interaction with perforce
    """
    def __init__(self, host, port, user):
        self.host = host
        self.port = port
        self.user = user

        p4 = P4.P4()
        if host:
            p4.host = host
        if port:
            p4.port = port
        if user:
            p4.user = user
        p4.connect()
        self.p4 = p4
        # Raise exceptions on errors only; not warnings
        self.p4.exception_level = 1

    def listdir(self, path):
        """
        Lists the contents of path
        """
        if not path.endswith('/'):
            path += '/'
        dirs = self._get_dirnames(path + '*')
        files = []
        if path != '//':
            # For some reason, p4 files throws an error if called with //*
            files = self._get_filenames(path + '*')
        return self._normalize_paths(path, dirs + files)

    def _normalize_paths(self, root, paths):
        return [path.split(root)[1] for path in paths]

    def _get_dirnames(self, path):
        results = self._get_dirs(path)
        return [item['dir'] for item in results]

    def _get_filenames(self, path):
        results = self._get_files(path)
        return [item['depotFile'] for item in results]

    def _get_dirs(self, path):
        """
        Get directories in path
        """
        return self.p4.run('dirs', path)

    def _get_files(self, path):
        """
        Get files in path
        """
        return self.p4.run('files', path)

    def get_attrs(self, path):
        """
        Get the attributes of path, if it exists. Else, return None
        """
        # Try directory first, then file
        result = self._get_dirs(path)
        if result:
            return P4Directory(path).attrs

        result = self._get_files(path)
        if result:
            return P4File(path, result[0]).attrs

        return None


class P4Directory(Directory):
    """
    A p4 directory, same as a normal directory
    """
    pass


class P4File(File):
    """
    Represents a p4 file
    """
    def __init__(self, path, depotfile):
        self.depotfile = depotfile
        super(P4File, self).__init__(path)

    def get_attrs(self):
        attrs = super(P4File, self).get_attrs()
        time = int(self.depotfile['time'])
        override = {
            'st_atime': time,
            'st_ctime': time,
            'st_mtime': time,
        }
        attrs.update(override)
        return attrs
