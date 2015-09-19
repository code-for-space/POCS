import sys
import logging

from .config import load_config

log_levels = {
    'critical': logging.CRITICAL,
    'error': logging.ERROR,
    'warning': logging.WARNING,
    'info': logging.INFO,
    'debug': logging.DEBUG,
}

has_logger = Logger()


def has_logger(Class, level='warning'):
    """Class decorator to add logging

    Args:
        level (str): log level to set for the class wrapper, defaults to 'warning'
    """
    has_logger.debug("Adding {} logging to: {}".format(level, Class.__name__))
    setattr(Class, 'logger', Logger(log_level=level, profile=Class.__name__))
    return Class


class Logger(logging.Logger):
    """ Consistent logging class for application

        The has_logger class decorator allows this to be
        applited to classes within a project for consistent functionality
    """

    def __init__(self, log_level='warning', profile=None):
        super().__init__(name=profile)

        # Get log info from config
        self.config = load_config()
        log_config = self.config.get('log', {})

        self.log_dir = log_config.setdefault('log_dir', '/var/panoptes/logs')
        self.log_file = log_config.setdefault('log_file', 'panoptes.log')
        self.log_level = log_config.setdefault('log_level', 'info')
        self.log_format = log_config.setdefault(
            'log_format', '%(asctime)23s %(name)15s %(levelname)8s: %(message)s')
        self.log_profile = profile if profile is not None else log_config.setdefault(
            'log_profile', 'PanoptesLogger')

        self.logger = logging.getLogger(self.log_profile)
        self.log_format = logging.Formatter(self.log_format)
        self.logger.setLevel(log_levels[self.log_level])

        fh = "{}/{}".format(self.log_dir, self.log_file)

        # Set up file output
        self.log_fh = logging.FileHandler(fh)
        # Always write the full debug information out to the file
        self.log_fh.setLevel(log_levels['debug'])
        self.log_fh.setFormatter(self.log_format)

        self.logger.addHandler(self.log_fh)

    def set_log_level(self, level='info'):
        """ Change to the new log level

        Note:
            This only changes the output logger level and does
            not affect the output to the log file, which is always
            set to 'debug'.

        Args:
            level(str):     Level to change to for log output. Must be
                one of keys from `log_levels`. Defaults to 'info'.
        """
        self.logger.setLevel(log_levels.get(level, 'info'))

    def debug(self, msg):
        """ Send a debug message

        Passes the message along to the logging class

        Args:
            msg(str): Message to be sent
        """

        self.logger.debug(msg)

    def info(self, msg):
        """ Send an info message

        Passes the message along to the logging class

        Args:
            msg(str): Message to be sent
        """

        self.logger.info(msg)

    def error(self, msg):
        """ Send an error message

        Passes the message along to the logging class. Includes caller.

        Args:
            msg(str): Message to be sent
        """

        self.logger.warning(self.logger.findCaller())
        self.logger.error(msg)

    def warning(self, msg):
        """ Send an warning message

        Passes the message along to the logging class.

        Args:
            msg(str): Message to be sent
        """

        # self.logger.warning(self.logger.findCaller())
        self.logger.warning(msg)

    def critical(self, msg):
        """ Send an critical message

        Passes the message along to the logging class. Includes caller.

        Args:
            msg(str): Message to be sent
        """

        self.logger.warning(self.logger.findCaller())
        self.logger.critical(msg)

    def exception(self, msg):
        """ Send an exception message

        Passes the message along to the logging class. Includes caller.

        Args:
            msg(str): Message to be sent
        """

        self.logger.warning(self.logger.findCaller())
        self.logger.exception(msg)
