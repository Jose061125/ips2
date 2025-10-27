from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Employee:
    """Entidad Employee del dominio"""
    id: Optional[int]
    name: str
    document: str
    position: str
    created_at: datetime = datetime.now()