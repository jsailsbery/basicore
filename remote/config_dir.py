import os
import configparser
import logging
from universal import ConfigReader


class DirConfig:
    """
    A class representing directory configuration.

    Attributes:
        data_directory (str): The path to the data directory.
        temp_directory (str): The path to the temporary directory.
    """

    def __init__(self, data_directory: str=None, temp_directory: str=None, config_file: str=None):
        """
        Initializes a new instance of the Dirconfig class.

        Args:
            config_file (str, optional): The path to the configuration file. Defaults to None.
        """
        # Set default values from environment variables
        self.data_directory = data_directory or os.getenv('DATA_DIRECTORY')
        self.temp_directory = temp_directory or os.getenv('TEMP_DIRECTORY')

        # Override defaults with values from config file, if provided
        if config_file:
            self.load_config(config_file)

    def __repr__(self):
        """
        Returns a string representation of the Dirconfig instance.

        Returns:
            str: A string representation of the Dirconfig instance.
        """
        retstr = "Dirconfig("
        retstr += f"data_directory={self.data_directory}" if hasattr(self, 'data_directory') else ""
        retstr += f"temp_directory={self.temp_directory}" if hasattr(self, 'temp_directory') else ""
        retstr += ")"
        return retstr

    def load_config(self, config_file: str) -> None:
        """
        Loads the directory mapping information from a configuration file.

        Args:
            config_file (str): The path to the configuration file.

        Raises:
            Exception: If the configuration file cannot be loaded or is missing required fields.
        """
        try:
            config = ConfigReader(config_file=config_file)
            self.data_directory = config.get('Directories', 'data_directory', "")
            self.temp_directory = config.get('Directories', 'temp_directory', "")
            logging.info('Directory configuration loaded from config file.')
        except (configparser.Error, IOError) as e:
            logging.error(f'Error loading configuration file {config_file}: {e}')
            raise Exception(f'Error loading configuration file {config_file}: {e}') from e
