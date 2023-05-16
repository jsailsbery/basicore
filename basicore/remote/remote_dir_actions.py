import os
import logging
from typing import Optional, Dict
from .remote_command import RemoteCommand
from basicore.parameters.config_ssh import SSHConfig
from basicore.generic import Basic
from .remote_file_actions import RemoteFileActions, RemoteExecuteException

__all__ = ['RemoteDirActions']
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RemoteDirActions(Basic):

    @classmethod
    def exists(cls, directory: str, authentication: SSHConfig) -> bool:
        """
        Check if a source_dir exists on the remote server.

        Args:
            authentication (SSHConfig): The SSH configuration for connecting to the remote server.
            directory (str): The path of the source_dir to check.

        Returns:
            bool: True if the source_dir exists, False otherwise.
        """
        command = f'if [ -e "{directory}" ]; then exit 0; else exit 1; fi'
        results = RemoteCommand.execute(command=command, command_id='directory_exists', authentication=authentication)
        if results.completion:
            if results.success:
                return Basic.bpass(f"Directory '{directory}' exists.")
            elif results.errors:
                raise RemoteExecuteException(f"Directory '{directory}' existence could not be verified. {results}")
            else:
                return Basic.bfail(f"Directory '{directory}' does not exist.")
        else:
            raise RemoteExecuteException(f"Error executing remote command: '{command}'")

    @classmethod
    def isdir(cls, directory: str, authentication: SSHConfig) -> bool:
        """Check if a directory path.

        Args:
            directory (str): The directory to check.
            authentication (SSHConfig): The SSH configuration for connecting to the remote server.

        Returns:
            bool: True if the directory exists, False otherwise.
        """
        if not RemoteDirActions.exists(directory=directory, authentication=authentication):
            return False

        command = f'if [ -d "{directory}" ]; then exit 0; else exit 1; fi'
        results = RemoteCommand.execute(command=command, command_id='isdir', authentication=authentication)
        if results.completion:
            if results.success:
                return Basic.bpass(f"Directory '{directory}' is a directory.")
            elif results.errors:
                raise RemoteExecuteException(f"Directory '{directory}' type could not be verified. {results}")
            else:
                return Basic.bfail(f"Directory '{directory}' is not a directory.")
        else:
            raise RemoteExecuteException(f"Error executing remote command: '{command}'")

    @classmethod
    def create(cls, directory: str, authentication: SSHConfig) -> bool:
        """
        Create a source_dir on the remote server.

        Args:
            authentication (SSHConfig): The SSH configuration for connecting to the remote server.
            directory (str): The path of the source_dir to create.

        Returns:
            bool: True if the operation is successful, False otherwise.
        """
        if RemoteDirActions.isdir(directory=directory, authentication=authentication):
            return True

        command = f'mkdir -p "{directory}"'
        results = RemoteCommand.execute(command=command, command_id='create_directory',
                                        authentication=authentication)
        if results.completion:
            if results.success:
                return Basic.bpass(f"Directory '{directory}' created.")
            elif results.errors:
                raise RemoteExecuteException(f"Directory '{directory}' creation not confirmed. {results}")
            else:
                return Basic.bfail(f"Did not complete creating Directory '{directory}'.")
        else:
            raise RemoteExecuteException(f"Error executing remote command: '{command}'")

    @classmethod
    def delete(cls, directory: str, authentication: SSHConfig) -> bool:
        """
        Remove a source_dir and its contents on the remote server.

        Args:
            authentication (SSHConfig): The SSH configuration for connecting to the remote server.
            directory (str): The path of the source_dir to remove.

        Returns:
            bool: True if the operation is successful, False otherwise.
        """
        if not RemoteDirActions.exists(directory=directory, authentication=authentication):
            return True

        command = f'rm -rf {directory}'
        results = RemoteCommand.execute(command=command, command_id='remove_directory',
                                        authentication=authentication)
        if results.completion:
            if results.success:
                return Basic.bpass(f"Directory '{directory}' removed.")
            elif results.errors:
                raise RemoteExecuteException(f"Directory '{directory}' removal not confirmed. {results}")
            else:
                return Basic.bfail(f"Did not complete removing Directory '{directory}'.")
        else:
            raise RemoteExecuteException(f"Error executing remote command: '{command}'")

    @classmethod
    def list(cls, directory: str, authentication: SSHConfig) -> Optional[Dict[str, int]]:
        """
        Get the contents of a source_dir on the remote server, excluding broken symbolic links.
        If the content is a valid symbolic link, it returns the path that the symbolic link points to.

        Args:
            authentication (SSHConfig): The SSH configuration for connecting to the remote server.
            directory (str): The path of the source_dir to get contents from.

        Returns:
            Optional[Dict[str, int]]: A dictionary where keys are the absolute paths of the contents of the source_dir
            and values are their corresponding file sizes, if the operation is successful, None otherwise.
        """
        if not RemoteDirActions.exists(directory=directory, authentication=authentication):
            return None

        command = f'ls -l {directory}'
        results = RemoteCommand.execute(command=command, command_id='list_directory',
                                        authentication=authentication)
        if results.completion:
            if results.success:

                contents = results.stdout.strip().split('\n')
                directory_contents = {}

                for item in contents:
                    item_info = item.split()
                    if len(item_info) < 9:
                        continue

                    # Check if it is a symbolic link
                    if item_info[0].startswith('l'):
                        symlink_target_path = item_info[-1]
                        size = RemoteFileActions.follow(symlink_target_path, authentication)
                        if size is not None:
                            directory_contents[symlink_target_path] = size

                    else:  # Regular file or source_dir
                        size = int(item_info[4])
                        full_path = os.path.join(directory, item_info[-1])
                        directory_contents[full_path] = size

                logger.info(
                    f"Contents of '{directory}':\n" + '\n'.join(f'{k}: {v}' for k, v in directory_contents.items()))
                return directory_contents

            elif results.errors:
                raise RemoteExecuteException(f"Contents of '{directory}' removal not confirmed. {results}")
            else:
                return Basic.nfail(f"Did not complete listing contents of '{directory}'.")
        else:
            raise RemoteExecuteException(f"Error executing remote command: '{command}'")

    @classmethod
    def copy(cls, source_dir: str, destination_dir: str, authentication: SSHConfig) -> bool:
        """
        Copy the contents of one source_dir to another on the remote server.
        WARNING: this is not scp. Do not use this to move files between servers.

        Args:
            authentication (SSHConfig): The SSH configuration for connecting to the remote server.
            source_dir (str): The path of the source source_dir.
            destination_dir (str): The path of the destination_dir source_dir.

        Returns:
            bool: True if the operation is successful, False otherwise.
        """
        if not RemoteDirActions.exists(directory=source_dir, authentication=authentication):
            return False
        RemoteDirActions.create(destination_dir, authentication)

        command = f'cp -r {source_dir}/* {destination_dir}'
        results = RemoteCommand.execute(command=command, command_id='copy_directory_contents',
                                        authentication=authentication)
        if results.completion:
            if results.success:
                return Basic.bpass(f"Contents copied from '{source_dir}' to '{destination_dir}'.")
            elif results.errors:
                raise RemoteExecuteException(f"Copying of '{source_dir}' contents not confirmed. {results}")
            else:
                return Basic.bfail(f"Did not complete copying contents of '{source_dir}'.")
        else:
            raise RemoteExecuteException(f"Error executing remote command: '{command}'")

    @classmethod
    def remove(cls, directory: str, authentication: SSHConfig, exceptions: list = None) -> bool:
        """
        Remove all contents of a source_dir except for specified exceptions on the remote server.

        Args:
            authentication (SSHConfig): The SSH configuration for connecting to the remote server.
            directory (str): The path of the source_dir to remove contents from.
            exceptions (list): optional - A list of files to keep.

        Returns:
            bool: True if the operation is successful, False otherwise.
        """
        if not RemoteDirActions.exists(directory=directory, authentication=authentication):
            return True

        exception_args = ' '.join(f"--exclude='{exception}'" for exception in exceptions) if exceptions else ""
        command = f'cd {directory} && rm -rf ./* {exception_args}'
        results = RemoteCommand.execute(command=command, command_id='remove_dir_contents',
                                        authentication=authentication)
        if results.completion:
            if results.success:
                return Basic.bpass(f"Contents removed from '{directory}' except for specified values.")
            elif results.errors:
                raise RemoteExecuteException(f"Contents of '{directory}' removal not confirmed. {results}")
            else:
                return Basic.bfail(f"Did not complete removing contents of '{directory}'.")
        else:
            raise RemoteExecuteException(f"Error executing remote command: '{command}'")
