import os
import pytest
import tempfile
from unittest.mock import patch, PropertyMock
from basicore.remote import RemoteDirActions, RemoteExecuteException
from basicore.parameters import SSHConfig

def test_exists():
    """Test RemoteDirActions.exists method"""
    temp_dir = tempfile.mkdtemp()
    with patch('basicore.remote.RemoteCommand.execute') as mock_execute:
        mock_execute.return_value = PropertyMock(success=True, completion=True, errors=False, stdout="0")
        assert RemoteDirActions.exists(temp_dir, SSHConfig()) is True
        mock_execute.return_value = PropertyMock(success=True, completion=True, errors=False, stdout="1")
        assert RemoteDirActions.exists(temp_dir, SSHConfig()) is False
        mock_execute.return_value = PropertyMock(success=False, completion=False)
        with pytest.raises(RemoteExecuteException):
            RemoteDirActions.exists(temp_dir, SSHConfig())
    os.rmdir(temp_dir)


def test_create():
    """Test RemoteDirActions.create method"""
    temp_dir = tempfile.mkdtemp()
    os.rmdir(temp_dir)
    with patch('basicore.remote.RemoteDirActions.isdir', return_value=False) as mock_isdir:
        with patch('basicore.remote.RemoteCommand.execute') as mock_execute:
            mock_execute.return_value = PropertyMock(success=True, completion=True, errors=False)
            result = RemoteDirActions.create(temp_dir, SSHConfig())
            assert result == True

            mock_execute.return_value = PropertyMock(success=False, completion=True, errors=False)
            with pytest.raises(RemoteExecuteException):
                RemoteDirActions.create(temp_dir, SSHConfig())

            mock_execute.return_value = PropertyMock(success=False, completion=False)
            with pytest.raises(RemoteExecuteException):
                RemoteDirActions.create(temp_dir, SSHConfig())


def test_delete():
    """Test RemoteDirActions.delete method"""
    temp_dir = tempfile.mkdtemp()
    with patch('basicore.remote.RemoteDirActions.exists', return_value=True) as mock_exists:
        with patch('basicore.remote.RemoteCommand.execute') as mock_execute:
            mock_execute.return_value = PropertyMock(success=True, completion=True, errors=False)
            assert RemoteDirActions.delete(temp_dir, SSHConfig()) == True
            mock_execute.return_value = PropertyMock(success=False, completion=True, errors=False)
            assert RemoteDirActions.delete(temp_dir, SSHConfig()) == False
            mock_execute.return_value = PropertyMock(success=False, completion=False)
            with pytest.raises(RemoteExecuteException):
                RemoteDirActions.delete(temp_dir, SSHConfig())
    os.rmdir(temp_dir)


def test_list():
    """Test RemoteDirActions.list method"""
    temp_dir = tempfile.mkdtemp()
    with patch('basicore.remote.RemoteCommand.execute') as mock_execute:
        with patch('basicore.remote.RemoteDirActions.exists', return_value=True):
            with patch('basicore.remote.RemoteFileActions.follow', return_value=1024):
                mock_execute.return_value = PropertyMock(success=True, completion=True, stdout='lrwxrwxrwx 1 user group 9 May 12 10:30 link -> target')
                assert RemoteDirActions.list(temp_dir, SSHConfig()) == {'target': 1024}

        mock_execute.return_value = PropertyMock(success=False, completion=True, errors=False)
        with patch('basicore.remote.RemoteDirActions.exists', return_value=True):
            assert RemoteDirActions.list(temp_dir, SSHConfig()) == None

        mock_execute.return_value = PropertyMock(success=False, completion=False)
        with pytest.raises(RemoteExecuteException):
            RemoteDirActions.list(temp_dir, SSHConfig())

    os.rmdir(temp_dir)


def test_copy():
    """Test RemoteDirActions.copy method"""
    source_dir = tempfile.mkdtemp()
    destination_dir = tempfile.mkdtemp()
    with patch('basicore.remote.RemoteDirActions.exists', return_value=True) as mock_exists:
        with patch('basicore.remote.RemoteDirActions.create', return_value=True) as mock_create:
            with patch('basicore.remote.RemoteCommand.execute') as mock_execute:
                mock_execute.return_value = PropertyMock(success=True, completion=True, errors=False)
                assert RemoteDirActions.copy(source_dir, destination_dir, SSHConfig()) == True

                mock_execute.return_value = PropertyMock(success=False, completion=True, errors=False)
                assert RemoteDirActions.copy(source_dir, destination_dir, SSHConfig()) == False

                mock_execute.return_value = PropertyMock(success=False, completion=False)
                with pytest.raises(RemoteExecuteException):
                    RemoteDirActions.copy(source_dir, destination_dir, SSHConfig())
    os.rmdir(source_dir)
    os.rmdir(destination_dir)


def test_remove():
    """Test RemoteDirActions.remove method"""
    temp_dir = tempfile.mkdtemp()
    with patch('basicore.remote.RemoteDirActions.exists', return_value=True) as mock_exists:
        with patch('basicore.remote.RemoteCommand.execute') as mock_execute:
            mock_execute.return_value = PropertyMock(success=True, completion=True, errors=False)
            assert RemoteDirActions.remove(temp_dir, SSHConfig()) == True
            mock_execute.return_value = PropertyMock(success=False, completion=True, errors=False)
            assert RemoteDirActions.remove(temp_dir, SSHConfig()) == False
            mock_execute.return_value = PropertyMock(success=False, completion=False)
            with pytest.raises(RemoteExecuteException):
                RemoteDirActions.remove(temp_dir, SSHConfig())
    os.rmdir(temp_dir)
