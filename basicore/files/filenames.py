import os
import logging
logger = logging.getLogger(__name__)


class Filenames:

    @classmethod
    def _breakdown(cls, filepath: str, directory: str = "") -> list[str]:
        """
        Breaks down a file path into its directory, filename, and extension components.

        Args:
            filepath (str): The file path to break down.
            directory (str): Optional. The directory path. If not provided, the directory of the file path will be used.

        Returns:
            list[str]: A list containing the directory, filename, and extension components.
        """
        directory = directory if directory else os.path.dirname(filepath)
        filename, file_ext = os.path.splitext(os.path.basename(filepath))
        file_ext = file_ext if file_ext else ""
        return [directory, filename, file_ext]

    @classmethod
    def append(cls, filepath: str, append: str, directory: str = "", delim: str = "_") -> str:
        """
        Returns a filename with a string appended at the end of the filename.

        Args:
            filepath (str): The file path to append the string to.
            append (str): The string to append to the filename.
            directory (str): Optional. The directory path. If not provided, the directory of the file path will be used.
            delim (str): Optional. The delimiter to use between the original filename and the appended string.

        Returns:
            str: A filename with the specified string appended.
        """
        directory, filename, file_ext = Filenames._breakdown(filepath, directory)
        new_filename = f"{filename}{delim}{append}"
        new_filepath = os.path.join(directory, new_filename + file_ext)
        return new_filepath

    @classmethod
    def prepend(cls, filepath: str, prepend: str, directory: str = "", delim: str = "_") -> str:
        """
        Returns a filename with a string prepended at the beginning of the filename.

        Args:
            filepath (str): The file path to prepend the string to.
            prepend (str): The string to prepend to the filename.
            directory (str): Optional. The directory path. If not provided, the directory of the file path will be used.
            delim (str): Optional. The delimiter to use between the prepended string and the original filename.

        Returns:
            str: A filename with the specified string prepended.
        """
        directory, filename, file_ext = Filenames._breakdown(filepath, directory)
        new_filename = f"{prepend}{delim}{filename}"
        new_filepath = os.path.join(directory, new_filename + file_ext)
        return new_filepath

    @classmethod
    def enumerate(cls, filepath: str, count: int, directory: str = "", delim: str = "_", digits: int = 3) -> str:
        """
        Returns a filename with a specified numerical suffix.

        Args:
            filepath (str): The file path to add the numerical suffix to.
            count (int): The numerical suffix to append to the filename.
            directory (str): Optional. The directory path. If not provided, the directory of the file path will be used.
            delim (str): Optional. The delimiter to use between the original filename and the numerical suffix.
            digits (int): Optional. The number of digits to use for the numerical suffix. The default is 3.

        Returns:
            str: A filename with the specified numerical suffix.
        """
        directory, filename, file_ext = Filenames._breakdown(filepath, directory)
        format_str = "{:0" + str(digits) + "}"
        formatted_num = format_str.format(count)
        new_filename = f"{filename}{delim}{formatted_num}"
        new_filepath = os.path.join(directory, new_filename + file_ext)
        return new_filepath

    @classmethod
    def unique(cls, filepath: str, directory: str = "", delim: str = "_", digits: int = 3) -> str:
        """
        Returns a unique filename by appending a numerical suffix to the original filename.

        The numerical suffix starts at 0 and increments until a unique filename is found.

        Args:
            filepath (str): The original file path.
            directory (str): Optional. The directory path. If not provided, the directory of the file path will be used.
            delim (str): Optional. The delimiter to use between the original filename and the numerical suffix.
            digits (int): Optional. The number of digits to use for the numerical suffix. The default is 3.

        Returns:
            str: A unique filename.
        """
        directory, filename, file_ext = Filenames._breakdown(filepath, directory)
        filepath = os.path.join(directory, filename + file_ext)

        current_suffix: int = 0
        new_filepath = Filenames.enumerate(filepath=filepath, count=current_suffix, directory=directory,
                                           delim=delim, digits=digits)

        # Loop until a unique filename is found
        while os.path.exists(new_filepath):
            current_suffix += 1
            new_filepath = Filenames.enumerate(filepath=filepath, count=current_suffix, directory=directory,
                                               delim=delim, digits=digits)
        return new_filepath
