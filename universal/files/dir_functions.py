import os
import shutil
import logging
from typing import List, Dict

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


class DirActions:

    @classmethod
    def copy_all(cls, directory: str, destination: str) -> bool:
        """
        This class method copies all contents of one directory to another.
        In case of a failure, an error is logged and the method returns False.
        On successful copying, the method returns True.

        Parameters:
        directory (str): The source directory from which files are to be copied.
        destination (str): The destination directory where files are to be copied.

        Returns:
        bool: True if successful, False otherwise.
        """
        try:
            shutil.copytree(directory, destination)
        except shutil.Error as e:
            logger.error(f"Failed to copy {directory} to {destination}: {e}")
            return False
        return True

    @classmethod
    def remove_contents(cls, directory: str, directories_to_keep: List[str]) -> bool:
        """Remove all directories and files except for a list of directories specified.

        Args:
            directory (str): The directory to remove files and directories from.
            directories_to_keep (List[str]): A list of directory names to keep.

        Returns:
            bool: True if the operation was successful, False otherwise.

        """
        try:
            for filename in os.listdir(directory):
                if filename not in directories_to_keep:
                    file_path = os.path.join(directory, filename)
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
        except Exception as e:
            logger.error(f"Failed to delete files and directories from {directory}. Reason: {str(e)}")
            return False

        return True

    @classmethod
    def list_contents(cls, dir_path: str) -> Dict[str, int]:
        """
        This function returns a dictionary of absolute paths and their corresponding file sizes of the contents of a directory,
        excluding broken symbolic links. If the content is a valid symbolic link,
        it returns the path that the symbolic link points to.

        Parameters:
        dir_path (str): The path to the directory.

        Returns:
        Dict[str, int]: A dictionary where keys are the absolute paths of the contents of the directory and values are their corresponding file sizes.
        """

        if not os.path.exists(dir_path):
            raise FileNotFoundError(f"Directory does not exist: {dir_path}")

        if not os.path.isdir(dir_path):
            raise NotADirectoryError(f"The provided path {dir_path} is not a directory.")

        directory_contents = {}
        for item in os.listdir(dir_path):
            item_full_path = os.path.join(dir_path, item)

            if os.path.islink(item_full_path):
                symlink_target_path = os.readlink(item_full_path)
                if os.path.exists(symlink_target_path):
                    directory_contents[symlink_target_path] = os.stat(symlink_target_path).st_size
                else:
                    logger.warning(f"Broken symbolic link detected: {item_full_path}")

            elif os.path.exists(item_full_path):
                directory_contents[item_full_path] = os.stat(item_full_path).st_size

        return directory_contents

