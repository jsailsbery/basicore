import os
import logging
from typing import Optional, Dict
from .remote_command import RemoteCommand
from universal.parameters.config_ssh import SSHConfig
from .remote_file_functions import RemoteFileActions
__all__ = ['RemoteDirActions']

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RemoteDirActions:

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
        check_directory_command = f'if [ -d "{directory}" ]; then exit 0; else exit 1; fi'
        command = RemoteCommand(command=check_directory_command, command_id='check_directory_exists')
        if command.execute(authentication):
            if command.exit_code == 0:
                logger.info(f"Directory '{directory}' exists.")
                return True
            else:
                logger.info(f"Directory '{directory}' does not exist.")
                return False
        return False

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
        if not RemoteDirActions.exists(directory=directory, authentication=authentication):

            # Directory does not exist, create it
            create_directory_command = f'mkdir -p "{directory}"'
            command = RemoteCommand(command=create_directory_command, command_id='create_directory')
            if command.execute(authentication):
                if command.success:
                    logger.info(f"Directory '{directory}' created.")
                    return True
        else:
            logger.info(f"Directory '{directory}' already exists.")
        return False

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
        remove_command = f'rm -rf {directory}'
        command = RemoteCommand(command=remove_command, command_id='remove_directory')
        if command.execute(authentication):
            logger.info(f"Directory '{directory}' removed.")
            return True
        logger.info(f"Did not complete removing source_dir '{directory}'.")
        return False

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
        get_command = f'ls -l {directory}'
        command = RemoteCommand(command=get_command, command_id='get_directory_contents')
        if command.execute(authentication):
            contents = command.stdout.strip().split('\n')
            directory_contents = {}

            for item in contents:
                item_info = item.split()
                if len(item_info) < 9:
                    continue

                # Check if it is a symbolic link
                if item_info[0].startswith('l'):
                    symlink_target_path = item_info[-1]
                    size = RemoteFileActions.follow_symlink(symlink_target_path, authentication)
                    if size is not None:
                        directory_contents[symlink_target_path] = size

                else:  # Regular file or source_dir
                    size = int(item_info[4])
                    full_path = os.path.join(directory, item_info[-1])
                    directory_contents[full_path] = size

            logger.info(f"Contents of '{directory}':\n" + '\n'.join(f'{k}: {v}' for k, v in directory_contents.items()))
            return directory_contents

        logger.info(f"Could not list contents of '{directory}' ")
        return None

    @classmethod
    def copy(cls, source_dir: str, destination_dir: str, authentication: SSHConfig) -> bool:
        """
        Copy the contents of one source_dir to another on the remote server.

        Args:
            authentication (SSHConfig): The SSH configuration for connecting to the remote server.
            source_dir (str): The path of the source source_dir.
            destination_dir (str): The path of the destination_dir source_dir.

        Returns:
            bool: True if the operation is successful, False otherwise.
        """
        # ensure destination_dir dir exists
        RemoteDirActions.create(directory=destination_dir, authentication=authentication)

        copy_command = f'scp -r {source_dir}/* {destination_dir}'
        command = RemoteCommand(command=copy_command, command_id='copy_directory')
        if command.execute(authentication):
            logger.info(f"Contents copied from '{source_dir}' to '{destination_dir}'.")
            return True
        logger.info(f"Did not complete copy contents command: '{source_dir}' to '{destination_dir}'.")
        return False

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
        exception_args = ' '.join(f"--exclude='{exception}'" for exception in exceptions) if exceptions else ""
        remove_command = f'cd {directory} && rm -rf ./* {exception_args}'
        command = RemoteCommand(command=remove_command, command_id='remove_directory_contents')
        if command.execute(authentication):
            logger.info(f"Contents removed from '{directory}' except for specified values.")
            return True
        logger.info(f"Did not complete removing contents from '{directory}' except for specified values.")
        return False
