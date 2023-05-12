import os
import json
import configparser
import logging


class ConfigReader:
    """
    A class used to read a configuration file and check for any already
    defined environment variables.

    ...

    Attributes
    ----------
    filepath : str
        a formatted string to define the file path of the configuration file
    config_dict : dict
        a dictionary to store the configuration data

    Methods
    -------
    load_config():
        Reads the configuration file and store it in a dictionary.
    """

    def __init__(self, config_file: str):
        """
        Constructs all the necessary attributes for the ConfigReader object.

        Parameters
        ----------
            config_file : str
                file path of the configuration file
        """

        self.filepath = config_file
        self.config_dict = self.load_config()

    def load_config(self):
        """
        Reads the configuration file and store it in a dictionary.
        If any environment variable exists for a key, it replaces the value in the file.

        Returns
        -------
        dict
            a dictionary that contains the configuration data
        """
        # Open the file and print its contents
        lines = ""
        with open(self.filepath, 'r') as f:
            lines = f.read()


        config = configparser.ConfigParser()
        config_dict = {}
        try:
            config.read(self.filepath)

            for section in config.sections():
                config_dict[section] = {}
                for key, value in config.items(section):
                    env_value = os.getenv(f"{section}_{key}".upper())
                    if env_value is not None:
                        config_dict[section][key] = env_value
                    else:
                        config_dict[section][key] = value

        except configparser.Error as e:
            logging.error(f'Error reading configuration file: {e}')

        return config_dict

    def __getitem__(self, key):
        return self.config_dict[key]

    def __setitem__(self, key, value):
        self.config_dict[key] = value

    def __delitem__(self, key):
        del self.config_dict[key]

    def __contains__(self, key):
        return key in self.config_dict

    def get(self, section, key, default=None):
        sect_dict = self.config_dict.get(section, {})
        value = sect_dict.get(key, default)

        # Check if the value is a string
        if isinstance(value, str):
            # Perform the appropriate type casting based on the expected data type
            if value.isdigit():
                # If the string contains only digits, cast it to an integer
                value = int(value)
            elif value.lower() == 'true':
                # If the string is 'true' (case-insensitive), cast it to a boolean True
                value = True
            elif value.lower() == 'false':
                # If the string is 'false' (case-insensitive), cast it to a boolean False
                value = False
            else:
                # Check if the string is a valid JSON-formatted dictionary or list
                try:
                    value = json.loads(value)
                except json.JSONDecodeError:
                    # If the string is not valid JSON, leave it as is
                    pass

        return value

    def __repr__(self):
        """
        Returns a string that represents the configuration dictionary in INI format.

        Returns
        -------
        str
            a string that represents the configuration dictionary in INI format
        """

        config = configparser.ConfigParser()
        config.read_dict(self.config_dict)
        output = []
        for section in config.sections():
            output.append(f'[{section}]')
            for key, val in config.items(section):
                output.append(f'{key} = {val}')
            output.append('')
        return '\n'.join(output)
