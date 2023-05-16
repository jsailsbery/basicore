import os
import pytest
import tempfile
from unittest.mock import patch, Mock, PropertyMock, MagicMock
from basicore.parameters import SSHConfig
from basicore.remote import RemoteCommand, RemoteExecuteException, RemoteFileActions


def test_exists():
    """Test RemoteFileActions.exists method"""
    with tempfile.NamedTemporaryFile() as temp_file:
        with patch('universal.remote.RemoteCommand.execute') as mock_execute:
            mock_execute.return_value = PropertyMock(success=True, completion=True, errors=False)
            assert RemoteFileActions.exists(temp_file.name, SSHConfig()) is True
            mock_execute.return_value = PropertyMock(success=False, completion=True, errors=False)
            assert RemoteFileActions.exists(temp_file.name, SSHConfig()) is False
            mock_execute.return_value = PropertyMock(completion=False)
            with pytest.raises(RemoteExecuteException):
                RemoteFileActions.exists(temp_file.name, SSHConfig())


def test_isfile():
    """Test RemoteFileActions.isfile method"""
    with tempfile.NamedTemporaryFile() as temp_file:
        with patch('universal.remote.RemoteCommand.execute') as mock_execute:
            mock_execute.return_value = PropertyMock(success=True, completion=True, errors=False)
            assert RemoteFileActions.isfile(temp_file.name, SSHConfig()) is True
            mock_execute.return_value = PropertyMock(success=False, completion=True, errors=False)
            assert RemoteFileActions.isfile(temp_file.name, SSHConfig()) is False
            mock_execute.return_value = PropertyMock(completion=False)
            with pytest.raises(RemoteExecuteException):
                RemoteFileActions.isfile(temp_file.name, SSHConfig())


def test_remove():
    """Test RemoteFileActions.remove method"""
    with tempfile.NamedTemporaryFile() as temp_file:
        with patch('universal.remote.RemoteCommand.execute') as mock_execute:
            mock_execute.return_value = PropertyMock(success=True, completion=True, errors=False)
            assert RemoteFileActions.remove(temp_file.name, SSHConfig()) is True
            mock_execute.return_value = PropertyMock(completion=False)
            with pytest.raises(RemoteExecuteException):
                RemoteFileActions.remove(temp_file.name, SSHConfig())


def test_read():
    """Test RemoteFileActions.read method"""
    with tempfile.NamedTemporaryFile() as temp_file:
        with patch('universal.remote.RemoteCommand.execute') as mock_execute:
            mock_execute.return_value = PropertyMock(success=True, completion=True, errors=False, stdout='{"key": "value"}')
            assert RemoteFileActions.read(temp_file.name, SSHConfig()) == {"key": "value"}
            mock_execute.return_value = PropertyMock(completion=False)
            with pytest.raises(RemoteExecuteException):
                RemoteFileActions.read(temp_file.name, SSHConfig())


def test_write():
    """Test RemoteFileActions.write method"""
    file_content = "This is a test content"
    with patch('universal.remote.RemoteCommand.scp') as mock_scp:
        mock_scp.return_value = PropertyMock(completion=True, success=True)
        with patch('tempfile.NamedTemporaryFile') as mock_tmp, patch('os.remove') as mock_remove:
            mock_file = MagicMock()
            mock_file.name = '/tmp/tmpfile'
            mock_tmp.return_value.__enter__.return_value = mock_file
            assert RemoteFileActions.write(mock_file.name, file_content, SSHConfig()) is True
            mock_file.write.assert_called_once_with(file_content)
            mock_remove.assert_called_once_with(mock_file.name)


def test_follow():
    """Test RemoteFileActions.follow method"""
    with tempfile.NamedTemporaryFile() as temp_file:
        name1, name2 = [temp_file.name, temp_file.name+"0"]
        os.symlink(name1, name2)
        with patch('universal.remote.RemoteCommand.execute') as mock_execute:
            mock_execute.return_value = PropertyMock(success=True, completion=True, errors=False, stdout=name1)
            assert RemoteFileActions.follow(name2, SSHConfig()) == name1
        os.remove(name2)
