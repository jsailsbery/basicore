import os
import json
import logging
import tempfile
from typing import Union

from .remote_command import RemoteCommand, RemoteConnection, RemoteExecuteException
from basicore.parameters import SSHConfig
from basicore.generic import Basic

__all__ = ['RemoteFileActions']
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


class RemoteFileActions:

    @classmethod
    def exists(cls, filepath: str, ssh: RemoteConnection) -> bool:
        """
        Determines if the file at the specified filepath exists.

        Parameters:
            filepath (str): The path of the file to check.
            ssh (RemoteConnection): The SSH connection to the remote server.

        Returns:
            bool: True if the file exists, False otherwise.
        """
        command = f'if [ -e "{filepath}" ]; then echo 0; else echo 1; fi'
        results = RemoteCommand.execute(command=command, command_id='file_exists', ssh=ssh)
        if not results.success:
            raise RemoteExecuteException(f"Error executing remote command: \n>'{command}'\n >{results}")

        if results.stdout == "0":
            return True #Basic.bpass(f"File '{filepath}' exists.")
        return False #Basic.bfail(f"File '{filepath}' does not exist.")

    @classmethod
    def exists_many(cls, filepath_list: list[str], ssh: RemoteConnection) -> dict[str, bool]:
        """
        Determines if the file at the specified filepath exists.

        Parameters:
            filepath_list (str): The paths of the files to check.
            ssh (RemoteConnection): The SSH connection to the remote server.

        Returns:
            bool: True if the file exists, False otherwise.
        """
        command = f'for f in {" ".join(filepath_list)}; do if [ -f "$f" ]; then echo "$f > 1"; ' \
                  f'else echo "$f > 2"; fi; done'
        results = RemoteCommand.execute(command=command, command_id='filelist_exists', ssh=ssh)
        if not results.success:
            raise RemoteExecuteException(f"Error executing remote command: \n>'{command}'\n >{results}")

        file_exists = {}
        for line in results.stdout.splitlines():
            filename, flag = line.split(" > ")
            file_exists[filename] = True if flag == "1" else False
        return file_exists

    @classmethod
    def isfile(cls, filepath: str, ssh: RemoteConnection) -> bool:
        """
        Determines if the file at the specified filepath exists.

        Parameters:
            filepath (str): The path of the file to check.
            ssh (RemoteConnection): The SSH connection to the remote server.

        Returns:
            bool: True if the file exists, False otherwise.
        """
        if not RemoteFileActions.exists(filepath=filepath, ssh=ssh):
            return False

        command = f'if [ -f "{filepath}" ]; then echo 0; else echo 1; fi'
        results = RemoteCommand.execute(command=command, command_id='isfile', ssh=ssh)
        if not results.success:
            raise RemoteExecuteException(f"Error executing remote command: \n>'{command}'\n >{results}")

        if results.stdout == "0":
            return True #Basic.bpass(f"File '{filepath}' is a file.")
        return False #Basic.bfail(f"File '{filepath}' is not a file.")

    @classmethod
    def remove(cls, filepath: str, ssh: RemoteConnection) -> bool:
        """
        Removes the file at the specified filepath if it exists.

        Parameters:
            filepath (str): The path of the file to remove.
            ssh (RemoteConnection): The SSH connection to the remote server.

        Returns:
            None
        """
        if not RemoteFileActions.exists(filepath=filepath, ssh=ssh):
            return True

        command = f'rm -f {filepath}'
        results = RemoteCommand.execute(command=command, command_id='remove_file', ssh=ssh)
        if not results.success:
            logger.warning(f"Error executing remote command: \n>'{command}'\n >{results}")
            if not results.completion:
                raise RemoteExecuteException(f"Error executing remote command: '{command}'")

        if results.success:
            return Basic.bpass(f"File '{filepath}' removed.")
        return Basic.bfail(f"Did not complete removing file '{filepath}'.")

    @classmethod
    def read(cls, filepath: str, ssh: RemoteConnection) -> Union[str, list, dict]:
        """
        Reads the content of a text file.

        Parameters:
            filepath (str): The path of the file to read.
            ssh (RemoteConnection): The SSH connection to the remote server.

        Returns:
            Union[str, list, dict]: The content of the file as a string, list, or dict.
        Raises:
            IOError: If an error occurs while reading the file.
        """
        if not RemoteFileActions.exists(filepath=filepath, ssh=ssh):
            return ""

        command = f'cat {filepath}'
        results = RemoteCommand.execute(command=command, command_id='read_file', ssh=ssh)
        if not results.success:
            logger.warning(f"Error executing remote command: \n>'{command}'\n >{results}")
            if not results.completion:
                raise RemoteExecuteException(f"Error executing remote command: '{command}'")

        if results.success:
            content = results.stdout
            try:
                return json.loads(content)  # Try parsing as JSON dict or list
            except json.JSONDecodeError:
                return content  # Return as plain text if parsing fails
        return Basic.sfail(f"Failed to read {filepath}.")

    @classmethod
    def write(cls, filepath: str, data: Union[str, list, dict], ssh: RemoteConnection, mode: str = "w") -> bool:
        """
        Writes data to a file on a remote system.

        Parameters:
            filepath (str): The path of the file to write on the remote system.
            data (Union[str, list, dict]): The data to write to the file. If it's a list or dict, it will be converted
            to a string using JSON.
            ssh (RemoteConnection): The SSH connection to the remote server.
            mode (str): The file mode to be used for writing. Default is "w" (write). "a" for append.

        Returns:
            bool: True if the operation was successful, False otherwise.
        Raises:
            RemoteExecuteException: If an error occurs while executing the remote command.
        """
        if mode != "w":
            raise RemoteExecuteException("Only write mode is supported at this time.")

        try:
            if isinstance(data, (list, dict)):
                data = json.dumps(data)

            # Write the data to a temporary file on the local system
            with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp:
                tmp.write(data)
                tmp_file = tmp.name

            # Use scp to copy the file to the remote system
            command = RemoteCommand.scp(source=tmp_file, destination=filepath, ssh=ssh)
            if command.completion:
                if command.success:
                    return Basic.bpass(f"Data written to remote file '{filepath}'.")
                else:
                    return Basic.bfail(f"Failed to write data to remote file '{filepath}'.")
            else:
                raise RemoteExecuteException(f"Error executing remote command: 'scp {tmp_file} {filepath}'")
        finally:
            # Ensure the temporary file is removed from the local system
            if tmp_file:
                os.remove(tmp_file)

    @classmethod
    def follow(cls, symlink_target_path: str, ssh: RemoteConnection) -> str:
        """
        Check if a path exists in the remote system and return its size.

        Args:
            symlink_target_path (str): The path to check.
            ssh (RemoteConnection): The SSH connection to the remote server.

        Returns:
            int: The size of the path if it exists, -1 otherwise.
        """
        if not RemoteFileActions.exists(filepath=symlink_target_path, ssh=ssh):
            return ""

        command = f'readlink -f "{symlink_target_path}"'
        results = RemoteCommand.execute(command=command, command_id='follow_symlink', ssh=ssh)
        if not results.success:
            logger.warning(f"Error executing remote command: \n>'{command}'\n >{results}")
            if not results.completion:
                raise RemoteExecuteException(f"Error executing remote command: '{command}'")

        if results.success:
            return Basic.spass(results.stdout, f"Symlink: '{symlink_target_path}' target: {results.stdout}.")
        return Basic.sfail(f"Could not follow symlink file: '{symlink_target_path}'.")
