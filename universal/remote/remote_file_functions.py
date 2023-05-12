from .remote_command import RemoteCommand
from .config_ssh import SSHConfig

class RemoteFileActions:

    @classmethod
    def follow_symlink(cls, symlink_target_path: str, authentication: SSHConfig) -> int:
        """
        Check if a path exists in the remote system and return its size.

        Args:
            symlink_target_path (str): The path to check.
            authentication (SSHConfig): The SSH configuration for connecting to the remote server.

        Returns:
            int: The size of the path if it exists, -1 otherwise.
        """
        check_link_command = f'if [ -e "{symlink_target_path}" ]; then du -b "{symlink_target_path}"; fi'
        check_command = RemoteCommand(command=check_link_command, command_id='check_symlink_target')
        if check_command.execute(authentication):
            size_info = check_command.stdout.strip().split('\t')
            if len(size_info) == 2:
                return int(size_info[0])
        return -1