import pytest
import socket
import paramiko
from unittest.mock import patch, Mock
from basicore.parameters import SSHConfig
from basicore.remote import RemoteCommand


def test_remote_command_success():
    """
    Test the scenario where a command is successfully executed on the remote server.
    """
    # Mock SSHConfig
    mock_auth = Mock(spec=SSHConfig)
    mock_auth.remote_server = "localhost"
    mock_auth.ssh_port = 22
    mock_auth.ssh_user = "user"
    mock_auth.ssh_pswd = "password"

    # Mock paramiko.SSHClient
    with patch('paramiko.SSHClient') as MockSSHClient:
        mock_ssh = MockSSHClient.return_value

        mock_stdout = Mock()
        mock_stdout.channel.recv_exit_status.return_value = 0
        mock_stdout.read.return_value = b''
        mock_stderr = Mock()
        mock_stderr.read.return_value = b''

        mock_ssh.exec_command.return_value = (None, mock_stdout, mock_stderr)

        result = RemoteCommand.execute(command="ls", command_id="1", authentication=mock_auth)

    assert result.success
    assert result.stderr == ''
    assert result.stdout == ''
    assert result.exit_code == 0


def test_remote_command_auth_failure():
    """
    Test the scenario where authentication to the remote server fails.
    """
    # Mock SSHConfig
    mock_auth = Mock(spec=SSHConfig)
    mock_auth.remote_server = "localhost"
    mock_auth.ssh_port = 22
    mock_auth.ssh_user = "user"
    mock_auth.ssh_pswd = "password"

    # Mock paramiko.SSHClient to raise an AuthenticationException
    with patch('paramiko.SSHClient') as MockSSHClient:
        mock_ssh = MockSSHClient.return_value
        mock_ssh.connect.side_effect = paramiko.AuthenticationException

        result = RemoteCommand.execute(command="ls", command_id="1", authentication=mock_auth)

    assert not result.success
    assert "Failed to log in to remote server." in result.stderr


def test_remote_command_command_failure():
    """
    Test the scenario where command execution fails on the remote server.
    """
    # Mock SSHConfig
    mock_auth = Mock(spec=SSHConfig)
    mock_auth.remote_server = "localhost"
    mock_auth.ssh_port = 22
    mock_auth.ssh_user = "user"
    mock_auth.ssh_pswd = "password"

    # Mock paramiko.SSHClient
    with patch('paramiko.SSHClient') as MockSSHClient:
        mock_ssh = MockSSHClient.return_value

        mock_stdout = Mock()
        mock_stdout.channel.recv_exit_status.return_value = 1  # Command failed
        mock_stdout.read.return_value = b''
        mock_stderr = Mock()
        mock_stderr.read.return_value = b'Command failed'

        mock_ssh.exec_command.return_value = (None, mock_stdout, mock_stderr)

        result = RemoteCommand.execute(command="ls", command_id="1", authentication=mock_auth)

    assert not result.success
    assert result.stderr == 'Command failed'
    assert result.exit_code == 1


def test_remote_command_ssh_error():
    """
    Test the scenario where the SSH connection drops while waiting for the command to finish.
    """
    # Mock SSHConfig
    mock_auth = Mock(spec=SSHConfig)
    mock_auth.remote_server = "localhost"
    mock_auth.ssh_port = 22
    mock_auth.ssh_user = "user"
    mock_auth.ssh_pswd = "password"

    # Mock paramiko.SSHClient to raise an SSHException
    with patch('paramiko.SSHClient') as MockSSHClient:
        mock_ssh = MockSSHClient.return_value
        mock_ssh.connect.side_effect = paramiko.SSHException

        result = RemoteCommand.execute(command="ls", command_id="1", authentication=mock_auth)

    assert not result.success
    assert "SSH error while waiting for command to finish:" in result.stderr


def test_remote_command_error_detection():
    """
    Test the scenario where command execution fails and the error is detected in stdout or stderr.
    """
    # Mock SSHConfig
    mock_auth = Mock(spec=SSHConfig)
    mock_auth.remote_server = "localhost"
    mock_auth.ssh_port = 22
    mock_auth.ssh_user = "user"
    mock_auth.ssh_pswd = "password"

    # Mock paramiko.SSHClient
    with patch('paramiko.SSHClient') as MockSSHClient:
        mock_ssh = MockSSHClient.return_value

        mock_stdout = Mock()
        mock_stdout.channel.recv_exit_status.return_value = 0  # Command succeeded
        mock_stdout.read.return_value = b'ERROR: something went wrong'
        mock_stderr = Mock()
        mock_stderr.read.return_value = b''

        mock_ssh.exec_command.return_value = (None, mock_stdout, mock_stderr)

        result = RemoteCommand.execute(command="ls", command_id="1", authentication=mock_auth)

    assert not result.success
    assert result.errors
    assert result.stderr == ''
    assert result.stdout == 'ERROR: something went wrong'
    assert result.exit_code == 0


#@pytest.mark.skip(reason="Time intensive. Only run on validation")
def test_remote_command_socket_timeout():
    """
    Test the scenario where a socket timeout occurs while waiting for the command to finish.
    """
    # Mock SSHConfig
    mock_auth = Mock(spec=SSHConfig)
    mock_auth.remote_server = "localhost"
    mock_auth.ssh_port = 22
    mock_auth.ssh_user = "user"
    mock_auth.ssh_pswd = "password"

    # Mock paramiko.SSHClient to simulate a timeout
    with patch('paramiko.SSHClient') as MockSSHClient:
        mock_ssh = MockSSHClient.return_value

        mock_stdout = Mock()
        mock_stdout.channel.exit_status_ready.side_effect = socket.timeout
        mock_stderr = Mock()
        mock_stderr.read.return_value = b''

        mock_ssh.exec_command.return_value = (None, mock_stdout, mock_stderr)

        result = RemoteCommand.execute(command="ls", command_id="1", authentication=mock_auth)

    assert not result.success
    assert "Socket timed out while waiting for command to finish." in result.stderr
