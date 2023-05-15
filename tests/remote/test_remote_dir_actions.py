import os
import tempfile
from unittest.mock import patch, PropertyMock
from universal.remote import RemoteDirActions
from universal.parameters import SSHConfig

def test_exists():
    """Test RemoteDirActions.exists method"""
    temp_dir = tempfile.mkdtemp()
    with patch('universal.remote.RemoteCommand.execute') as mock_execute:
        mock_execute.return_value = True
        with patch('universal.remote.RemoteCommand.exit_code', new_callable=PropertyMock) as mock_exit_code:
            mock_exit_code.return_value = 0
            assert RemoteDirActions.exists(temp_dir, SSHConfig()) is True
            mock_exit_code.return_value = 1
            assert RemoteDirActions.exists(temp_dir, SSHConfig()) is False
    os.rmdir(temp_dir)

def test_create():
    """Test RemoteDirActions.create method"""
    temp_dir = tempfile.mkdtemp()
    os.rmdir(temp_dir)
    with patch('universal.remote.RemoteCommand.execute') as mock_execute:
        mock_execute.return_value = True
        with patch('universal.remote.RemoteCommand.success', new_callable=PropertyMock) as mock_success:
            mock_success.return_value = True
            with patch('universal.remote.RemoteDirActions.exists', return_value=False) as mock_exists:
                result = RemoteDirActions.create(temp_dir, SSHConfig())
                assert result == True

def test_delete():
    """Test RemoteDirActions.remove_contents method"""
    temp_dir = tempfile.mkdtemp()
    with patch('universal.remote.RemoteCommand.execute', return_value=True):
        assert RemoteDirActions.remove(temp_dir, SSHConfig()) == True
    os.rmdir(temp_dir)

def test_list():
    """Test RemoteDirActions.list_contents method"""
    temp_dir = tempfile.mkdtemp()

    with patch('universal.remote.RemoteCommand.execute') as mock_execute, \
        patch('universal.remote.RemoteCommand.stdout', new_callable=PropertyMock) as mock_stdout, \
        patch('universal.remote.RemoteFileActions.follow_symlink') as mock_check_and_get_size:

        mock_execute.return_value = True
        # Simulate the output of 'ls -l' that includes only a symbolic link
        mock_stdout.return_value = 'lrwxrwxrwx 1 user group    9 May 12 10:30 link -> target'
        # Simulate the size of the symbolic link target
        mock_check_and_get_size.return_value = 1024

        expected_result = {
            'target': 1024,
        }

        assert RemoteDirActions.list(temp_dir, SSHConfig()) == expected_result

    os.rmdir(temp_dir)

def test_copy():
    """Test RemoteDirActions.copy method"""
    source_dir = tempfile.mkdtemp()
    destination_dir = tempfile.mkdtemp()
    with patch('universal.remote.RemoteCommand.execute', return_value=True):
        assert RemoteDirActions.copy(source_dir, destination_dir, SSHConfig()) == True
    os.rmdir(source_dir)
    os.rmdir(destination_dir)

def test_remove():
    """Test RemoteDirActions.remove_directory method"""
    temp_dir = tempfile.mkdtemp()
    with patch('universal.remote.RemoteCommand.execute') as mock_execute:
        mock_execute.return_value = True
        assert RemoteDirActions.delete(temp_dir, SSHConfig()) == True
        mock_execute.return_value = False
        assert RemoteDirActions.delete(temp_dir, SSHConfig()) == False
    os.rmdir(temp_dir)