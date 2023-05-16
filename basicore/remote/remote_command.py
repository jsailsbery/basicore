import time
import socket
import logging
import paramiko
from scp import SCPClient
from dataclasses import dataclass
from basicore.parameters.config_ssh import SSHConfig

__all__ = ['RemoteCommand', 'RemoteResults', 'RemoteExecuteException']
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

    def set_errors(self):
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

    def set_success(self):
        """
        Set the success attribute based on the errors attribute and the exit code.

        If the errors attribute is True or the exit code is not zero, the success attribute is set to False.
        Otherwise, the success attribute is set to True.
        """
        self.set_errors()
        if self.errors or self.exit_code != 0:
            logger.info(f"Command exited with error status: {self}")
            self.success = False
        else:
            logger.info(f"{self.command_id}: Command completed successfully.")
            self.success = True


class RemoteCommand:
    """
    A dataclass for storing the details of a command to be executed on a remote server.
    """
    @classmethod
    def _set_error(cls, results: RemoteResults, description: str) -> RemoteResults:
        results.stderr = description if not results.stderr else f"{results.stderr}\n{description}"
        results.completion = False
        logger.error(f"ERROR: {str(results)}")
        return results

    @classmethod
    def _ssh_setup(cls, authentication: SSHConfig):
        # Connect to remote server using SSH
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            authentication.remote_server,
            port=authentication.ssh_port,
            username=authentication.ssh_user,
            password=authentication.ssh_pswd
        )
        return ssh

    @classmethod
    def execute(cls, command: str, command_id: str, authentication: SSHConfig) -> RemoteResults:
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
        ssh = None
        res = RemoteResults(command=command, command_id=command_id)

        try:
            # Connect to remote server using SSH and Execute command
            ssh = RemoteCommand._ssh_setup(authentication)
            stdin, stdout, stderr = ssh.exec_command(command)
            time.sleep(1)

            # Wait for command to finish and capture its exit status
            exit_status = -1
            while exit_status == -1:
                if not stdout.channel.exit_status_ready():
                    time.sleep(20)  # Wait 20 sec before checking again
                else:
                    exit_status = stdout.channel.recv_exit_status()

            # Check for specific errors from the command
            res.stdout = stdout.read().decode().strip()
            res.stderr = stderr.read().decode().strip()
            res.exit_code = exit_status
            res.completion = True
            res.set_success()

        except paramiko.AuthenticationException:
            return RemoteCommand._set_error(res, "Failed to log in to remote server.")
        except paramiko.SSHException as e:
            return RemoteCommand._set_error(res, f"SSH error while waiting for command to finish: {str(e)}")
        except socket.timeout:
            return RemoteCommand._set_error(res, f"Socket timed out while waiting for command to finish.")
        except socket.error as e:
            return RemoteCommand._set_error(res, f"Socket error while waiting for command to finish: {str(e)}")

        finally:
            # Close SSH connection and return True to signify successful operation
            if ssh is not None:
                ssh.close()
        return res

    @classmethod
    def scp(cls, source: str, destination: str, authentication: SSHConfig, put: bool = True) -> RemoteResults:
        """
        Securely copies a file or directory from the source to the destination.

        This method uses the Secure Copy Protocol (SCP) to copy files or directories between the local host and a remote host
        or between two remote hosts.

        WARNING: currently the option to recursively scp all a files contents is disabled.

        Args:
        source (str): The path to the source file or directory.
        destination (str): The path to the destination file or directory.
        authentication (SSHConfig): The SSH configuration for connecting to the remote server.
        put (bool, optional): If True, the source is the local path and the destination is the remote path (uploading).
                              If False, the source is the remote path and the destination is the local path (downloading).
                              Default is True (uploading).

        Returns:
        RemoteResults: A RemoteResults object containing the details of the SCP operation, including whether the operation
                       was successful (success), the command that was executed (command), the identifier for the command
                       (command_id), and any output or error messages (stdout, stderr).
        """
        ssh = None
        command_id = "scp_put" if put else "scp_get"
        res = RemoteResults(command=f"scp {source} {destination}", command_id=command_id)
        try:
            # Connect to remote server using SSH and Perform SCP operation
            ssh = RemoteCommand._ssh_setup(authentication)
            with SCPClient(ssh.get_transport()) as scp:
                if put:
                    scp.put(source, destination, recursive=False)
                else:
                    scp.get(source, destination, recursive=False)
                res.exit_code = 0
                res.completion = True
                res.set_success()

        except paramiko.AuthenticationException:
            return RemoteCommand._set_error(res, "Failed to log in to remote server.")
        except paramiko.SSHException as e:
            return RemoteCommand._set_error(res, f"SSH connection error: {str(e)}")
        except Exception as e:
            return RemoteCommand._set_error(res, f"Error during SCP operation: {str(e)}")

        finally:
            # Close SSH connection and return True to signify successful operation
            if ssh is not None:
                ssh.close()
        return res
