import logging
logging.basicConfig(level=logging.INFO)


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

    def _bool_fail(self, msg: str = "") -> bool:
        """
        Log an error message and return False.

        Parameters:
        msg (str): optional. The error message to log.

        Returns:
        bool: Always returns False.
        """
        if msg:
            self.logger.error(msg)
        return False

    def _bool_pass(self, msg: str = "") -> bool:
        """
        Log an pass message and return True.

        Parameters:
        msg (str): optional. The message to log.

        Returns:
        bool: Always returns True.
        """
        if msg:
            self.logger.error(msg)
        return True