import os
import pytest
import socket
import paramiko
from unittest.mock import patch, Mock
from universal.remote import RemoteCommand, SSHConfig


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

    # RemoteCommand instance
    cmd = RemoteCommand(command="ls", command_id="1")

    # Mock paramiko.SSHClient
    with patch('paramiko.SSHClient') as MockSSHClient:
        mock_ssh = MockSSHClient.return_value

        mock_stdout = Mock()
        mock_stdout.channel.recv_exit_status.return_value = 0
        mock_stdout.read.return_value = b''
        mock_stderr = Mock()
        mock_stderr.read.return_value = b''

        mock_ssh.exec_command.return_value = (None, mock_stdout, mock_stderr)

        cmd.execute(mock_auth)

    assert cmd.success
    assert cmd.stderr == ''
    assert cmd.stdout == ''
    assert cmd.exit_code == 0


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

    # RemoteCommand instance
    cmd = RemoteCommand(command="ls", command_id="1")

    # Mock paramiko.SSHClient to raise an AuthenticationException
    with patch('paramiko.SSHClient') as MockSSHClient:
        mock_ssh = MockSSHClient.return_value
        mock_ssh.connect.side_effect = paramiko.AuthenticationException

        cmd.execute(mock_auth)

    assert not cmd.success
    assert "Failed to log in to remote server." in cmd.stderr


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

    # RemoteCommand instance
    cmd = RemoteCommand(command="ls", command_id="1")

    # Mock paramiko.SSHClient
    with patch('paramiko.SSHClient') as MockSSHClient:
        mock_ssh = MockSSHClient.return_value

        mock_stdout = Mock()
        mock_stdout.channel.recv_exit_status.return_value = 1  # Command failed
        mock_stdout.read.return_value = b''
        mock_stderr = Mock()
        mock_stderr.read.return_value = b'Command failed'

        mock_ssh.exec_command.return_value = (None, mock_stdout, mock_stderr)

        cmd.execute(mock_auth)

    assert not cmd.success
    assert cmd.stderr == 'Command exited with error status.'
    assert cmd.exit_code == 1


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

    # RemoteCommand instance
    cmd = RemoteCommand(command="ls", command_id="1")

    # Mock paramiko.SSHClient to raise an SSHException
    with patch('paramiko.SSHClient') as MockSSHClient:
        mock_ssh = MockSSHClient.return_value
        mock_ssh.connect.side_effect = paramiko.SSHException

        cmd.execute(mock_auth)

    assert not cmd.success
    assert "SSH connection error:" in cmd.stderr

@pytest.mark.skip(reason="Time intensive. Only run on validation")
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

    # RemoteCommand instance
    cmd = RemoteCommand(command="ls", command_id="1")

    # Mock paramiko.SSHClient to simulate a timeout
    with patch('paramiko.SSHClient') as MockSSHClient:
        mock_ssh = MockSSHClient.return_value

        mock_stdout = Mock()
        mock_stdout.channel.exit_status_ready.return_value = False
        mock_stdout.channel.recv_exit_status.side_effect = socket.timeout
        mock_stderr = Mock()
        mock_stderr.read.return_value = b''

        mock_ssh.exec_command.return_value = (None, mock_stdout, mock_stderr)

        cmd.execute(mock_auth)

    assert not cmd.success
    assert "Socket timed out while waiting for command to finish." in cmd.stderr
