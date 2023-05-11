import os
import fnmatch
import re
import logging
from typing import List, Iterator

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


class GrepTool:
    """
    A utility class for searching and matching patterns in files within a directory and its subdirectories.
    This class provides methods for searching files based on a file name pattern, searching for a text
    pattern within files, and combining both operations to grep all files in a directory.
    """

    @classmethod
    def search_files(cls, directory: str, pattern: str, case_sensitive: bool = False) -> Iterator[str]:
        """
        Search for files matching a pattern in a directory and its subdirectories.

        :param directory: The directory to start the search from.
        :param pattern: The pattern to search for in file names.
        :param case_sensitive: Whether the search should be case-sensitive. Defaults to False.
        :return: An iterator of file paths matching the pattern.
        """
        if not case_sensitive:
            pattern = pattern.lower()

        if not os.path.isdir(directory):
            logger.error(f"Provided path is not a directory: {directory}")
            return iter([])

        try:
            for root, _, filenames in os.walk(directory):
                for filename in fnmatch.filter(filenames, '*'):
                    if not case_sensitive:
                        filename = filename.lower()
                    if fnmatch.fnmatch(filename, pattern):
                        yield os.path.join(root, filename)
        except (OSError, FileNotFoundError) as e:
            logger.error(f"Error searching files: {str(e)}")
            return iter([])

    @classmethod
    def grep(cls, pattern: str, files: Iterator[str], ignore_case: bool = True) -> List[str]:
        """
        Search for a pattern in a list of files and log the file path, line number, and line content for each match found.

        :param pattern: The pattern to search for.
        :param files: An iterator of file paths to search in.
        :param ignore_case: Whether the search should ignore case. Defaults to True.
        """
        lines = []
        regex = re.compile(pattern, re.IGNORECASE if ignore_case else 0)

        for file_path in files:
            try:
                with open(file_path, "r", errors='ignore') as file:
                    for line_number, line in enumerate(file, 1):
                        if regex.search(line):
                            lines.append(line)
                            logger.info(f"{file_path}:{line_number}:{line.strip()}")
            except (FileNotFoundError, PermissionError, OSError) as e:
                logger.error(f"Error processing file {file_path}: {str(e)}")

        return lines

    @classmethod
    def grep_all_files(cls, pattern: str, directory: str) -> List[str]:
        """
        Search for a pattern in all files within a directory and its subdirectories.

        This method combines the functionality of search_files and grep methods to search for a
        text pattern in all files within the specified directory and its subdirectories.

        :param pattern: The pattern to search for.
        :param directory: The directory to start the search from.
        :return: A list of lines containing the pattern from all matching files.
        """
        all_files = GrepTool.search_files(directory, "*")
        return cls.grep(pattern, all_files)
