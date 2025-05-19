class YaMusicRpcException(Exception):
    """
    Base exception class for exceptions raised by this library.
    """


class DiscordProcessNotFound(YaMusicRpcException):
    """
    Error raised when a Discord client is not found.
    """

    def __init__(self):
        super().__init__("Process Not Found")
