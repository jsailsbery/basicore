import time
import socket
import logging
import paramiko
from dataclasses import dataclass
from .config_ssh import SSHConfig
__all__ = ['RemoteCommand']

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


@dataclass
class RemoteCommand:
    """
    A dataclass for storing the details of a command to be executed on a remote server.

    Attributes:
    command (str): The command that will be executed.
    command_id (str): An identifier for the command.
    stdout (str): The standard output from the command. Initialized as an empty string.
    stderr (str): The standard error from the command. Initialized as an empty string.
    exit_code (int): The exit status of the command. Initialized as -1.
    success (bool): Whether the command was executed successfully. Initialized as False.
    """
    command: str
    command_id: str
    stdout: str = ""
    stderr: str = ""
    exit_code: int = -1
    success: bool = False

    def __repr__(self):
        val = f"RemoteCommand(command_id:{self.command_id}, exit_code:{self.exit_code}, success:{self.success}):\n" \
              f"    command:{self.command}\n    stdout:{self.stdout}\n  stderr:{self.stderr}"
        return val

    def _set_error(self, description: str, ssh_client: paramiko.SSHClient = None) -> bool:
        self.stderr = description
        self.success = False
        logger.error(f"ERROR: {str(self)}")
        ssh_client.close()
        return False

    def execute(self, authentication: SSHConfig) -> bool:
        """
        Execute a command on a remote server and return the results.

        This function connects to a remote server via SSH, executes a command, and waits for the command to finish.
        It modifies the given RemoteCommand object with the standard output, standard error, exit status,
        and success of the command.

        Args:
        authentication (SSHConfig): The SSH configuration for connecting to the remote server.

        Returns:
        None
        """
        # Connect to remote server using SSH
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(
                authentication.remote_server,
                port=authentication.ssh_port,
                username=authentication.ssh_user,
                password=authentication.ssh_pswd
            )

        except paramiko.AuthenticationException:
            return self._set_error("Failed to log in to remote server.", ssh)
        except paramiko.SSHException as e:
            return self._set_error(f"SSH connection error: {str(e)}", ssh)

        # Execute command
        stdin, stdout, stderr = ssh.exec_command(self.command)

        # Wait for command to finish and capture its exit status
        exit_status = -1
        while not stdout.channel.exit_status_ready():
            time.sleep(60)  # Wait 1 minute before checking again
            try:
                exit_status = stdout.channel.recv_exit_status()
            except paramiko.SSHException as e:
                return self._set_error(f"SSH error while waiting for command to finish: {str(e)}", ssh)
            except socket.timeout:
                return self._set_error(f"Socket timed out while waiting for command to finish.", ssh)
            except socket.error as e:
                return self._set_error(f"Socket error while waiting for command to finish: {str(e)}", ssh)

        # Check for specific errors from the command
        self.stdout = stdout.read().decode().strip()
        self.stderr = stderr.read().decode().strip()
        self.exit_code = exit_status

        # Hunt for errors
        if "ERROR" in self.stdout.upper():
            self._set_error(f"Command failure in stdout.", ssh)
        elif "ERROR" in self.stderr.upper():
            self._set_error(f"Command failure in stderr.", ssh)
        elif self.exit_code != 0:
            self._set_error(f"Command exited with error status.", ssh)

        else:
            # Close SSH connection and update this object with updated results
            self.success = True
            logger.info(f"{self.command_id}: Command completed successfully.")
            ssh.close()

        return True
