class YaMusicRpcException(Exception):
    """
    Base exception class for exceptions raised by this library.
    """


class DiscordProcessNotFoundError(YaMusicRpcException):
    """
    Error raised when a Discord client is not found.
    """

    def __init__(self):
        super().__init__("Process Not Found")

class AdminRightsRequiredError(YaMusicRpcException):
    """
    Error raised when a Discord client has not enough rights to use Discord RPC.
    """
    def __init__(self):
        super().__init__("Admin Rights Required")