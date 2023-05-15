import os
import shutil
import logging
from typing import List
from dataclasses import dataclass
from .file_node import FileNode
from .i_node import INode
logger = logging.getLogger(__name__)


@dataclass
class DirNode(INode):
    """
    A class used to represent the metadata of a directory.
    """
    def __init__(self, path: str, create_if_not_exists: bool = True):
        super().__init__(path)

        # Check if directory exists and if not, create if specified
        if not self.exists:
            if create_if_not_exists:
                self.create()
            else:
                raise FileNotFoundError(f"The provided path {self.path} does not exist.")
        elif not self.is_dir:
            raise NotADirectoryError(f"The provided path {self.path} is not a directory.")

    def __repr__(self):
        return f"DirInfo({self.path})"


    def create(self, mode: int = 0o777, exist_ok: bool = False) -> bool:
        """
        Create directories recursively.

        Parameters:
        - mode (int): The permissions to be set for the directories. Default is 0o777.
        - exist_ok (bool): Whether to raise an error if the directories already exist. Default is False.

        Returns:
        - bool: True if the directories were successfully created, False otherwise.
        """
        if self.exists:
            return True

        try:
            os.makedirs(self.path, mode=mode, exist_ok=exist_ok)
            self._update_attributes()
            return self._bool_pass(f"Successfully created dir: {self.path}")
        except Exception as e:
            logger.error(f"Failed to create dir path: {self.path}. Error: {str(e)}")
            return False

    def delete(self) -> bool:
        """
        Delete the directory.

        Returns:
        - bool: True if the directory was successfully deleted, False otherwise.
        """
        try:
            shutil.rmtree(self.path)
            self._update_attributes()
            return self._bool_pass(f"Successfully deleted dir: {self.path}")
        except Exception as e:
            logger.error(f"Failed to delete directory {self.path}. Reason: {str(e)}")
            return False

    def list(self) -> List[INode]:
        """
        Get a list of file and directory nodes inside the directory.

        Returns:
        - List[INode]: A list of INode objects representing the contents of the directory.
        """
        if not self.exists:
            raise FileNotFoundError(f"Cannot read {self.path}: Dir does not exist.")
        if not self.r_ok:
            raise PermissionError(f"Cannot read {self.path}: Read permission is not granted.")

        directory_contents = []
        for item in os.listdir(self.path):
            item_path = os.path.join(self.path, item)
            if os.path.isfile(item_path):
                directory_contents.append(FileNode(item_path))
            elif os.path.isdir(item_path):
                directory_contents.append(DirNode(item_path))
            else:
                logger.warning(f"File disappeared or bad file handle: {item_path}")

        return directory_contents

    def copy(self, destination_dir: str) -> bool:
        """
        Copy the directory and its contents to the destination directory.

        Parameters:
        - destination_dir (str): The destination directory where the contents will be copied.

        Returns:
        - bool: True if the directory was successfully copied, False otherwise.
        """
        if os.path.exists(destination_dir):
            logger.error(f"Destination directory {destination_dir} already exists.")
            return False

        try:
            shutil.copytree(self.path, destination_dir)
            return True
        except Exception as e:
            logger.error(f"Failed to copy {self.path} to {destination_dir}: {str(e)}")
            return False

    def remove(self, files_to_keep: List[str]) -> bool:
        """Remove all directories and files except for a list of directories specified.

        Args:
            files_to_keep (List[str]): A list of file names to keep. Relative paths only.

        Returns:
            bool: True if the operation was successful, False otherwise.

        """
        try:
            for inode in self.list():
                filename = os.path.basename(inode.path)
                if filename not in files_to_keep:
                    if isinstance(inode, FileNode):
                        os.unlink(inode.path)
                    elif isinstance(inode, DirNode):
                        shutil.rmtree(inode.path)
            return True
        except Exception as e:
            logger.error(f"Failed to delete files and directories from {self.path}. Reason: {str(e)}")
            return False
