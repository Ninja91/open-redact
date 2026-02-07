from abc import ABC, abstractmethod
from typing import Dict, Any
from src.models.database import User

class BaseBroker(ABC):
    def __init__(self, name: str, domain: str):
        self.name = name
        self.domain = domain

    @abstractmethod
    async def submit_opt_out(self, user: User) -> Dict[str, Any]:
        """
        Logic to submit an opt-out request.
        Should return a dict with 'status' and 'external_id' or 'error'.
        """
        pass

    @abstractmethod
    async def check_status(self, external_id: str) -> str:
        """
        Check the status of a previously submitted request.
        """
        pass
