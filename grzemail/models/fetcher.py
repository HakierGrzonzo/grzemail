from aioimaplib.aioimaplib import IMAP4_SSL

class ClientWrapper:
    def __init__(self, connection: IMAP4_SSL) -> None:
        self._connection = connection
    
