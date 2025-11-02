from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field


class Message(BaseModel):
    content: str = Field(default_factory=str, description="The content of the message")
    role: Optional[Literal['user', 'assistant']] = Field(default="user", description="The content of the message")
    translation: Optional[str] = Field(default=None, description="The translation of the message to english")

    model_config = ConfigDict(extra='allow')
