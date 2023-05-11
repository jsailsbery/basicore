import os
import pytest
import tempfile
from unittest.mock import patch, Mock
from remote import RemoteDirectory, SSHConfig

def test_exists():
    """Test RemoteDirectory.exists method"""
    temp_dir = tempfile.mkdtemp()
    with patch('remote_command.RemoteCommand.execute') as mock_execute:
        mock_execute.return_value = True
        with patch('remote_command.RemoteCommand.exit_code', new_callable=Mock) as mock_exit_code:
            mock_exit_code.__get__ = Mock(return_value=0)
            assert RemoteDirectory.exists(temp_dir, SSHConfig()) == True
            mock_exit_code.__get__ = Mock(return_value=1)
            assert RemoteDirectory.exists(temp_dir, SSHConfig()) == False
    os.rmdir(temp_dir)

def test_create():
    """Test RemoteDirectory.create method"""
    temp_dir = tempfile.mkdtemp()
    os.rmdir(temp_dir)
    with patch('remote_command.RemoteCommand.execute') as mock_execute:
        mock_execute.return_value = True
        with patch('remote_directory.RemoteDirectory.exists') as mock_exists:
            mock_exists.return_value = False
            assert RemoteDirectory.create(temp_dir, SSHConfig()) == True
            mock_exists.return_value = True
            assert RemoteDirectory.create(temp_dir, SSHConfig()) == False

def test_copy():
    """Test RemoteDirectory.copy method"""
    source_dir = tempfile.mkdtemp()
    destination_dir = tempfile.mkdtemp()
    os.rmdir(destination_dir)
    with patch('remote_command.RemoteCommand.execute', return_value=True):
        assert RemoteDirectory.copy(source_dir, destination_dir, SSHConfig()) == True
    os.rmdir(source_dir)
    os.rmdir(destination_dir)

def test_remove_contents():
    """Test RemoteDirectory.remove_contents method"""
    temp_dir = tempfile.mkdtemp()
    with patch('remote_command.RemoteCommand.execute', return_value=True):
        assert RemoteDirectory.remove_contents(temp_dir, SSHConfig()) == True
    os.rmdir(temp_dir)

def test_list_contents():
    """Test RemoteDirectory.list_contents method"""
    temp_dir = tempfile.mkdtemp()
    with patch('remote_command.RemoteCommand.execute') as mock_execute:
        mock_execute.return_value = True
        with patch('remote_command.RemoteCommand.stdout', new_callable=Mock) as mock_stdout:
            mock_stdout.__get__ = Mock(return_value='file1\nfile2')
            assert RemoteDirectory.list_contents(temp_dir, SSHConfig()) == ['file1', 'file2']
    os.rmdir(temp_dir)
