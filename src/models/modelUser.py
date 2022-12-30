from typing import Optional
from pydantic import BaseModel

# Classe
class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None 