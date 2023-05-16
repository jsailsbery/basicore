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
        remote_command = f'if [ -e "{filepath}" ]; then exit 0; else exit 1; fi'
        remote_results = RemoteCommand.execute(command=remote_command, command_id='check_file_command',
                                               authentication=authentication)
        if remote_results.completion:
            if remote_results.success:
                return Basic.bpass(f"File '{filepath}' exists.")
            else:
                return Basic.bfail(f"File '{filepath}' does not exist.")
        else:
            raise RemoteExecuteException(f"Error executing remote command: '{remote_command}'")

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
        remote_command = f'if [ -f "{filepath}" ]; then exit 0; else exit 1; fi'
        command = RemoteCommand(command=remote_command, command_id='check_file_command')
        if command.execute(authentication):
            if command.exit_code == 0:
                return Basic.bpass(f"File '{filepath}' is a file.")
            else:
                return Basic.bfail(f"File '{filepath}' is not a file.")
        else:
            raise RemoteExecuteException(f"Error executing remote command: '{remote_command}'")

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
        remote_command = f'rm -f {filepath}'
        command = RemoteCommand(command=remote_command, command_id='remove_file')
        if command.execute(authentication):
            if command.exit_code == 0:
                return Basic.bpass(f"File '{filepath}' removed.")
            else:
                return Basic.bfail(f"Did not complete removing source_dir '{filepath}'.")
        else:
            raise RemoteExecuteException(f"Error executing remote command: '{remote_command}'")

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
        remote_command = f'cat {filepath}'
        command = RemoteCommand(command=remote_command, command_id='read_file')
        if command.execute(authentication):
            if command.exit_code == 0:
                content = command.stdout
                try:
                    return json.loads(content)  # Try parsing as JSON dict or list
                except json.JSONDecodeError:
                    return content  # Return as plain text if parsing fails
            else:
                return Basic.sfail(f"Failed to read {filepath}.")
        else:
            raise RemoteExecuteException(f"Error executing remote command: '{remote_command}'")

    @classmethod
    def write(cls, filepath: str, data: Union[str, list, dict], authentication: SSHConfig, mode: str = "w") -> bool:
        """
        Writes data to a file on a remote system.

        Parameters:
            filepath (str): The path of the file to write on the remote system.
            data (Union[str, list, dict]): The data to write to the file. If it's a list or dict, it will be converted to a string using JSON.
            authentication (SSHConfig): The authentication configuration for the remote system.
            mode (str): The file mode to be used for writing. Default is "w" (write). "a" for append.

        Returns:
            bool: True if the operation was successful, False otherwise.
        Raises:
            RemoteExecuteException: If an error occurs while executing the remote command.
        """
        try:
            if isinstance(data, (list, dict)):
                data = json.dumps(data)

            # Write the data to a temporary file on the local system
            with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp:
                tmp.write(data)
                tmp_file = tmp.name

            # Use scp to copy the file to the remote system
            command = RemoteCommand(command="", command_id='write_file')
            if command.scp(tmp_file, filepath, authentication):
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
        remote_command = f'if [ -e "{symlink_target_path}" ]; then readlink -f "{symlink_target_path}"; fi'
        command = RemoteCommand(command=remote_command, command_id='follow_link_command')
        if command.execute(authentication):
            if command.exit_code == 0:
                return Basic.spass(command.stdout, f"Symlink: '{symlink_target_path}' target: {command.stdout}.")
            else:
                return Basic.sfail(f"Could not follow symlink file: '{symlink_target_path}'.")
        else:
            raise RemoteExecuteException(f"Error executing remote command: '{remote_command}'")