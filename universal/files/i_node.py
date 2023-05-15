import os
import time
import logging
from dataclasses import dataclass
from pathlib import Path
from universal.generic import Basic
logger = logging.getLogger(__name__)


@dataclass
class INode(Basic):
    """
    A class used to represent the metadata of a file or directory.

    Attributes
    ----------
    path : str
        The absolute path of the file or directory. Required.
    name : str
        The name of the file or directory.
    parent : str
        The absolute path of the parent directory.
    exists : bool
        A flag indicating whether the file or directory exists.
    is_dir : bool
        A flag indicating whether the path represents a directory.
    is_symlink : bool
        A flag indicating whether the file or directory is a symlink.
    symlink_target : str
        The target of the symlink (if the file or directory is a symlink).
    mod_time : str
        The last modification time of the file or directory.
    create_time : str
        The creation time of the file or directory.
    access_time : str
        The last access time of the file or directory.
    r_ok : bool
        A flag indicating whether the file or directory has read permission.
    w_ok : bool
        A flag indicating whether the file or directory has write permission.
    x_ok : bool
        A flag indicating whether the file or directory has execute permission.
    """

    path: str
    name: str
    parent: str
    exists: bool
    is_dir: bool
    is_symlink: bool
    symlink_target: str
    mod_time: str
    create_time: str
    access_time: str
    r_ok: bool
    w_ok: bool
    x_ok: bool

    def __init__(self, path: str):
        """
        Initialize an INode object.

        Parameters
        ----------
        path : str
            The path of the file or directory.
        """
        super().__init__()
        self.path = str(Path(path).absolute())
        self._update_attributes()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state):
        self.__dict__ = state

    def __repr__(self):
        return f"INode({self.path})"

    def _update_attributes(self):
        """
        Update the attributes of the INode object.
        """
        try:
            p = Path(self.path)
            self.name = p.name
            self.parent = str(p.parent.absolute())
            self.exists = p.exists()

            self.is_dir = p.is_dir() if self.exists else None
            self.r_ok = os.access(self.path, os.R_OK) if self.exists else None
            self.w_ok = os.access(self.path, os.W_OK) if self.exists else None
            self.x_ok = os.access(self.path, os.X_OK) if self.exists else None

            self.mod_time = time.ctime(p.stat().st_mtime) if self.exists else None
            self.create_time = time.ctime(p.stat().st_ctime) if self.exists else None
            self.access_time = time.ctime(p.stat().st_atime) if self.exists else None

            self.is_symlink = p.is_symlink() if self.exists else None
            if self.is_symlink:
                self.symlink_target = os.readlink(self.path) if self.exists else None
                self.exists = Path(self.symlink_target).exists() if self.exists else None
            else:
                self.symlink_target = ""  if self.exists else None

        except PermissionError as e:
            logger.error(f"Permission denied: {str(e)}")
