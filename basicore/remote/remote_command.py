import time
import socket
import logging
import paramiko
from scp import SCPClient
from typing import Any, Tuple
from dataclasses import dataclass
from basicore.parameters.config_ssh import SSHConfig

__all__ = ['RemoteCommand', 'RemoteResults', 'RemoteConnection', 'RemoteExecuteException']
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


class RemoteExecuteException(Exception):
    """Custom exception class for remote execution errors."""

    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f'Remote execution error: {self.message}'


@dataclass
class RemoteResults:
    """
    A dataclass for storing the results of a command executed on a remote server.

    Attributes:
    command (str): The command that was executed.
    command_id (str): An identifier for the command.
    stdout (str): The standard output from the command. Initialized as an empty string.
    stderr (str): The standard error from the command. Initialized as an empty string.
    exit_code (int): The exit status of the command. Initialized as -1.
    errors (bool): Whether any errors were detected in the stdout or stderr. Initialized as False.
    success (bool): Whether the command was executed successfully. Initialized as False.
    completion (bool): Whether the command has completed execution. Initialized as False.
    """
    command: str
    command_id: str
    stdout: str = ""
    stderr: str = ""
    exit_code: int = -1
    errors: bool = False
    success: bool = False
    completion: bool = False

    def __init__(self, command: str = "", command_id: str = ""):
        """
        Initialize a RemoteResults instance.

        Args:
        command (str): The command that was executed. Defaults to an empty string.
        command_id (str): An identifier for the command. Defaults to an empty string.
        """
        self.command = command
        self.command_id = command_id

    def __repr__(self):
        """
        Generate a string representation of the RemoteResults instance.

        Returns:
        str: A string representation of the RemoteResults instance.
        """
        repr_string = (
            f"RemoteResults(\n"
            f"\tcommand_id: {self.command_id},\n"
            f"\tcommand: {self.command},\n"
            f"\tstdout: {self.stdout},\n"
            f"\tstderr: {self.stderr},\n"
            f"\texit_code: {self.exit_code},\n"
            f"\terrors: {self.errors},\n"
            f"\tsuccess: {self.success},\n"
            f"\tcompletion: {self.completion}\n"
            ")"
        )
        return repr_string

    def determine_errors(self):
        """
        Check the stdout and stderr for errors.

        If the word "ERROR" is found in the stdout or stderr (case-insensitive), the errors attribute is set to True.
        """
        if "ERROR" in self.stdout.upper():
            logger.info(f"Command failure in stdout: {self}")
            self.errors = True
        elif "ERROR" in self.stderr.upper():
            logger.info(f"Command failure in stderr: {self}")
            self.errors = True

    def determine_success(self):
        """
        Set the success attribute based on the errors attribute and the exit code.

        If the errors attribute is True or the exit code is not zero, the success attribute is set to False.
        Otherwise, the success attribute is set to True.
        """
        self.determine_errors()
        if self.errors or self.exit_code != 0:
            logger.info(f"Command exited with error status: {self}")
            self.success = False
        else:
            logger.info(f"{self.command_id}: Command completed successfully.")
            self.success = True


