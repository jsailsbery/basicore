import os
import time
from tempfile import TemporaryDirectory
from unittest.mock import patch
from universal.files import INode

# PyTest test cases
def test_inode_creation():
    # Create a temporary directory for testing
    with TemporaryDirectory() as temp_dir:
        # Create a temporary file inside the directory
        temp_file_path = os.path.join(temp_dir, 'test_file.txt')
        with open(temp_file_path, 'w') as temp_file:
            temp_file.write('Test file contents')

        # Create an INode object with the temporary file path
        node = INode(temp_file_path)

        # Check the attributes of the INode object
        assert node.path == temp_file_path
        assert node.name == 'test_file.txt'
        assert node.parent == temp_dir
        assert node.exists
        assert not node.is_dir
        assert not node.is_symlink
        assert node.mod_time == time.ctime(os.path.getmtime(temp_file_path))
        assert node.create_time == time.ctime(os.path.getctime(temp_file_path))
        assert node.access_time == time.ctime(os.path.getatime(temp_file_path))
        assert node.r_ok
        assert node.w_ok
        assert not node.x_ok
        assert node.symlink_target is ""


def test_inode_creation_symlink():
    # Create a temporary directory for testing
    with TemporaryDirectory() as temp_dir:
        # Create a temporary file inside the directory
        temp_file_path = os.path.join(temp_dir, 'test_file.txt')
        with open(temp_file_path, 'w') as temp_file:
            temp_file.write('Test file contents')

        # Create a symlink to the temporary file
        symlink_path = os.path.join(temp_dir, 'test_symlink')
        os.symlink(temp_file_path, symlink_path)

        # Create an INode object with the symlink path
        node = INode(symlink_path)

        # Check the attributes of the INode object
        assert node.path == symlink_path
        assert node.name == 'test_symlink'
        assert node.parent == temp_dir
        assert node.exists
        assert not node.is_dir
        assert node.is_symlink
        assert node.symlink_target == temp_file_path
        assert node.mod_time == time.ctime(os.path.getmtime(temp_file_path))
        assert node.create_time == time.ctime(os.path.getctime(temp_file_path))
        assert node.access_time == time.ctime(os.path.getatime(temp_file_path))
        assert node.r_ok
        assert node.w_ok
        assert not node.x_ok


@patch('os.access', return_value=False)
def test_inode_creation_permissions(mock_access):
    # Create a temporary file path
    temp_file_path = '/path/to/file.txt'

    # Create an INode object with the temporary file path
    node = INode(temp_file_path)

    # Check the attributes of the INode object
    assert node.path == temp_file_path
    assert node.name == 'file.txt'
    assert node.parent == '/path/to'
    assert not node.exists
    assert not node.is_dir
    assert not node.is_symlink
    assert not node.r_ok
    assert not node.w_ok
    assert not node.x_ok
    assert node.mod_time is None
    assert node.create_time is None
    assert node.access_time is None
