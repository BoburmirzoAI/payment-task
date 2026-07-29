class CustomException(Exception):
    """
    Custom exception for raising every single kind of exception in the project.
    Use message_key from MESSAGES dict.
    """
    def __init__(self, message_key: str, context: dict = None):
        self.message_key = message_key
        self.context = context or {}
