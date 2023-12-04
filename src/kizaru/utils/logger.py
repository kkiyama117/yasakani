from pathlib import Path

from loguru import logger
from notifiers.logging import NotificationHandler

from kizaru.secret import Secrets
from kizaru.utils import send_email


def setup_logger(debug: bool = False):
    # LOGGING SETTINGS
    log_dir = Path.cwd() / 'logs'
    error_log_file = log_dir / 'error.log'
    if debug:
        log_file = log_dir / "debug.log"
        file_log_level = "DEBUG"
    else:
        log_file = log_dir / "main.log"
        file_log_level = "WARNING"
    logger.add(log_file, level=file_log_level, retention="1 days")
    # test debugging
    logger.debug(f"Logger created: {log_file}")

    # error log
    logger.add(error_log_file, level="WARNING", backtrace=True, diagnose=True)
    logger.debug(f"Logger created: {error_log_file}")
    # Be alerted on each error message
    # https://notifiers.readthedocs.io/en/latest/providers/email.html
    notifiers_param = Secrets().MAIL_NOTIFIERS_PARAM
    handler = NotificationHandler("gmail", defaults=notifiers_param)
    logger.add(handler, level="WARNING")
