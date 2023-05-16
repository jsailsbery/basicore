import os
import json
import logging
import tempfile
from typing import Union

from .remote_command import RemoteCommand, RemoteExecuteException
from universal.parameters import SSHConfig
from universal.generic import Basic

__all__ = ['RemoteFileActions']
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


class RemoteFileActions:

    @classmethod
    def exists(cls, filepath: str, authentication: SSHConfig) -> bool:
        """
        Determines if the file at the specified filepath exists.

        Parameters:
            filepath (str): The path of the file to check.
            authentication (SSHConfig): The SSH configuration for connecting to the remote server.

        Returns:
            bool: True if the file exists, False otherwise.
        """
        command = f'if [ -e "{filepath}" ]; then exit 0; else exit 1; fi'
        results = RemoteCommand.execute(command=command, command_id='file_exists', authentication=authentication)
        if results.completion:
            if results.success:
                return Basic.bpass(f"File '{filepath}' exists.")
            elif results.errors:
                raise RemoteExecuteException(f"File '{filepath}' existence could not be verified. {results}")
            else:
                return Basic.bfail(f"File '{filepath}' does not exist.")
        else:
            raise RemoteExecuteException(f"Error executing remote command: '{command}'")

    @classmethod
    def isfile(cls, filepath: str, authentication: SSHConfig) -> bool:
        """
        Determines if the file at the specified filepath exists.

        Parameters:
            filepath (str): The path of the file to check.
            authentication (SSHConfig): The SSH configuration for connecting to the remote server.

        Returns:
            bool: True if the file exists, False otherwise.
        """
        if not RemoteFileActions.exists(filepath=filepath, authentication=authentication):
            return False

        command = f'if [ -f "{filepath}" ]; then exit 0; else exit 1; fi'
        results = RemoteCommand.execute(command=command, command_id='isfile', authentication=authentication)
        if results.completion:
            if results.success:
                return Basic.bpass(f"File '{filepath}' is a file.")
            elif results.errors:
                raise RemoteExecuteException(f"File '{filepath}' type could not be verified. {results}")
            else:
                return Basic.bfail(f"File '{filepath}' is not a file.")
        else:
            raise RemoteExecuteException(f"Error executing remote command: '{command}'")

    @classmethod
    def remove(cls, filepath: str, authentication: SSHConfig) -> bool:
        """
        Removes the file at the specified filepath if it exists.

        Parameters:
            filepath (str): The path of the file to remove.
            authentication (SSHConfig): The SSH configuration for connecting to the remote server.

        Returns:
            None
        """
        if not RemoteFileActions.exists(filepath=filepath, authentication=authentication):
            return True

        command = f'rm -f {filepath}'
        results = RemoteCommand.execute(command=command, command_id='remove_file', authentication=authentication)
        if results.completion:
            if results.success:
                return Basic.bpass(f"File '{filepath}' removed.")
            elif results.errors:
                raise RemoteExecuteException(f"File '{filepath}' removal not confirmed. Errors in execution. {results}")
            else:
                return Basic.bfail(f"Did not complete removing file '{filepath}'.")
        else:
            raise RemoteExecuteException(f"Error executing remote command: '{command}'")

    @classmethod
    def read(cls, filepath: str, authentication: SSHConfig) -> Union[str, list, dict]:
        """
        Reads the content of a text file.

        Parameters:
            filepath (str): The path of the file to read.
            authentication (SSHConfig): The SSH configuration for connecting to the remote server.

        Returns:
            Union[str, list, dict]: The content of the file as a string, list, or dict.
        Raises:
            IOError: If an error occurs while reading the file.
        """
        if not RemoteFileActions.exists(filepath=filepath, authentication=authentication):
            return ""

        command = f'cat {filepath}'
        results = RemoteCommand.execute(command=command, command_id='read_file', authentication=authentication)
        if results.completion:
            if results.success:
                content = results.stdout
                try:
                    return json.loads(content)  # Try parsing as JSON dict or list
                except json.JSONDecodeError:
                    return content  # Return as plain text if parsing fails
            else:
                return Basic.sfail(f"Failed to read {filepath}.")
        else:
            raise RemoteExecuteException(f"Error executing remote command: '{command}'")

    @classmethod
    def write(cls, filepath: str, data: Union[str, list, dict], authentication: SSHConfig, mode: str = "w") -> bool:
        """
        Writes data to a file on a remote system.

        Parameters:
            filepath (str): The path of the file to write on the remote system.
            data (Union[str, list, dict]): The data to write to the file. If it's a list or dict, it will be converted
            to a string using JSON.
            authentication (SSHConfig): The authentication configuration for the remote system.
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
            command = RemoteCommand.scp(source=tmp_file, destination=filepath, authentication=authentication)
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
    def follow(cls, symlink_target_path: str, authentication: SSHConfig) -> str:
        """
        Check if a path exists in the remote system and return its size.

        Args:
            symlink_target_path (str): The path to check.
            authentication (SSHConfig): The SSH configuration for connecting to the remote server.

        Returns:
            int: The size of the path if it exists, -1 otherwise.
        """
        if not RemoteFileActions.exists(filepath=symlink_target_path, authentication=authentication):
            return ""

        command = f'readlink -f "{symlink_target_path}"'
        results = RemoteCommand.execute(command=command, command_id='follow_symlink', authentication=authentication)
        if results.completion:
            if results.success:
                return Basic.spass(results.stdout.strip(), f"Symlink: '{symlink_target_path}' target: {results.stdout}.")
            elif results.errors:
                raise RemoteExecuteException(f"Errors occurred trying to follow symlink file {results}")
            else:
                return Basic.sfail(f"Could not follow symlink file: '{symlink_target_path}'.")
        else:
            raise RemoteExecuteException(f"Error executing remote command: '{command}'")