import os
import logging
import json
import asyncio
from typing import List, Dict, Any

from universal import strip_lines, rremove, first_word

logger = logging.getLogger(__name__)
lock = asyncio.Lock()

class UFile:
    """
    A class containing file I/O utility functions.

    Args:
        filename (str): The input file to read.
        directory (str, optional): The output directory to write files to. Defaults to "".
        overwrite (bool, optional): Whether to overwrite existing files with the same name. Defaults to False.
    """

    def __init__(self, filename: str, directory: str = "", overwrite: bool = False):
        """
        Initializes a new instance of the UFile class.

        Args:
            filename (str): The input file to read.
            directory (str, optional): The output directory to write files to. Defaults to "".
            overwrite (bool, optional): Whether to overwrite existing files with the same name. Defaults to False.
        """
        self.directory = directory if directory else os.path.dirname(filename)
        self.filename, self.file_ext = os.path.splitext(os.path.basename(filename))
        self.file_ext = self.file_ext if self.file_ext else ""
        self.filepath = f"{self.directory}/{self.filename}{self.file_ext}"

        # make path if does not exist, create it
        # If permission prevent it, that ok, as this may be an input file.
        try:
            os.makedirs(self.directory, exist_ok=True)
            logger.info(f"directory exists: {self.directory}")
        except OSError:
            pass

        # clear out old files
        if overwrite:
            self.remove()

    def __str__(self) -> str:
        """
        Returns a JSON string representation of the UFile object.

        Returns:
            str: The JSON string representation of the UFile object.
        """
        return json.dumps(self.__dict__)

    def append_filename(self, to_append: str) -> str:
        """
        Returns a filename with inserted string in the at the end of the filename

        Args:
            to_append (int): The string to append to the filename.

        Returns:
            str: A filename with the specified numerical suffix.
        """
        return f"{self.directory}/{self.filename}_{to_append}{self.file_ext}"

    def prepend_filename(self, to_append: str) -> str:
        """
        Returns a filename with inserted string in the at the end of the filename

        Args:
            to_append (int): The string to append to the filename.

        Returns:
            str: A filename with the specified numerical suffix.
        """
        return f"{self.directory}/{to_append}_{self.filename}{self.file_ext}"

    def enumerate_filename(self, count: int, digits: int = 3) -> str:
        """
        Returns a filename with a specified numerical suffix.

        Args:
            count (int): The numerical suffix to append to the filename.
            digits (int): The number of digits to use for the numerical suffix. The default is 3.

        Returns:
            str: A filename with the specified numerical suffix.
        """
        format_str = "{:0"+str(digits)+"}"
        formatted_num = format_str.format(count)
        return f"{self.directory}/{self.filename}_{formatted_num}{self.file_ext}"

    def unique_filename(self) -> str:
        """
        Returns a unique filename by appending a numerical suffix to the original filename.

        The numerical suffix starts at 0 and increments until a unique filename is found.

        Returns:
            str: A unique filename.
        """
        current_suffix: int = 0
        current_filename: str = self.enumerate_filename(current_suffix)

        # Loop until a unique filename is found
        while os.path.exists(current_filename):
            current_suffix += 1
            current_filename = self.enumerate_filename(current_suffix)

        # Return the unique filename
        return current_filename

    def exists(self) -> bool:
        """
        Determines if filepath in this object exists.

        Returns:
            bool: file exists or not
        """
        return os.path.exists(self.filepath)

    def remove(self) -> None:
        """
        Removes the file at the current filepath if it exists.

        Returns:
            None
        """
        if os.path.exists(self.filepath):
            os.remove(self.filepath)
        logger.info(f"file removed: {self.filepath}")

    def read_text(self) -> str:
        """
        Reads an entire file into a string, preserving newline characters.

        Returns:
            str: The contents of the file as a string.
        """
        with open(self.filepath, 'r') as f:
            return f.read()

    def read_list(self) -> List[str]:
        """
        Reads a text file containing a list of strings.
        Each line will be made an entry into list.
        """
        with open(self.filepath, "r") as file:
            return file.readlines()

    def read_dict(self) -> List[str]:
        """
        Reads a text file containing a dictionary and returns the same.
        Expectation: JSON format
        """
        text = self.read_text()
        return json.loads(text)

    def read_list_of_dicts(self) -> List[Dict[str, Any]]:
        """
        Reads a text file containing a list of dictionaries and returns the list.
        Each line will be made into a dictionary and then an entry into the returned list.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing the data from the file.
        """
        lines = self.read_list()
        return [json.loads(line) for line in lines]

    def write_text(self, text: str, mode: str = "w") -> None:
        """
        Writes the given text to a file.

        Args:
            text (str): The text to be written to the file.
            mode (str): The file mode to be used for writing. Default is "w" (write).

        Returns:
            None
        """
        with open(self.filepath, mode) as outfile:
            outfile.write(text)
            if mode == "a":
                outfile.write("\n")
            outfile.flush()
        logger.info(f"Text written to file: {self.filepath}")

    def write_list(self, data: list, mode: str = "w") -> None:
        """
        Writes the given list of strings to a file.

        Args:
            data (list): The list of strings to be written to the file.
            mode (str): The file mode to be used for writing. Default is "w" (write).

        Returns:
            None
        """
        listdata = [str(dataobj) for dataobj in data]
        strdata = '\n'.join(listdata)
        self.write_text(text=strdata, mode=mode)

    def write_dict(self, data: dict, mode: str = "w") -> None:
        """
        Writes the given dictionary to a file in JSON format.

        Args:
            data (dict): The dictionary to be written to the file.
            mode (str): The file mode to be used for writing. Default is "w" (write).

        Returns:
            None
        """
        self.write_text(text=json.dumps(data), mode=mode)

    async def write_text_async(self, text: str, mode: str = "w") -> None:
        """
        Writes the given text to a file.

        Args:
            text (str): The text to be written to the file.
            mode (str): The file mode to be used for writing. Default is "w" (write).

        Returns:
            None
        """
        async with lock:
            with open(self.filepath, mode) as outfile:
                outfile.write(text)
                if mode == "a":
                    outfile.write("\n")
                outfile.flush()
        logger.info(f"Text written to file: {self.filepath}")

    async def write_list_async(self, data: list, mode: str = "w") -> None:
        """
        Writes the given list of strings to a file.

        Args:
            data (list): The list of strings to be written to the file.
            mode (str): The file mode to be used for writing. Default is "w" (write).

        Returns:
            None
        """
        listdata = [str(dataobj) for dataobj in data]
        strdata = '\n'.join(listdata)
        await self.write_text_async(text=strdata, mode=mode)

    async def write_dict_async(self, data: dict, mode: str = "w") -> None:
        """
        Writes the given dictionary to a file in JSON format.

        Args:
            data (dict): The dictionary to be written to the file.
            mode (str): The file mode to be used for writing. Default is "w" (write).

        Returns:
            None
        """
        await self.write_text_async(text=json.dumps(data), mode=mode)

