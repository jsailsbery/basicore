import os
import json
import logging
from typing import Union
from dataclasses import dataclass
from pathlib import Path
from .i_node import INode
logger = logging.getLogger(__name__)


@dataclass
class FileNode(INode):
    """
    A class representing a file node.

    Attributes:
        extension (str): The extension of the file.
        size (int): The size of the file in bytes.
    """

    extension: str
    size: int

    def __init__(self, path: str):
        """
        Initializes a FileNode object.

        Args:
            path (str): The path of the file.
        """
        super().__init__(path)
        self._update_attributes()

    def __repr__(self):
        """
        Returns a string representation of the FileNode object.

        Returns:
            str: The string representation of the FileNode object.
        """
        return f"FileNode({self.path})"

    def _update_attributes(self):
        """
        Updates the attributes of the FileNode object.
        """
        super()._update_attributes()
        if self.is_dir:
            raise IsADirectoryError(f"Cannot read {self.path}: It's a directory.")

        p = Path(self.path)
        self.extension = p.suffix
        if self.exists:
            self.size = Path(self.symlink_target).stat().st_size if self.is_symlink else p.stat().st_size

    def remove(self) -> bool:
        """
        Removes the file at the current filepath if it exists.

        Returns:
            bool: True if the file is successfully removed, False otherwise.
        Raises:
            FileNotFoundError: If the file does not exist.
            PermissionError: If write permission is not granted.
            IOError: If an error occurs while removing the file.
        """
        if not self.exists:
            raise FileNotFoundError(f"File does not exist, cannot remove: {self.path}")
        if not self.w_ok:
            raise PermissionError(f"Cannot remove file {self.path}: Write permission is not granted.")

        try:
            os.remove(self.path)
            logger.info(f"File removed: {self.path}")
            return True
        except IOError as e:
            logger.error(f"Failed to remove {self.path}: {str(e)}")
            raise IOError(f"Failed to remove {self.path}: {str(e)}")

    def is_size_greater(self, amount: float, unit: str = "B") -> bool:
        """
        Checks if the file size is greater than the given amount, taking the unit into account.

        Args:
            amount (float): The amount to compare the file size to.
            unit (str): Optional. The unit of the amount ("B", "KB", "MB", "GB"). Default is "B".

        Returns:
            bool: True if the file size is greater than the given amount, False otherwise.
        Raises:
            ValueError: If an invalid unit is provided.
        """
        unit = unit.upper()
        size_in_bytes = {
            "B": self.size,
            "KB": self.size / 1024,
            "MB": self.size / (1024 ** 2),
            "GB": self.size / (1024 ** 3),
        }.get(unit, -1)

        if size_in_bytes == -1:
            raise ValueError(f"Invalid unit: {unit}")

        return size_in_bytes > amount

    def read(self) -> Union[str, list, dict]:
        """
        Read the content of the file and return it as text, list, or dict depending on the content.

        Returns:
            Union[str, list, dict]: The content of the file as text, list, or dict.
        Raises:
            FileNotFoundError: If the file does not exist.
            PermissionError: If read permission is not granted.
            IOError: If an error occurs while reading the file.
        """
        if not self.exists:
            raise FileNotFoundError(f"Cannot read {self.path}: File does not exist.")
        if not self.r_ok:
            raise PermissionError(f"Cannot read {self.path}: Read permission is not granted.")

        try:
            with open(self.path, "r") as f:
                content = f.read()
            try:
                return json.loads(content)  # Try parsing as JSON dict or list
            except json.JSONDecodeError:
                return content  # Return as plain text if parsing fails
        except IOError as e:
            logger.error(f"Failed to read {self.path}: {str(e)}")
            raise IOError(f"Failed to read {self.path}: {str(e)}")

    def write(self, data: Union[str, list, dict], mode: str = "w") -> bool:
        """
        Write data to the file. If the file is a symlink, write to the actual file it points to.

        Args:
            data (Union[str, list, dict]): The data to write to the file. If it's a list or dict,
                it will be converted to a string using JSON.
            mode (str): Optional. The file mode to be used for writing. Default is "w" (write). "a" for append.

        Returns:
            bool: True if the operation was successful, False otherwise.
        Raises:
            PermissionError: If write permission is not granted.
            IOError: If an error occurs while writing to the file.
        """
        if not self.w_ok:
            raise PermissionError(f"Cannot write to {self.path}: Write permission is not granted.")

        try:
            if isinstance(data, (list, dict)):
                data = json.dumps(data)

            file_path = self.path if not self.is_symlink else self.symlink_target
            with open(file_path, mode) as f:
                f.write(data)

            logger.info(f"Data written to file: {self.path}")
            self._update_attributes()
            return True
        except IOError as e:
            logger.error(f"Failed to write data to {self.path}: {str(e)}")
            raise IOError(f"Failed to write data to {self.path}: {str(e)}")
