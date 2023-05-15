import os
import tempfile
import pytest
from universal.files import ConfigReader


def test_load_config():
    """
    Test that the load_config method correctly reads a configuration file
    and stores it in a dictionary. Also checks if it correctly replaces the values
    with environment variables if they exist.
    """
    # create a temporary config file
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp:
        temp.write("[SECTION1]\nkey1 = value1\n")
        temp_path = temp.name

    # set environment variable
    os.environ["SECTION1_KEY1"] = "env_value"

    # test load_config
    config_reader = ConfigReader(temp_path)
    assert config_reader.config_dict == {"SECTION1": {"key1": "env_value"}}

    # clean up
    os.remove(temp_path)
    del os.environ["SECTION1_KEY1"]


def test_repr():
    """
    Test that the __repr__ method correctly returns a string that represents
    the configuration dictionary in INI format.
    """
    # create a temporary config file
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp:
        temp.write("[SECTION1]\nkey1 = value\n")
        temp_path = temp.name

    # test __repr__
    config_reader = ConfigReader(temp_path)
    assert str(config_reader) == "[SECTION1]\nkey1 = value\n"

    # clean up
    os.remove(temp_path)


def test_dictionary_access():
    """
    Test that the ConfigReader behaves like a dictionary.
    """
    # create a temporary config file
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp:
        temp.write("[SECTION1]\nkey1 = value\n")
        temp_path = temp.name

    # test dictionary behavior
    config_reader = ConfigReader(temp_path)
    assert config_reader["SECTION1"]["key1"] == "value"
    config_reader["SECTION1"]["key1"] = "new_value"
    assert config_reader["SECTION1"]["key1"] == "new_value"
    del config_reader["SECTION1"]["key1"]
    assert "key1" not in config_reader["SECTION1"]

    # clean up
    os.remove(temp_path)


def test_get():
    """
    Test that the get method correctly returns the value for a given key, or
    a default value if the key is not in the configuration dictionary.
    Also checks if it correctly converts string values to the appropriate data types.
    """
    # create a temporary config file
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp:
        temp.write("[SECTION1]\n"
                   "key = value\n"
                   "integer_key = 42\n"
                   "boolean_key_true = true\n"
                   "boolean_key_false = false\n"
                   "json_key_dict = {\"subkey\": \"subvalue\"}\n"
                   "json_key_list = [\"item1\", \"item2\"]\n")
        temp_path = temp.name

    # test get
    config_reader = ConfigReader(temp_path)
    assert config_reader.get("SECTION1", "key") == "value"
    assert config_reader.get("SECTION1", "integer_key") == 42
    assert config_reader.get("SECTION1", "boolean_key_true") is True
    assert config_reader.get("SECTION1", "boolean_key_false") is False
    assert config_reader.get("SECTION1", "json_key_dict") == {"subkey": "subvalue"}
    assert config_reader.get("SECTION1", "json_key_list") == ["item1", "item2"]
    assert config_reader.get("SECTION1", "non_existent_key", "default") == "default"

    # clean up
    os.remove(temp_path)
