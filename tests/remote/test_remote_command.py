import pytest
import socket
import paramiko
from unittest.mock import patch, Mock
from basicore.parameters import SSHConfig
from basicore.remote import RemoteCommand, RemoteConnection

@pytest.fixture
def mock_auth():
    mock_auth = Mock(spec=SSHConfig)
    mock_auth.remote_server = "localhost"
    mock_auth.ssh_port = 22
    mock_auth.ssh_user = "user"
    mock_auth.ssh_pswd = "password"
    return mock_auth


@pytest.fixture
def mock_ssh():
    with patch('paramiko.SSHClient') as MockSSHClient:
        mock_ssh = MockSSHClient.return_value
        mock_stdout = Mock()
        mock_stdout.channel.recv_exit_status.return_value = 0  # Command succeeded
        mock_stdout.read.return_value = 'stdout'
        mock_stderr = Mock()
        mock_stderr.read.return_value = 'stderr'
        mock_ssh.exec_command.return_value = (None, mock_stdout, mock_stderr)


@pytest.fixture()
def mock_conn(mock_auth, mock_ssh):
    def create_mock_conn(stderr: str, exitcode: int):
        mock_conn = Mock(spec=RemoteConnection)
        mock_conn.authentication = mock_auth
        mock_conn.conn = mock_ssh
        mock_conn.exec_command.return_value = (None, 'stdout', stderr, exitcode)
        return mock_conn
    return create_mock_conn


def test_remote_command_success(mock_conn):
    """
    Test the scenario where a command is successfully executed on the remote server.
    """
    result = RemoteCommand.execute(command="ls", command_id="1", ssh=mock_conn('stderr', 0))

    assert result.success
    assert result.stderr == 'stderr'
    assert result.stdout == 'stdout'
    assert result.exit_code == 0


def test_remote_command_auth_failure(mock_auth):
    """
    Test the scenario where authentication to the remote server fails.
    """

    # Mock paramiko.SSHClient to raise an AuthenticationException
    with patch('paramiko.SSHClient') as MockSSHClient:
        mock_ssh = MockSSHClient.return_value
        mock_ssh.connect.side_effect = paramiko.AuthenticationException
        mock_conn = RemoteConnection(mock_auth)

        result = RemoteCommand.execute(command="ls", command_id="1", ssh=mock_conn)

    assert not result.success
    assert "Failed to log in to remote server." in result.stderr


def test_remote_command_command_failure(mock_conn):
    """
    Test the scenario where command execution fails on the remote server.
    """
    result = RemoteCommand.execute(command="ls", command_id="1", ssh=mock_conn('ERROR: Command failed', 1))

    assert not result.success
    assert "Command failed" in result.stderr
    assert result.exit_code == 1


def test_remote_command_ssh_error(mock_auth):
    """
    Test the scenario where the SSH connection drops while waiting for the command to finish.
    """

    # Mock paramiko.SSHClient to raise an SSHException
    with patch('paramiko.SSHClient') as MockSSHClient:
        mock_ssh = MockSSHClient.return_value
        mock_ssh.connect.side_effect = paramiko.AuthenticationException
        mock_conn = RemoteConnection(mock_auth)

        result = RemoteCommand.execute(command="ls", command_id="1", ssh=mock_conn)

    assert not result.success
    assert "Failed to log in" in result.stderr


def test_remote_command_error_detection(mock_conn):
    """
    Test the scenario where command execution fails and the error is detected in stdout or stderr.
    """
    result = RemoteCommand.execute(command="ls", command_id="1", ssh=mock_conn('ERROR: something went wrong', 0))

    assert result.completion
    assert not result.success
    assert result.errors
    assert result.stderr == 'ERROR: something went wrong'
    assert result.stdout == ''
    assert result.exit_code == 0


#@pytest.mark.skip(reason="Time intensive. Only run on validation")
def test_remote_command_error_detection(mock_conn):
    """
    Test the scenario where command execution fails and the error is detected in stdout or stderr.
    """
    result = RemoteCommand.execute(command="ls", command_id="1", ssh=mock_conn('ERROR: something went wrong', 0))

    assert result.completion
    assert not result.success
    assert result.errors
    assert result.stderr == 'ERROR: something went wrong'
    assert result.stdout == 'stdout'
    assert result.exit_code == 0

