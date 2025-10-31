
from typing import List, Literal, Optional, Union

from pydantic import BaseModel, Field

class Message(BaseModel):
    content: str = Field(default_factory=str, description="The content of the message")
    role: Optional[Literal['user', 'assitant']] = Field(default="user", description="The content of the message")

class FrontDeskFlowState(BaseModel):
    message: Message = Field(
        default_factory=Message,
        description="The latest message exchanged at the front desk"
    )

    history: List[
        Union[Message, dict[Literal["translation"], str]]
    ] = Field(
        default_factory=list,
        description="The history of messages exchanged at the front desk"
    )

    def add_message(self, content: str, role: Optional[Literal['user', 'assitant']] = None):
        if role is None or role not in ['user', 'assitant']:
          raise ValueError("Role must be either 'user' or 'assitant'")

        message = Message(content=content, role=role)
        self.history.append(message)
        return message
