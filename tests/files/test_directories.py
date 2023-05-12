import os
import shutil
import tempfile
import pytest
from universal.files import DirActions

def test_purge_directory():
    """Test removing all directories and files except for the specified directories."""

    # Create a temporary directory for testing
    temp_dir = tempfile.mkdtemp()

    # Create some directories and files
    os.makedirs(os.path.join(temp_dir, 'analysis'))
    os.makedirs(os.path.join(temp_dir, 'metadata'))
    os.makedirs(os.path.join(temp_dir, 'logs'))
    open(os.path.join(temp_dir, 'data.txt'), 'w').close()

    # Call the function to remove directories except 'analysis' and 'metadata'
    assert DirActions.remove_contents(temp_dir, ['analysis', 'metadata']) == True

    # Check that 'analysis' and 'metadata' directories still exist
    assert os.path.isdir(os.path.join(temp_dir, 'analysis')) == True
    assert os.path.isdir(os.path.join(temp_dir, 'metadata')) == True

    # Check that 'logs' and 'data.txt' files were removed
    assert os.path.exists(os.path.join(temp_dir, 'logs')) == False
    assert os.path.exists(os.path.join(temp_dir, 'data.txt')) == False

    # Remove the temporary directory
    shutil.rmtree(temp_dir)
