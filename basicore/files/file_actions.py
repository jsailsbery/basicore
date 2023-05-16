import os
import json
import logging
from pathlib import Path
from typing import Union
logger = logging.getLogger(__name__)


class FileActions:

    @classmethod
    def exists(cls, filepath: str) -> bool:
        """
        Determines if the file at the specified filepath exists.

        Parameters:
            filepath (str): The path of the file to check.

        Returns:
            bool: True if the file exists, False otherwise.
        """
        return os.path.exists(filepath)

    @classmethod
    def isfile(cls, directory: str) -> bool:
        """Check if a directory path.

        Args:
            directory (str): The directory to check.

        Returns:
            bool: True if the directory exists, False otherwise.
        """
        return os.path.isfile(directory)

    @classmethod
    def remove(cls, filepath: str) -> None:
        """
        Removes the file at the specified filepath if it exists.

        Parameters:
            filepath (str): The path of the file to remove.

        Returns:
            None
        """
        if os.path.exists(filepath):
            os.remove(filepath)
        logger.info(f"File removed: {filepath}")

    @classmethod
    def read(cls, filepath: str) -> Union[str, list, dict]:
        """
        Reads the content of a text file.

        Parameters:
            filepath (str): The path of the file to read.

        Returns:
            Union[str, list, dict]: The content of the file as a string, list, or dict.
        Raises:
            IOError: If an error occurs while reading the file.
        """
        try:
            with open(filepath, "r") as f:
                content = f.read()
            try:
                return json.loads(content)  # Try parsing as JSON dict or list
            except json.JSONDecodeError:
                return content  # Return as plain text if parsing fails
        except IOError as e:
            raise IOError(f"Failed to read {filepath}: {str(e)}")

    @classmethod
    def write(cls, filepath: str, data: Union[str, list, dict], mode: str = "w") -> bool:
        """
        Writes data to a file.

        Parameters:
            filepath (str): The path of the file to write.
            data (Union[str, list, dict]): The data to write to the file. If it's a list or dict, it will be converted to a string using JSON.
            mode (str): The file mode to be used for writing. Default is "w" (write). "a" for append.

        Returns:
            bool: True if the operation was successful, False otherwise.
        Raises:
            PermissionError: If write permission is not granted.
            IOError: If an error occurs while writing to the file.
        """
        p = Path(filepath)
        if not p.exists():
            p.mkdir(parents=True, exist_ok=True)

        try:
            if isinstance(data, (list, dict)):
                data = json.dumps(data)

            file_path = filepath if not p.is_symlink() else os.readlink(filepath)
            with open(file_path, mode) as f:
                f.write(data)
        except PermissionError as e:
            raise PermissionError(f"Cannot write to {filepath}: Write permission is not granted.")
        except IOError as e:
            raise IOError(f"Failed to append data to {filepath}: {str(e)}")
        return True

    @classmethod
    def follow(cls, symlink_path: str) -> str:
        """
        Returns the absolute path of the target of a symbolic link.

        Parameters:
            symlink_path (str): The path to the symbolic link.

        Returns:
            str: The absolute path of the target of the symlink.
        Raises:
            FileNotFoundError: If the symlink does not exist.
            ValueError: If the provided path is not a symlink.
        """
        if not os.path.exists(symlink_path):
            raise FileNotFoundError(f"Symlink does not exist: {symlink_path}")

        if not os.path.islink(symlink_path):
            raise ValueError(f"The provided path {symlink_path} is not a symlink.")

        symlink_target_path = os.readlink(symlink_path)
        if os.path.exists(symlink_target_path):
            return os.path.abspath(symlink_target_path)
        else:
            logger.warning(f"Broken symbolic link detected: {symlink_path}")
            return ""