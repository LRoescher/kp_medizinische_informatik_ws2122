from enum import Enum


class FlashMessageTypes(Enum):
    """ mapping to _flash_messages.sass classes"""
    MESSAGE = "message"
    SUCCESS = "success"
    WARNING = "warning"
    FAILURE = "failure"
