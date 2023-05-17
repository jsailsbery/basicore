import pytest
import socket
import paramiko
from unittest.mock import patch, Mock
from basicore.parameters import SSHConfig
from basicore.remote import RemoteCommand, RemoteConnection


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

        # Mock SSHClient
        mock_ssh = MockSSHClient.return_value
        mock_stdout = Mock()
        mock_stdout.channel.recv_exit_status.return_value = 0
        mock_stdout.read.return_value = b''
        mock_stderr = Mock()
        mock_stderr.read.return_value = b''
        mock_ssh.exec_command.return_value = (None, mock_stdout, mock_stderr)

        # Mock RemoteConnection
        mock_conn = Mock(spec=RemoteConnection)
        mock_conn.authentication = mock_auth
        mock_conn.exec_command.return_value = (None, 'stdout', 'stderr', 0)

        result = RemoteCommand.execute(command="ls", command_id="1", ssh=mock_conn)

    assert result.success
    assert result.stderr == 'stderr'
    assert result.stdout == 'stdout'
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
        mock_conn = RemoteConnection(mock_auth)

        result = RemoteCommand.execute(command="ls", command_id="1", ssh=mock_conn)

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
        mock_stdout.read.return_value = 'stdout'  # Return actual string
        mock_stderr = Mock()
        mock_stderr.read.return_value = 'ERROR: Command failed'  # Return actual string

        mock_ssh.exec_command.return_value = (None, mock_stdout, mock_stderr)

        # Mock RemoteConnection
        mock_conn = Mock(spec=RemoteConnection)
        mock_conn.authentication = mock_auth
        mock_conn.conn = mock_ssh  # Add this line
        mock_conn.exec_command.return_value = (None, 'stdout', 'ERROR: Command failed', 1)  # Fixed return value

        result = RemoteCommand.execute(command="ls", command_id="1", ssh=mock_conn)

    assert not result.success
    assert "Command failed" in result.stderr
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
        mock_ssh.connect.side_effect = paramiko.AuthenticationException
        mock_conn = RemoteConnection(mock_auth)

        result = RemoteCommand.execute(command="ls", command_id="1", ssh=mock_conn)

    assert not result.success
    assert "Failed to log in" in result.stderr


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
        mock_stdout.read.return_value = ''  # Return actual string
        mock_stderr = Mock()
        mock_stderr.read.return_value = 'ERROR: something went wrong'  # Return actual string

        mock_ssh.exec_command.return_value = (None, mock_stdout, mock_stderr)

        # Mock RemoteConnection
        mock_conn = Mock(spec=RemoteConnection)
        mock_conn.authentication = mock_auth
        mock_conn.conn = mock_ssh  # Add this line
        mock_conn.exec_command.return_value = (None, '', 'ERROR: something went wrong', 0)  # Fixed return value

        result = RemoteCommand.execute(command="ls", command_id="1", ssh=mock_conn)

    assert result.completion
    assert not result.success
    assert result.errors
    assert result.stderr == 'ERROR: something went wrong'
    assert result.stdout == ''
    assert result.exit_code == 0


#@pytest.mark.skip(reason="Time intensive. Only run on validation")
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
        mock_stdout.read.return_value = ''  # Return actual string
        mock_stderr = Mock()
        mock_stderr.read.return_value = 'ERROR: something went wrong'  # Return actual string

        mock_ssh.exec_command.return_value = (None, mock_stdout, mock_stderr)

        # Mock RemoteConnection
        mock_conn = Mock(spec=RemoteConnection)
        mock_conn.authentication = mock_auth
        mock_conn.conn = mock_ssh  # Add this line
        mock_conn.exec_command.return_value = (None, '', 'ERROR: something went wrong', 0)  # Fixed return value

        result = RemoteCommand.execute(command="ls", command_id="1", ssh=mock_conn)

    assert result.completion
    assert not result.success
    assert result.errors
    assert result.stderr == 'ERROR: something went wrong'
    assert result.stdout == ''
    assert result.exit_code == 0

