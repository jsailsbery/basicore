import pytest
import os
import configparser
from unittest.mock import MagicMock
from remote import DirConfig


def test_default_values():
    """
    Test if DirConfig instance is initialized with default values from environment variables.
    """
    dc = DirConfig()
    assert dc.data_directory == os.getenv('DATA_DIRECTORY')
    assert dc.temp_directory == os.getenv('TEMP_DIRECTORY')


def test_config_file_values(tmp_path):
    """
    Test if DirConfig instance loads directory mapping information from a configuration file and overrides default values.
    """
    config = configparser.ConfigParser()
    config['Directories'] = {'data_directory': str(tmp_path / 'data'), 'temp_directory': str(tmp_path / 'temp')}
    with open(tmp_path / 'config.ini', 'w') as f:
        config.write(f)

    dc = DirConfig(config_file=str(tmp_path / 'config.ini'))
    assert dc.data_directory == str(tmp_path / 'data')
    assert dc.temp_directory == str(tmp_path / 'temp')


def test_load_config_error(tmp_path, caplog):
    """
    Test if DirConfig instance raises an exception when the configuration file is missing required fields or cannot be loaded.
    """
    with open(tmp_path / 'config.ini', 'w') as f:
        f.write('[Directories]\n')

    with pytest.raises(Exception) as exc_info:
        dc = DirConfig(config_file=str(tmp_path / 'config.ini'))
    assert 'Error loading configuration file' in str(exc_info.value)
    assert 'No option \'data_directory\' in section: \'Directories\'' in caplog.text


def test_repr():
    """
    Test if the string representation of DirConfig instance is correct.
    """
    dc = DirConfig(data_directory='/data', temp_directory='/tmp')
    assert repr(dc) == "Dirconfig(data_directory=/data,temp_directory=/tmp)"


def test_load_config(tmp_path, caplog):
    """
    Test if DirConfig instance loads directory mapping information from a configuration file and overrides the default values.
    """
    config = configparser.ConfigParser()
    config['Directories'] = {'data_directory': str(tmp_path / 'data'), 'temp_directory': str(tmp_path / 'temp')}
    with open(tmp_path / 'config.ini', 'w') as f:
        config.write(f)

    dc = DirConfig(data_directory='/default_data', temp_directory='/default_temp')
    dc.load_config(config_file=str(tmp_path / 'config.ini'))
    assert dc.data_directory == str(tmp_path / 'data')
    assert dc.temp_directory == str(tmp_path / 'temp')
    assert 'Directory configuration loaded from config file.' in caplog.text
