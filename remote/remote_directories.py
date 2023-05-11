import logging
from typing import Optional, List
from remote_command import RemoteCommand
from config_ssh import SSHConfig

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RemoteDirectory:

    @classmethod
    def exists(cls, directory: str, authentication: SSHConfig) -> bool:
        """
        Check if a directory exists on the remote server.

        Args:
            authentication (SSHConfig): The SSH configuration for connecting to the remote server.
            directory (str): The path of the directory to check.

        Returns:
            bool: True if the directory exists, False otherwise.
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
        Create a directory on the remote server.

        Args:
            authentication (SSHConfig): The SSH configuration for connecting to the remote server.
            directory (str): The path of the directory to create.

        Returns:
            bool: True if the operation is successful, False otherwise.
        """
        if not RemoteDirectory.exists(directory=directory, authentication=authentication):

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
    def copy(cls, source_dir: str, destination_dir: str, authentication: SSHConfig) -> bool:
        """
        Copy the contents of one directory to another on the remote server.

        Args:
            authentication (SSHConfig): The SSH configuration for connecting to the remote server.
            source_dir (str): The path of the source directory.
            destination_dir (str): The path of the destination directory.

        Returns:
            bool: True if the operation is successful, False otherwise.
        """
        copy_command = f'scp -r {source_dir}/* {destination_dir}'
        command = RemoteCommand(command=copy_command, command_id='copy_directory')
        if command.execute(authentication):
            logger.info(f"Contents copied from '{source_dir}' to '{destination_dir}'.")
            return True
        logger.info(f"Did not complete copy contents command: '{source_dir}' to '{destination_dir}'.")
        return False

    @classmethod
    def remove_contents(cls, directory: str, authentication: SSHConfig, exceptions: list = None) -> bool:
        """
        Remove all contents of a directory except for specified exceptions on the remote server.

        Args:
            authentication (SSHConfig): The SSH configuration for connecting to the remote server.
            directory (str): The path of the directory to remove contents from.
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

    @classmethod
    def list_contents(cls, directory: str, authentication: SSHConfig) -> Optional[List[str]]:
        """
        Get the contents of a directory on the remote server.

        Args:
            authentication (SSHConfig): The SSH configuration for connecting to the remote server.
            directory (str): The path of the directory to get contents from.

        Returns:
            Optional[List[str]]: A list of items in the directory if the operation is successful, None otherwise.
        """
        get_command = f'ls {directory}'
        command = RemoteCommand(command=get_command, command_id='get_directory_contents')
        if command.execute(authentication):
            contents = command.stdout.strip().split('\n')
            logger.info(f"Contents of '{directory}':\n" + '\n'.join(contents))
            return contents
        logger.info(f"Could not list contents of '{directory}' ")
        return None
