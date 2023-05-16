import os
import tempfile
import pytest
from basicore.parameters import SSHConfig


@pytest.fixture
def config_file():
    """
    Fixture that creates a temporary config file and returns its path.

    Returns:
        str: The path to the temporary config file.
    """
    # Create a temporary config file
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp:
        temp.write("[SSH]\nremote_server=localhost\nssh_user=testuser\nssh_pswd=testpass\nssh_port=22\n"
                   "remote_dir=/home/testuser\n")
        return temp.name


def test_init_with_defaults():
    """
    Test initializing with default values from environment variables.
    """
    # Test initializing with default values from environment variables
    os.environ['REMOTE_SERVER'] = 'example.com'
    os.environ['SSH_USER'] = 'user'
    os.environ['SSH_PSWD'] = 'pass'
    os.environ['SSH_PORT'] = '22'
    os.environ['SSH_DIR'] = '/home/user'
    config = SSHConfig()
    assert config.remote_server == 'example.com'
    assert config.ssh_user == 'user'
    assert config.ssh_pswd == 'pass'
    assert config.ssh_port == '22'
    assert config.remote_dir == '/home/user'


def test_init_with_arguments():
    """
    Test initializing with values passed as arguments.
    """
    # Test initializing with values passed as arguments
    config = SSHConfig(remote_server='example.com', ssh_user='user', ssh_pswd='pass', ssh_port='22', remote_dir='/home/user')
    assert config.remote_server == 'example.com'
    assert config.ssh_user == 'user'
    assert config.ssh_pswd == 'pass'
    assert config.ssh_port == '22'
    assert config.remote_dir == '/home/user'



def test_init_with_config_file(config_file):
    """
    Test initializing with values from a config file.
    """
    # Test initializing with values from a config file
    config = SSHConfig(config_file=config_file)
    assert config.remote_server == 'localhost'
    assert config.ssh_user == 'testuser'
    assert config.ssh_pswd == 'testpass'
    assert config.ssh_port == 22
    assert config.remote_dir == '/home/testuser'


def test_load_config_file_not_found():
    """
    Test loading a config file that can't be found.
    """
    # Test loading a config file that can't be found
    with pytest.raises(Exception, match=r'No such file or directory'):
        SSHConfig(config_file='/does/not/exist')


def test_repr():
    """
    Test string representation of object.
    """
    # Test string representation of object
    config = SSHConfig(remote_server='example.com', ssh_user='user', ssh_pswd='pass', ssh_port='22',
                       remote_dir='/home/user')
    assert repr(config) == \
           "SSHConfig(remote_server=example.com,ssh_user=user,ssh_pswd=<private>,ssh_port=22,remote_dir=/home/user)"