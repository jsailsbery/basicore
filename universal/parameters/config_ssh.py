import os
import configparser
import logging
from .config_file import ConfigReader

__all__ = ['SSHConfig']
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


class SSHConfig:
    """
    A class representing SSH configuration.
    """

    def __init__(self, remote_server: str = None, ssh_user: str = None, ssh_pswd: str = None, ssh_port: str = None,
                 remote_dir: str = None, config_file: str = None):
        """
        Initializes a new instance of the SSHConfig class.

        Args:
            remote_server (str, optional): The remote server to access. Defaults to None.
            ssh_user (str, optional): The SSH username. Defaults to None.
            ssh_pswd (str, optional): The SSH password. Defaults to None.
            ssh_port (str): The SSH port.
            remote_dir (str, optional): The path to the SSH source_dir. Defaults to None.
            config_file (str, optional): The path to the configuration file. Defaults to None.
        """
        # Set default values from environment variables
        self.remote_server = remote_server or os.getenv('REMOTE_SERVER')
        self.ssh_user = ssh_user or os.getenv('SSH_USER')
        self.ssh_pswd = ssh_pswd or os.getenv('SSH_PSWD')
        self.ssh_port = ssh_port or os.getenv('SSH_PORT')
        self.remote_dir = remote_dir or os.getenv('SSH_DIR')

        # Override defaults with values from config file, if provided
        if config_file:
            self.load_config(config_file)

    def __repr__(self):
        """
        Returns a string representation of the SSHConfig instance.

        Returns:
            str: A string representation of the SSHConfig instance.
        """
        retstr = "SSHConfig("
        retstr += f"remote_server={self.remote_server}," if hasattr(self, 'remote_server') else ""
        retstr += f"ssh_user={self.ssh_user}," if hasattr(self, 'ssh_user') else ""
        retstr += f"ssh_pswd=<private>," if hasattr(self, 'ssh_pswd') else ""
        retstr += f"ssh_port={self.ssh_port}," if hasattr(self, 'ssh_port') else ""
        retstr += f"remote_dir={self.remote_dir}" if hasattr(self, 'remote_dir') else ""
        retstr += ")"
        return retstr

    def load_config(self, config_file: str) -> None:
        """
        Loads the source_dir mapping information from a configuration file.

        Args:
            config_file (str): The path to the configuration file.

        Raises:
            Exception: If the configuration file cannot be loaded or is missing required fields.
        """
        try:
            config = ConfigReader(config_file=config_file)
            self.remote_server = config.get('SSH', 'remote_server', "")
            self.ssh_user = config.get('SSH', 'ssh_user', "")
            self.ssh_pswd = config.get('SSH', 'ssh_pswd', "")
            self.ssh_port = config.get('SSH', 'ssh_port', "")
            self.remote_dir = config.get('SSH', 'remote_dir', "")
            logging.info('SSH configuration loaded from config file.')
        except (configparser.Error, IOError) as e:
            logging.error(f'Error loading configuration file {config_file}: {e}')
            raise Exception(f'Error loading configuration file {config_file}: {e}') from e
