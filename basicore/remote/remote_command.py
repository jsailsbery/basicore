import time
import json
import socket
import logging
import paramiko
from scp import SCPClient
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
    success (bool): Whether the command was executed successfully (no errors, graceful exit). Initialized as False.
    completion (bool): Whether the command has completed execution. Initialized as False.
    stdin (str): The standard input for the command. Initialized as an empty string.
    """
    command: str
    command_id: str
    stdin: str = ""
    stdout: str = ""
    stderr: str = ""
    exit_code: int = -1
    completion: bool = False
    success: bool = False
    errors: bool = False

    def __init__(self, **kwargs):
        """
        Initialize a RemoteResults instance.

        Args:
        command (str): The command that was executed. Defaults to an empty string.
        command_id (str): An identifier for the command. Defaults to an empty string.
        """
        self.__dict__.update(**kwargs)

    def __repr__(self) -> str:
        """
        Generate a string representation of the RemoteResults instance.

        Returns:
        str: A string representation of the RemoteResults instance.
        """
        return f"RemoteResults({json.dumps(self.__dict__)})"

    def add_to_stderr(self, msg: str = "") -> None:
        """
        Append a message to the standard error output.

        Args:
        msg (str): The message to append. Defaults to an empty string.
        """
        self.stderr = f"{self.stderr}\n >{msg}" if self.stderr else msg

    def determine_states(self, completion: bool = False) -> None:
        """
        Check the stdout and stderr for errors and update the status attributes.

        Set the success attribute based on the errors attribute and the exit code.
        If the errors attribute is True or the exit code is not zero, the success attribute is set to False.
        Otherwise, the success attribute is set to True.

        Args:
        completion (bool): Whether the command has completed execution. Defaults to False.
        """
        self.completion = completion

        self.errors = "ERROR" in self.stdout.upper() or "ERROR" in self.stderr.upper()
        if self.errors:
            logger.info(f"Command failure detected: {self}")

        if self.errors or not self.completion or self.exit_code != 0:
            logger.info(f"Command exited with error status: {self}")
            self.success = False
        else:
            logger.info(f"{self.command_id}: Command completed successfully.")
            self.success = True


class RemoteConnection:
    """
    A class to establish and manage a connection to a remote server using SSH.

    Attributes:
    client (Optional[paramiko.SSHClient]): The SSH client. Initialized as None.
    authentication (SSHConfig): The SSH authentication configuration.
    """
    client: paramiko.SSHClient = None
    authentication: SSHConfig = None

    def __init__(self, authentication: SSHConfig):
        """
        Initialize a RemoteConnection instance.

        Args:
        authentication (SSHConfig): The SSH authentication configuration.
        """
        self.authentication = authentication
        self.connect()

    def __del__(self) -> None:
        """
        Clean up when the RemoteConnection instance is being destroyed.
        If the client attribute is not None, the SSH connection is closed.
        """
        if self.client is not None:
            self.client.close()

    def connect(self) -> str:
        """
        Connect to the remote server using SSH.

        Returns:
        str: Returns an error message string if any error occurred, else returns an empty string.
        """
        try:
            if self.client is None:
                self.client = paramiko.SSHClient()
                self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                self.client.connect(
                    self.authentication.remote_server,
                    port=self.authentication.ssh_port,
                    username=self.authentication.ssh_user,
                    password=self.authentication.ssh_pswd
                )
        except paramiko.AuthenticationException as e:
            self.client = None
            return f"ERROR: Failed to log in to remote server. {self.authentication}. {str(e)}"
        return ""


class RemoteCommand:
    """
    A class providing utility methods to execute commands and transfer files on a remote server via SSH.
    """
    INIT_WAIT_TIME = 1
    LOOP_WAIT_TIME = 15

    @classmethod
    def execute(cls, command: str, command_id: str, ssh: RemoteConnection, bufsize: int = -1,
                timeout: int = None, get_pty: bool = False, environment: dict = None) -> RemoteResults:
        """
        Execute a command on the remote server.

        Args:
        command (str): The command to be executed on the remote server.
        command_id (str): An identifier for the command.
        ssh (RemoteConnection): The SSH connection to the remote server.
        bufsize (int, optional): The buffer size. Defaults to -1.
        timeout (int, optional): The timeout for the command in seconds. Defaults to None.
        get_pty (bool, optional): Whether to get a pseudo-terminal for the command. Defaults to False.
        environment (dict, optional): The environment variables for the command. Defaults to None.

        Returns:
        RemoteResults: An instance of RemoteResults containing the standard input, standard output, standard error, and
        exit status of the command.
        """
        results = RemoteResults(command=command, command_id=command_id)
        if (emsg := ssh.connect()) != "":
            results.add_to_stderr(emsg)
            results.determine_states(completion=False)
            return results

        try:
            # Connect to remote server using SSH and Execute command
            stdin, stdout, stderr = ssh.client.exec_command(command=command, bufsize=bufsize, timeout=timeout,
                                                            get_pty=get_pty, environment=environment)
            time.sleep(RemoteCommand.INIT_WAIT_TIME)

            # Wait for command to finish and capture its exit status
            results.exit_code = -1
            while results.exit_code == -1:
                if not stdout.channel.exit_status_ready():
                    time.sleep(RemoteCommand.LOOP_WAIT_TIME)
                else:
                    results.exit_code = stdout.channel.recv_exit_status()

            # set in cli results
            #results.stdin = stdin.read().decode().strip() if stdin else ""
            results.stdout = "\n".join([line.strip() for line in stdout.readlines()]) if stdout else ""
            results.stderr = "\n".join([line.strip() for line in stdout.readlines()]) if stdout else ""
            results.determine_states(completion=True)

        except paramiko.SSHException as e:
            results.add_to_stderr(f"ERROR: SSH error while waiting for command to finish: {str(e)}")
            results.determine_states(completion=False)
        except socket.timeout as e:
            results.add_to_stderr(f"ERROR: Socket timed out while waiting for command to finish. {str(e)}")
            results.determine_states(completion=False)
        except socket.error as e:
            results.add_to_stderr(f"ERROR: Socket error while waiting for command to finish: {str(e)}")
            results.determine_states(completion=False)

        return results

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
                              Defaults to True (uploading).

        Returns:
        RemoteResults: A RemoteResults object containing the results of the SCP operation, including the success status,
                       the command that was executed, the identifier for the command, and any output or error messages.
        """
        command = f"scp {source} {destination}"
        command_id = "scp_put" if put else "scp_get"
        results = RemoteResults(command=command, command_id=command_id)

        if (emsg := ssh.connect()) != "":
            results.add_to_stderr(emsg)
            results.determine_states(completion=False)
            return results

        try:
            # Perform SCP operation
            with SCPClient(ssh.client.get_transport()) as scp:
                if put:
                    scp.put(source, destination, recursive=False)
                else:
                    scp.get(source, destination, recursive=False)

                # set in cli results
                results.exit_code = 0
                results.determine_states(completion=True)

        except paramiko.SSHException as e:
            results.add_to_stderr(f"ERROR: SSH error while waiting for command to finish: {str(e)}")
            results.determine_states(completion=False)
        except socket.timeout as e:
            results.add_to_stderr(f"ERROR: Socket timed out while waiting for command to finish. {str(e)}")
            results.determine_states(completion=False)
        except socket.error as e:
            results.add_to_stderr(f"ERROR: Socket error while waiting for command to finish: {str(e)}")
            results.determine_states(completion=False)

        return results
