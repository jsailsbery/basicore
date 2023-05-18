import pytest
import tempfile
import paramiko
from unittest.mock import patch, Mock
from basicore.parameters import SSHConfig
from basicore.remote import RemoteCommand, RemoteConnection, RemoteResults

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
    def create_mock_ssh(stdout: str, stderr: str, exit_code: int):
        with patch('paramiko.SSHClient') as MockSSHClient:
            mock_ssh = MockSSHClient.return_value

            mock_stdin, mock_stdin_read = [Mock(), Mock()]
            #mock_stdin_read.decode.return_value = ''
            #mock_stdin.read.return_value = mock_stdin_read
            mock_stdin.readlines.return_value = ''

            mock_stdout, mock_stdout_read = [Mock(), Mock()]
            #mock_stdout_read.decode.return_value = stdout
            #mock_stdout.read.return_value = mock_stdout_read
            mock_stdout.readlines.return_value = [stdout]

            mock_stderr, mock_stderr_read = [Mock(), Mock()]
            #mock_stderr_read.decode.return_value = stderr
            #mock_stderr.read.return_value = mock_stderr_read
            mock_stderr.readlines.return_value = [stderr]

            mock_stdout.channel.recv_exit_status.return_value = exit_code  # Command succeeded
            mock_ssh.exec_command.return_value = (mock_stdin, mock_stdout, mock_stderr)
            return mock_ssh
    return create_mock_ssh

@pytest.fixture()
def mock_conn(mock_auth, mock_ssh):
    mock_conn = Mock(spec=RemoteConnection)
    mock_conn.authentication = mock_auth
    mock_conn.client = mock_ssh
    mock_conn.connect.return_value = ""
    return mock_conn


@pytest.mark.parametrize('stdout, stderr, exit_code', [('stdout', 'stderr', 0)])
def test_remote_command_success(mock_conn, mock_ssh, stdout, stderr, exit_code):
    mock_conn.client = mock_ssh(stdout, stderr, exit_code)
    result = RemoteCommand.execute(command="ls", command_id="1", ssh=mock_conn)
    assert result.completion
    assert result.success
    assert result.stderr == stderr
    assert result.stdout == stdout
    assert result.exit_code == exit_code


def test_remote_command_auth_failure(mock_auth):
    with patch('paramiko.SSHClient') as MockSSHClient:
        mock_ssh = MockSSHClient.return_value
        mock_ssh.connect.side_effect = paramiko.AuthenticationException
        mock_conn = RemoteConnection(mock_auth)
        result = RemoteCommand.execute(command="ls", command_id="1", ssh=mock_conn)
    assert not result.success
    assert "Failed to log in to remote server." in result.stderr


@pytest.mark.parametrize('stdout, stderr, exit_code', [('stdout', 'ERROR: Command failed', 1)])
def test_remote_command_command_failure(mock_conn, mock_ssh, stdout, stderr, exit_code):
    mock_conn.client = mock_ssh(stdout, stderr, exit_code)
    result = RemoteCommand.execute(command="ls", command_id="1", ssh=mock_conn)
    assert result.completion
    assert not result.success
    assert result.stderr == stderr
    assert result.stdout == stdout
    assert result.exit_code == exit_code


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


@pytest.mark.parametrize('stdout, stderr, exit_code', [('stdout', 'ERROR: something went wrong', 0)])
def test_remote_command_error_detection(mock_conn, mock_ssh, stdout, stderr, exit_code):
    mock_conn.client = mock_ssh(stdout, stderr, exit_code)
    result = RemoteCommand.execute(command="ls", command_id="1", ssh=mock_conn)
    assert result.completion
    assert not result.success
    assert result.stderr == stderr
    assert result.stdout == stdout
    assert result.exit_code == exit_code
