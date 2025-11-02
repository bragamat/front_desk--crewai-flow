
from typing import List, Literal, Optional

from pydantic import BaseModel, Field,ConfigDict

class Message(BaseModel):
    content: str = Field(default_factory=str, description="The content of the message")
    role: Optional[Literal['user', 'assistant']] = Field(default="user", description="The content of the message")
    translation: Optional[str] = Field(default=None, description="The translation of the message to english")

    
    model_config = ConfigDict(extra='allow')

class FrontDeskFlowState(BaseModel):
    message: Message = Field(
        default_factory=Message,
        description="The latest message exchanged at the front desk"
    )

    history: List[Message] = Field(
        default_factory=list,
        description="The history of messages exchanged at the front desk"
    )

    def add_user_message(self,
                    content: str,
                    translation: Optional[str] = None,
                    ):

        message = Message(content=content, translation=translation, role="user")

        self.history.append(message)
        return message

    def add_assistant_message(self,
                    content: str,
                    translation: Optional[str] = None,
                    ):
        message = Message(content=content, translation=translation, role="assistant")

        self.history.append(message)
        return message
