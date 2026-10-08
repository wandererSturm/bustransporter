import logging

import pytest

from bustransporter import log


@pytest.fixture(autouse=True)
def clean_logging():
    """Remove handlers added by a test so they do not leak into the next one."""
    yield
    logger = logging.getLogger(log.ROOT)
    for handler in logger.handlers:
        handler.close()
    logger.handlers.clear()
