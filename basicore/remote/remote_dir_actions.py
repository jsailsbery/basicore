import os
import logging
from typing import Optional, Dict
from basicore.generic import Basic
from .remote_command import RemoteCommand, RemoteConnection, RemoteExecuteException
from .remote_file_actions import RemoteFileActions

__all__ = ['RemoteDirActions']
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RemoteDirActions(Basic):

    @classmethod
    def exists(cls, directory: str, ssh: RemoteConnection) -> bool:
        """
        Check if a source_dir exists on the remote server.

        Args:
            directory (str): The path of the source_dir to check.
            ssh (RemoteConnection): The SSH connection to the remote server.

        Returns:
            bool: True if the source_dir exists, False otherwise.
        """
        command = f'if [ -e "{directory}" ]; then echo 0; else echo 1; fi'
        results = RemoteCommand.execute(command=command, command_id='directory_exists', ssh=ssh)
        if results.completion:
            if results.stdout == "0":
                return Basic.bpass(f"Directory '{directory}' exists.")
            elif results.errors:
                raise RemoteExecuteException(f"Directory '{directory}' existence could not be verified. {results}")
            else:
                return Basic.bfail(f"Directory '{directory}' does not exist.")
        else:
            raise RemoteExecuteException(f"Error executing remote command: '{command}'")

    @classmethod
    def isdir(cls, directory: str, ssh: RemoteConnection) -> bool:
        """Check if a directory path.

        Args:
            directory (str): The directory to check.
            ssh (RemoteConnection): The SSH connection to the remote server.

        Returns:
            bool: True if the directory exists, False otherwise.
        """
        if not RemoteDirActions.exists(directory=directory, ssh=ssh):
            return False

        command = f'if [ -d "{directory}" ]; then exit 0; else exit 1; fi'
        results = RemoteCommand.execute(command=command, command_id='isdir', ssh=ssh)
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
    def create(cls, directory: str, ssh: RemoteConnection) -> bool:
        """
        Create a source_dir on the remote server.

        Args:
            directory (str): The path of the source_dir to create.
            ssh (RemoteConnection): The SSH connection to the remote server.

        Returns:
            bool: True if the operation is successful, False otherwise.
        """
        if RemoteDirActions.isdir(directory=directory, ssh=ssh):
            return True

        command = f'mkdir -p "{directory}"'
        results = RemoteCommand.execute(command=command, command_id='create_directory', ssh=ssh)
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
    def delete(cls, directory: str, ssh: RemoteConnection) -> bool:
        """
        Remove a source_dir and its contents on the remote server.

        Args:
            directory (str): The path of the source_dir to remove.
            ssh (RemoteConnection): The SSH connection to the remote server.

        Returns:
            bool: True if the operation is successful, False otherwise.
        """
        if not RemoteDirActions.exists(directory=directory, ssh=ssh):
            return True

        command = f'rm -rf {directory}'
        results = RemoteCommand.execute(command=command, command_id='remove_directory', ssh=ssh)
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
    def list(cls, directory: str, ssh: RemoteConnection) -> Optional[Dict[str, int]]:
        """
        Get the contents of a source_dir on the remote server, excluding broken symbolic links.
        If the content is a valid symbolic link, it returns the path that the symbolic link points to.

        Args:
            directory (str): The path of the source_dir to get contents from.
            ssh (RemoteConnection): The SSH connection to the remote server.

        Returns:
            Optional[Dict[str, int]]: A dictionary where keys are the absolute paths of the contents of the source_dir
            and values are their corresponding file sizes, if the operation is successful, None otherwise.
        """
        if not RemoteDirActions.exists(directory=directory, ssh=ssh):
            return None

        command = f'ls -l {directory}'
        results = RemoteCommand.execute(command=command, command_id='list_directory', ssh=ssh)
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
                        size = RemoteFileActions.follow(symlink_target_path, ssh=ssh)
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
    def copy(cls, source_dir: str, destination_dir: str, ssh: RemoteConnection) -> bool:
        """
        Copy the contents of one source_dir to another on the remote server.
        WARNING: this is not scp. Do not use this to move files between servers.

        Args:
            source_dir (str): The path of the source source_dir.
            destination_dir (str): The path of the destination_dir source_dir.
            ssh (RemoteConnection): The SSH connection to the remote server.

        Returns:
            bool: True if the operation is successful, False otherwise.
        """
        if not RemoteDirActions.exists(directory=source_dir, ssh=ssh):
            return False
        RemoteDirActions.create(destination_dir, ssh=ssh)

        command = f'cp -r {source_dir}/* {destination_dir}'
        results = RemoteCommand.execute(command=command, command_id='copy_directory_contents', ssh=ssh)
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
    def remove(cls, directory: str, ssh: RemoteConnection, exceptions: list = None) -> bool:
        """
        Remove all contents of a source_dir except for specified exceptions on the remote server.

        Args:
            directory (str): The path of the source_dir to remove contents from.
            exceptions (list): optional - A list of files to keep.
            ssh (RemoteConnection): The SSH connection to the remote server.

        Returns:
            bool: True if the operation is successful, False otherwise.
        """
        if not RemoteDirActions.exists(directory=directory, ssh=ssh):
            return True

        exception_args = ' '.join(f"--exclude='{exception}'" for exception in exceptions) if exceptions else ""
        command = f'cd {directory} && rm -rf ./* {exception_args}'
        results = RemoteCommand.execute(command=command, command_id='remove_dir_contents', ssh=ssh)
        if results.completion:
            if results.success:
                return Basic.bpass(f"Contents removed from '{directory}' except for specified values.")
            elif results.errors:
                raise RemoteExecuteException(f"Contents of '{directory}' removal not confirmed. {results}")
            else:
                return Basic.bfail(f"Did not complete removing contents of '{directory}'.")
        else:
            raise RemoteExecuteException(f"Error executing remote command: '{command}'")
