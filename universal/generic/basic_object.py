import logging

__all__ = ['Basic']
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Basic:
    """
    A Basic class to be inherited by other classes. This base class includes a method `_bool_fail`
    that logs an error message and returns False.

    Methods
    -------
    _bool_fail(msg: str) -> bool:
        Logs an error message and returns False.
    """
    def __init__(self, **kwargs):
        self.logger = logging.getLogger(self.__class__.__name__)

    def _bfail(self, info: str = "", error: str = "") -> bool:
        """
        Log an error message and return False.

        Parameters:
        info (str): optional. The info message to log.
        error (str): optional. The error message to log.

        Returns:
        bool: Always returns False.
        """
        if info:
            self.logger.info(info)
        if error:
            self.logger.error(error)
        return False

    def _bpass(self, info: str = "") -> bool:
        """
        Log an pass message and return True.

        Parameters:
        info (str): optional. The info message to log.

        Returns:
        bool: Always returns True.
        """
        if info:
            self.logger.error(info)
        return True

    @classmethod
    def bfail(cls, info: str = "", error: str = "") -> bool:
        """
        Logs an error message and returns False.

        Parameters:
        info (str): Optional. The informational message to log.
        error (str): Optional. The error message to log.

        Returns:
        bool: Always returns False, signifying a failure.
        """
        if info:
            logger.info(info)
        if error:
            logger.error(error)
        return False

    @classmethod
    def sfail(cls, info: str = "", error: str = "") -> str:
        """
        Logs an error message and returns an empty string.

        Parameters:
        info (str): Optional. The informational message to log.
        error (str): Optional. The error message to log.

        Returns:
        str: Always returns an empty string, signifying a failure.
        """
        if info:
            logger.info(info)
        if error:
            logger.error(error)
        return ""

    @classmethod
    def ifail(cls, info: str = "", error: str = "") -> int:
        """
        Logs an error message and returns -1.

        Parameters:
        info (str): Optional. The informational message to log.
        error (str): Optional. The error message to log.

        Returns:
        int: Always returns -1, signifying a failure.
        """
        if info:
            logger.info(info)
        if error:
            logger.error(error)
        return -1

    @classmethod
    def nfail(cls, info: str = "", error: str = ""):
        """
        Logs an error message and returns -1.

        Parameters:
        info (str): Optional. The informational message to log.
        error (str): Optional. The error message to log.

        Returns:
        int: Always returns None, signifying a failure.
        """
        if info:
            logger.info(info)
        if error:
            logger.error(error)
        return None

    @classmethod
    def bpass(cls, info: str = "") -> bool:
        """
        Logs a success message and returns True.

        Parameters:
        info (str): Optional. The success message to log.

        Returns:
        bool: Always returns True, signifying a success.
        """
        if info:
            logger.info(info)
        return True

    @classmethod
    def spass(cls, val: str, info: str = "") -> str:
        """
        Logs a success message and returns the provided string.

        Parameters:
        val (str): The string to be returned upon successful operation.
        info (str): Optional. The success message to log.

        Returns:
        str: Returns the provided string 'val', used to signify a successful operation and communicate a result.
        """
        if info:
            logger.info(info)
        return val

    @classmethod
    def ipass(cls, val: int, info: str = "") -> int:
        """
        Logs a success message and returns the provided integer.

        Parameters:
        val (int): The integer to be returned upon successful operation.
        info (str): Optional. The success message to log.

        Returns:
        int: Returns the provided integer 'val', used to signify a successful operation and communicate a result.
        """
        if info:
            logger.info(info)
        return val