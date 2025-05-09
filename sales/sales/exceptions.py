from typing import Dict


class SaleCantBeCreated(Exception):
    """Exception raised when a sale cannot be created."""

    def __init__(self, response: Dict):
        self.response = response

    def errors(self) -> Dict:
        return self.response