class RemoteConnection:
    """
    A class to establish and manage a connection to a remote server using SSH.

    Attributes:
    conn (paramiko.SSHClient): The SSH client. Initialized as None.
    authentication (SSHConfig): The SSH authentication configuration.
    """

    conn: paramiko.SSHClient = None
    authentication: SSHConfig = None
    error_message: str = ""

    def __init__(self, authentication: SSHConfig):
        """
        Initialize a RemoteConnection instance.

        Args:
        authentication (SSHConfig): The SSH authentication configuration.
        """
        self.authentication = authentication
        self.connect()

    def __del__(self):
        """
        Clean up when the RemoteConnection instance is being destroyed.

        If the conn attribute is not None, the SSH connection is closed.
        """
        if self.conn is not None:
            self.conn.close()

    def _set_error(self, msg: str):
        self.error_message = msg
        logger.error(msg)

    def connect(self) -> bool:
        """
        Connect to the remote server using SSH.
        """
        try:
            if self.conn is None:
                self.conn = paramiko.SSHClient()
                self.conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                self.conn.connect(
                    self.authentication.remote_server,
                    port=self.authentication.ssh_port,
                    username=self.authentication.ssh_user,
                    password=self.authentication.ssh_pswd
                )
                return True
        except paramiko.AuthenticationException:
            self.conn = None
            self._set_error(f"ERROR: Failed to log in to remote server. {self.authentication}")
        return False

    def exec_command(self, command: str, bufsize: int = -1, timeout: int = None, get_pty: bool = False,
                     environment: dict = None) -> Tuple[Any, str, str, int]:
        """
        Execute a command on the remote server.

        Args:
        command (str): The command to execute.
        bufsize (int, optional): The buffer size. Defaults to -1.
        timeout (int, optional): The timeout for the command in seconds. Defaults to None.
        get_pty (bool, optional): Whether to get a pseudo-terminal for the command. Defaults to False.
        environment (dict, optional): The environment variables for the command. Defaults to None.

        Returns:
        Tuple[Any, str, str, int]: A tuple containing the standard input, standard output, standard error, and exit status of the command.
        """
        stdin, stdout, stderr, exit_status = ["", "", "", -1]
        if not self.connect():
            return stdin, stdout, self.error_message, exit_status

        try:
            # Connect to remote server using SSH and Execute command
            stdin, stdout, stderr = self.conn.exec_command(command=command, bufsize=bufsize, timeout=timeout,
                                                           get_pty=get_pty, environment=environment)

            # Wait for command to finish and capture its exit status
            exit_status = -1
            while exit_status == -1:
                if not stdout.channel.exit_status_ready():
                    time.sleep(20)  # Wait 20 sec before checking again
                else:
                    exit_status = stdout.channel.recv_exit_status()

            stdout = stdout.read().decode().strip()
            stderr = stderr.read().decode().strip()

        except paramiko.SSHException as e:
            self._set_error(f"ERROR: SSH error while waiting for command to finish: {str(e)}")
        except socket.timeout as e:
            self._set_error(f"ERROR: Socket timed out while waiting for command to finish. {str(e)}")
        except socket.error as e:
            self._set_error(f"ERROR: Socket error while waiting for command to finish: {str(e)}")

        stderr = stderr+"\n >"+self.error_message if stderr else self.error_message
        return stdin, stdout, stderr, exit_status


class RemoteCommand:
    """
    A class providing utility methods to execute commands and transfer files on a remote server via SSH.
    """

    @classmethod
    def execute(cls, command: str, command_id: str, ssh: RemoteConnection) -> RemoteResults:
        """
        Execute a command on a remote server and return the results.

        Args:
            command (str): The command to be executed on the remote server.
            command_id (str): An identifier for the command.
            ssh (RemoteConnection): The SSH connection to the remote server.

        Returns:
            RemoteResults: An object containing the results of the executed command including standard output,
                           standard error, exit status, success status, and completion status.
        """
        # Execute the command
        stdin, stdout, stderr, exit_code = ssh.exec_command(command)

        # Prepare the command results
        res = RemoteResults(command=command, command_id=command_id)
        res.stdout = stdout
        res.stderr = stderr
        res.exit_code = exit_code
        res.completion = True

        res.determine_success()
        return res

    @classmethod
    def scp(cls, source: str, destination: str, ssh: RemoteConnection, put: bool = True) -> RemoteResults:
        """
        Securely copies a file or directory from the source to the destination using SCP.

        Args:
            source (str): The path to the source file or directory.
            destination (str): The path to the destination file or directory.
            ssh (RemoteConnection): The SSH connection to the remote server.
            put (bool, optional): If True, the source is the local path and the destination is the remote path (uploading).
                                  If False, the source is the remote path and the destination is the local path (downloading).
                                  Default is True (uploading).

        Returns:
            RemoteResults: A RemoteResults object containing the results of the SCP operation, including the success status,
                           the command that was executed, the identifier for the command, and any output or error messages.
        """
        command_id = "scp_put" if put else "scp_get"
        res = RemoteResults(command=f"scp {source} {destination}", command_id=command_id)

        try:
            # Perform SCP operation
            with SCPClient(ssh.conn.get_transport()) as scp:
                if put:
                    scp.put(source, destination, recursive=False)
                else:
                    scp.get(source, destination, recursive=False)

                res.exit_code = 0
                res.completion = True

        except paramiko.SSHException as e:
            res.stderr = f"ERROR: SSH error while waiting for command to finish: {str(e)}"
            logger.error(res.stderr)
        except socket.timeout as e:
            res.stderr = f"ERROR: Socket timed out while waiting for command to finish. {str(e)}"
            logger.error(res.stderr)
        except socket.error as e:
            res.stderr = f"ERROR: Socket error while waiting for command to finish: {str(e)}"
            logger.error(res.stderr)

        if ssh.conn is None:
            res.stderr = f"ERROR: Failed to log in to remote server. {ssh.authentication}"
        res.determine_success()
        return res
